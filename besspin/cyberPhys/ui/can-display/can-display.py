#!/usr/bin/env python3
"""
Simple CAN listener. Listens to CAN CMD messages,
update the display when status changes.

Exchange format:
{
    func: "name-of-the-function-to-be-called",
    args: {"dictionary of arguments}
    resp: {"dictionary of return vaues}
    status: response status
        200 -OK
        500 - unexpected failure
        501 - func not implemented
}
"""
import signal
import logging
import zmq
import struct
from enum import Enum
import threading

from can import Message

import cyberphyslib.canlib as canlib
from cyberphyslib.demonstrator import config

DEFAULT_NETWORK_CONFIG_PATH = "/home/pi/BESSPIN-Tool-Suite/besspin/base/utils/setupEnv.json"

# make CAN module less noisy
logging.getLogger("can").setLevel(logging.WARNING)

STATE_NORMAL = "normal"
STATE_HACKED = "hacked"
STATE_SSITH = "ssith"

class CanDisplay(threading.Thread):
    ZMQ_POLL_TIMEOUT = 0.1

    # Keep a dictionary of components, and keep tabs on which ones are showing errors
    component_status = canlib.CanlibComponentNames.copy()

    def __init__(self):
        # Threading
        super().__init__(name="CanDisplay", daemon=False)
        self.stop_evt = threading.Event()

        # CMD network init
        net_conf = config.DemonstratorNetworkConfig.from_setup_env(DEFAULT_NETWORK_CONFIG_PATH)
        cmd_host, cmd_subscribers = net_conf.getCmdNetworkNodes("CanDisplay")
        self.cmd_bus = canlib.TcpBus(cmd_host, cmd_subscribers)

        # ZMQ init
        self.zmq_port = net_conf.port_network_ipcPort
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.zmq_port}")

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        self.scenario = canlib.SCENARIO_BASELINE
        self.state = STATE_NORMAL
        self.error_msg = ""
        self.func_level = canlib.FUNCTIONALITY_NONE

        # initialize components dictionary - no errors by default
        for key in self.component_status:
            self.component_status[key] = canlib.ERROR_NONE

        print(f"<{self.__class__.__name__}> Listening on CAN_PORT {net_conf.port_network_commandPort}, and ZMQ_PORT {self.zmq_port}")

        self.cmd_thread = threading.Thread(target=self.cmdLoop, args=[], daemon=True)

    def update_component_status(self, component_id=None, error_id=None):
        """
        Update the component dictionary and update the error message,
        including the functionality level
        """
        err_msg = ""
        if component_id and error_id:
            self.component_status[component_id] = error_id
        for cid in self.component_status:
            err = self.component_status[cid]
            if  err != canlib.ERROR_NONE:
                err_msg += f"\n{canlib.CanlibComponentNames.get(cid,None)}: {canlib.CanlibComponentNames.get(err,None)}"
        if self.func_level != canlib.FUNCTIONALITY_FULL:
            err_msg += f"\nFUNCTIONALITY: {canlib.CanlibComponentNames.get(self.func_level)}"
        self.error_msg = err_msg
        print(f"{self.error_msg}")

    def run(self):
        self.cmd_thread.start()
        while not self.stopped:
            msgs = dict(self.poller.poll(timeout=CanDisplay.ZMQ_POLL_TIMEOUT))
            if self.socket in msgs and msgs[self.socket] == zmq.POLLIN:
                # recv there
                self.serve()

    def stop(self):
        self.stop_evt.set()

    @property
    def stopped(self):
        return self.stop_evt.is_set()

    def exit(self):
        self.stop()

    def serve(self):
        req = self.socket.recv_json()
        assert("func" in req and "args" in req)
        if req['func'] == "scenario":
            req['retval'] = self.state
            req['status'] = 200 # OK
        elif req['func'] == "error":
            req['retval'] = self.error_msg
            req['status'] = 200 # OK
        else:
            req['status'] = 501 # Not implemented
        self.socket.send_json(req)

    def cmdLoop(self):
        while True:
            msg = self.cmd_bus.recv()
            if msg:
                self.processCmdMsg(msg)

    def processCmdMsg(self, msg):
        """
        process CMD message
        """
        cid = msg.arbitration_id
        try:
            if cid == canlib.CAN_ID_CMD_ACTIVE_SCENARIO:
                scenario_id = struct.unpack(canlib.CAN_FORMAT_CMD_ACTIVE_SCENARIO, msg.data)[0]
                print(f"<{self.__class__.__name__}> CAN_ID_CMD_ACTIVE_SCENARIO: {canlib.CanlibComponentNames.get(scenario_id,None)}")
                if scenario_id == canlib.SCENARIO_BASELINE or\
                   scenario_id == canlib.SCENARIO_SECURE_ECU or\
                   scenario_id == canlib.SCENARIO_SECURE_INFOTAINMENT:
                   self.scenario = scenario_id
                else:
                    print(f"<{self.__class__.__name__}> Unknown scenario ID: {hex(scenario_id)}")
                if self.scenario == canlib.SCENARIO_BASELINE:
                    self.state = STATE_NORMAL
                else:
                    self.state = STATE_SSITH
                print(f"Scenario: {self.scenario}, State: {self.state}")
            elif cid == canlib.CAN_ID_CMD_HACK_ACTIVE:
                hack_id = struct.unpack(canlib.CAN_FORMAT_CMD_HACK_ACTIVE, msg.data)[0]
                print(f"<{self.__class__.__name__}> CAN_ID_CMD_HACK_ACTIVE: {canlib.CanlibComponentNames.get(hack_id,None)}")
                if self.scenario == canlib.SCENARIO_BASELINE:
                    if hack_id == canlib.HACK_NONE or hack_id == canlib.HACK_INFOTAINMENT_MUSIC or hack_id == canlib.HACK_INFOTAINMENT_VOLUME:
                        self.state = STATE_NORMAL
                    else:
                        self.state = STATE_HACKED
                    print(f"Scenario: {self.scenario}, State: {self.state}")
            elif cid == canlib.CAN_ID_HEARTBEAT_REQ:
                req_number = struct.unpack(canlib.CAN_FORMAT_HEARTBEAT_REQ, msg.data)[0]
                heartbeat_ack = Message(arbitration_id=canlib.CAN_ID_HEARTBEAT_ACK,
                                        dlc=canlib.CAN_DLC_HEARTBEAT_ACK,
                                        data=struct.pack(canlib.CAN_FORMAT_HEARTBEAT_ACK, canlib.CAN_DISPLAY_BACKEND, req_number))
                self.cmd_bus.send(heartbeat_ack)
            elif cid == canlib.CAN_ID_CMD_COMPONENT_ERROR:
                component_id, error_id = struct.unpack(canlib.CAN_FORMAT_CMD_COMPONENT_ERROR, msg.data)
                self.update_component_status(component_id, error_id)
            elif cid == canlib.CAN_ID_CMD_FUNCTIONALITY_LEVEL:
                self.func_level = struct.unpack(canlib.CAN_FORMAT_CMD_FUNCTIONALITY_LEVEL, msg.data)[0]
                self.update_component_status()
            else:
                pass
        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    listener.exit()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    listener = CanDisplay()
    listener.start()
