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
from enum import Enum
import threading

import cyberphyslib.canlib as ccan

# make CAN module less noisy
logging.getLogger("can").setLevel(logging.WARNING)

STATE_NORMAL = "normal"
STATE_HACKED = "hacked"
STATE_SSITH = "ssith"

class CanDisplay(threading.Thread):
    CMD_PORT = 5041
    ZMQ_PORT = 5091
    ZMQ_POLL_TIMEOUT = 0.1

    def __init__(self):
        # Threading
        super().__init__(name="CanDisplay", daemon=False)
        self.stop_evt = threading.Event()

        # CMD network init
        self.cmd_port = CanDisplay.CMD_PORT
        self.host = f"10.88.88.5:{self.cmd_port}" # Can display
        self.nodes = [f"10.88.88.1:{self.cmd_port}",
                      f"10.88.88.2:{self.cmd_port}",
                      f"10.88.88.3:{self.cmd_port}",
                      f"10.88.88.4:{self.cmd_port}"]
        self.canbus = ccan.TcpBus(self.host, self.nodes)

        # ZMQ init
        self.zmq_port = CanDisplay.ZMQ_PORT
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.zmq_port}")

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        self.scenario = ccan.SCENARIO_BASELINE
        self.state = STATE_NORMAL

        print(f"<{self.__class__.__name__}> Listening on CAN_PORT {self.cmd_port}, and ZMQ_PORT {self.zmq_port}")

        self.cmd_thread = threading.Thread(target=self.cmdLoop, args=[], daemon=True)

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
        print(f"<{self.__class__.__name__}> Got request {req}")
        assert("func" in req and "args" in req)
        if req['func'] == "scenario":
            req['retval'] = self.state
            req['status'] = 200 # OK
        else:
            req['status'] = 501 # Not implemented
        print(f"<{self.__class__.__name__}> Responding with {req}")
        self.socket.send_json(req)

    def cmdLoop(self):
        while True:
            msg = self.canbus.recv()
            if msg:
                self.processCmdMsg(msg)

    def processCmdMsg(self, msg):
        """
        process CMD message
        """
        cid, data = msg.arbitration_id, msg.data
        data = int.from_bytes(data, byteorder='big', signed=False)

        try:
            if cid == ccan.CAN_ID_CMD_ACTIVE_SCENARIO:
                print(f"<{self.__class__.__name__}> CAN_ID_CMD_ACTIVE_SCENARIO: {hex(data)}")
                if data == ccan.SCENARIO_BASELINE or\
                   data == ccan.SCENARIO_SECURE_ECU or\
                   data == ccan.SCENARIO_SECURE_INFOTAINMENT:
                   self.scenario = data
                else:
                    print(f"<{self.__class__.__name__}> Unknown scenario ID: {hex(data)}")
                if self.scenario == ccan.SCENARIO_BASELINE:
                    self.state = STATE_NORMAL
                else:
                    self.state = STATE_SSITH
            elif cid == ccan.CAN_ID_CMD_HACK_ACTIVE:
                print(f"<{self.__class__.__name__}> CAN_ID_CMD_HACK_ACTIVE: {hex(data)}")
                if self.scenario == ccan.SCENARIO_BASELINE:
                    if data == ccan.HACK_NONE:
                        self.state = STATE_NORMAL
                    else:
                        self.state = STATE_HACKED
            print(f"State: {self.scenario}")
        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    listener.exit()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    listener = CanDisplay()
    listener.start()
