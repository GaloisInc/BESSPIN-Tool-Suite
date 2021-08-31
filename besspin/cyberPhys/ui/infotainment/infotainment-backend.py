#!/usr/bin/env python3
"""
Infotainment UI backend. Listends for Reset button presses,
and sends CMD restart request messages

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
import threading

from can import Message

import cyberphyslib.canlib as canlib
from cyberphyslib.demonstrator import config

DEFAULT_NETWORK_CONFIG_PATH = "/home/pi/BESSPIN-Tool-Suite/besspin/base/utils/setupEnv.json"

# make CAN module less noisy
logging.getLogger("can").setLevel(logging.WARNING)


class InfotainmentBackend(threading.Thread):
    ZMQ_POLL_TIMEOUT = 0.1

    def __init__(self):
        # Threading
        super().__init__(name="InfotainmentBackend", daemon=False)
        self.stop_evt = threading.Event()

        # CMD network init
        net_conf = config.DemonstratorNetworkConfig.from_setup_env(DEFAULT_NETWORK_CONFIG_PATH)
        cmd_host, cmd_subscribers = net_conf.getCmdNetworkNodes("InfotainmentThinClient")
        self.cmd_bus = canlib.TcpBus(cmd_host, cmd_subscribers)

        # ZMQ init
        self.zmq_port = net_conf.port_network_ipcPort
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.zmq_port}")

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        print(f"<{self.__class__.__name__}> Listening on CAN_PORT {net_conf.port_network_commandPort}, and ZMQ_PORT {self.zmq_port}")

        self.cmd_thread = threading.Thread(target=self.cmdLoop, args=[], daemon=True)

    def run(self):
        self.cmd_thread.start()
        while not self.stopped:
            msgs = dict(self.poller.poll(timeout=InfotainmentBackend.ZMQ_POLL_TIMEOUT))
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
        assert("func" in req)
        if req['func'] == "reset":
            req['retval'] = {}
            req['status'] = 200 # OK
            print(f"<{self.__class__.__name__}> Requesting BeamNG reset {req}")
            reset_req = Message(arbitration_id=canlib.CAN_ID_CMD_RESTART,
                                dlc=canlib.CAN_DLC_CMD_RESTART,
                                data=struct.pack(canlib.CAN_FORMAT_CMD_RESTART, canlib.IGNITION))
            self.cmd_bus.send(reset_req)
        else:
            req['status'] = 501 # Not implemented
        print(f"<{self.__class__.__name__}> Responding with {req}")
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
            if cid == canlib.CAN_ID_HEARTBEAT_REQ:
                req_number = struct.unpack(canlib.CAN_FORMAT_HEARTBEAT_REQ, msg.data)[0]
                heartbeat_ack = Message(arbitration_id=canlib.CAN_ID_HEARTBEAT_ACK,
                                        dlc=canlib.CAN_DLC_HEARTBEAT_ACK,
                                        data=struct.pack(canlib.CAN_FORMAT_HEARTBEAT_ACK, canlib.INFOTAINMENT_BACKEND, req_number))
                self.cmd_bus.send(heartbeat_ack)
            else:
                pass
        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    listener.exit()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    listener = InfotainmentBackend()
    listener.start()
