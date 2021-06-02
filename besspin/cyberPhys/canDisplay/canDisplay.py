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

class CanDisplay(threading.Thread):
    CMD_PORT = 5041
    ZMQ_PORT = 5091

    def __init__(self):
        # Threading
        super().__init__(name="CanDisplay", daemon=False)
        self.stop_evt = threading.Event()

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

        self.cmd_thread = threading.Thread(target=self.cmdLoop, args=[], daemon=True)
    
    def run(self):
        self.cmd_thread.start()
        while not self.stopped:
            self.serve()
    
    def stop(self):
        self.stop_evt.set()

    @property
    def stopped(self):
        return self.stop_evt.is_set()
    
    def exit(self):
        self.stop()
        self.join()

    def serveScenarioStatus(self):
        """
        Reply to requests for update
        """
        return self.state

    def serve(self):
        req = self.socket.recv_json()
        print(f"<{self.__class__.__name__}> Got request {req}")
        assert("func" in req and "args" in req)
        func = req['func']
        args = req['args']
        resp = {}
        resp['args'] = args
        resp['func'] = func
        resp['retval'] = {}
        if func == "serveScenarioStatus":
            resp['retval'] = self.serveScenarioStatus()
            resp['status'] = 200 # OK
        else:
            resp['status'] = 501 # Not implemented
        
        print(f"<{self.__class__.__name__}> Responding with {resp}")
        self.socket.send_json(resp)

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
                if data == ccan.SCENARIO_BASELINE or\
                   data == ccan.SCENARIO_SECURE_ECU or\
                   data == ccan.SCENARIO_SECURE_INFOTAINMENT:
                    self.state = data
                else:
                    print(f"<{self.__class__.__name__}> Unknown scenario ID: {data}")
            elif cid == ccan.CAN_ID_CMD_HACK_ACTIVE:
                self.state = data
                print(f"<{self.__class__.__name__}> Hack ID: {data}")

        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    listener.stop()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    listener = CanDisplay()
    listener.run()
