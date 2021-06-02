#!/usr/bin/env python3
"""
Simple CAN listener. Listens to CAN CMD messages,
update the display when status changes.
"""

import logging
import zmq
from enum import Enum
import threading

import cyberphyslib.canlib as ccan

# make CAN module less noisy
logging.getLogger("can").setLevel(logging.WARNING)

class CanDisplay:
    CMD_PORT = 5041
    ZMQ_PORT = 5091

    def __init__(self):
        # CMD network init
        self.can_port = CanDisplay.CMD_PORT
        self.host = f"10.88.88.5:{self.can_port}" # Can display
        self.nodes = [f"10.88.88.1:{self.can_port}",
                      f"10.88.88.2:{self.can_port}",
                      f"10.88.88.3:{self.can_port}",
                      f"10.88.88.4:{self.can_port}"]
        self.canbus = ccan.TcpBus(self.host, self.nodes)

        # ZMQ init
        self.zmq_port = CanDisplay.ZMQ_PORT
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.zmq_port}")

        self.state = ccan.SCENARIO_BASELINE

        print(f"<{self.__class__.__name__}> Listening on CAN_PORT {self.can_port}, and ZMQ_PORT {self.zmq_port}")
    
    def serveScenarioStatus(self):
        """
        Reply to requests for update
        """
        req = self.socket.recv_json()
        res = self.state
        print(f"<{self.__class__.__name__}> Got request {req}, responding with {res}")
        self.socket.send_json(res)

    def serveLoop(self):
        while True:
            self.serveScenarioStatus()

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

        try:
            if cid == ccan.CAN_ID_CMD_ACTIVE_SCENARIO:
                if msg.data == ccan.SCENARIO_BASELINE or\
                   msg.data == ccan.SCENARIO_SECURE_ECU or\
                   msg.data == ccan.SCENARIO_SECURE_INFOTAINMENT:
                    self.state = msg.data
                else:
                    print(f"<{self.__class__.__name__}> Unknown scenario ID: {msg.data}")
            elif cid == ccan.CAN_ID_CMD_HACK_ACTIVE:
                self.state = msg.data
                print(f"<{self.__class__.__name__}> Hack ID: {msg.data}")
            else:
                print(f"<{self.__class__.__name__}> {msg}")

        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

if __name__ == '__main__':
    listener = CanDisplay()

    t1 = threading.Thread(target=listener.serveLoop, args=[])
    t2 = threading.Thread(target=listener.cmdLoop, args=[])
    
    t1.start()
    t2.start()

    t1.join()
    t2.join()
    
