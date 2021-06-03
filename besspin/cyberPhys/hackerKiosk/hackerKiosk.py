#!/usr/bin/env python3
"""
Hacker Kiosk backend

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
import zmq
import threading
import struct
from can import Message

import cyberphyslib.canlib as ccan

class HackerKiosk(threading.Thread):
    CMD_PORT = 5041
    ZMQ_PORT = 5091
    ZMQ_POLL_TIMEOUT = 0.1

    def __init__(self):
        # Threading
        super().__init__(name="HackerKiosk", daemon=False)
        self.stop_evt = threading.Event()

        # CMD network init
        self.can_port = HackerKiosk.CMD_PORT
        self.host = f"10.88.88.2:{self.can_port}" # Can display
        self.nodes = [f"10.88.88.1:{self.can_port}",
                      f"10.88.88.3:{self.can_port}",
                      f"10.88.88.4:{self.can_port}",
                      f"10.88.88.5:{self.can_port}"]
        self.canbus = ccan.TcpBus(self.host, self.nodes)

        # ZMQ init
        self.zmq_port = HackerKiosk.ZMQ_PORT
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.zmq_port}")

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        print(f"<{self.__class__.__name__}> Listening on CAN_PORT {self.can_port}, and ZMQ_PORT {self.zmq_port}")

        # State machine data
        self.active_scenario = ccan.SCENARIO_BASELINE
        # The tuple is (function pointer, arguments?)
        self.allowedFuncCalls = {
            "switchActiveScenario": (self.switchActiveScenario,True),
            "restartComponent": (self.restartComponent,True),
            "hackOta": (self.hackOta,False),
            "hackInfotainment": (self.hackInfotainment,True),
            "hackEcu": (self.hackEcu,True)
        }

        self.cmd_thread = threading.Thread(target=self.cmdLoop, args=[], daemon=True)

    def run(self):
        self.cmd_thread.start()
        while not self.stopped:
            msgs = dict(self.poller.poll(timeout=HackerKiosk.ZMQ_POLL_TIMEOUT))
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
        self.join()

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

        if func in self.allowedFuncCalls:
            # Attempt to evaluate
            try:
                fp,hasArg = self.allowedFuncCalls[func]
                if hasArg:
                    argList = [v for v in args.values()]
                    # TODO: support multi argument?
                    resp['retval'] = fp(argList[0])
                else:
                    resp['retval'] = fp()
                resp['status'] = 200 # OK
            except Exception as exc:
                print(f"<{self.__class__.__name__}> Error caling {func}: {exc}")
                resp['status'] = 500 # Unspecified error
        else:
            resp['status'] = 501 # Not implemented
        if func == "serveScenarioStatus":
            resp['retval'] = self.serveScenarioStatus()

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
            # TODO
            print(f"<{self.__class__.__name__}> CAN_ID={cid}, data={data}")

        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

    def switchActiveScenario(self, scenario_id) -> bool:
        print(f"switchActiveScenario({scenario_id})")
        try:
            msg = Message(arbitration_id=ccan.CAN_ID_CMD_ACTIVE_SCENARIO,
                        data=struct.pack(ccan.CAN_FORMAT_CMD_ACTIVE_SCENARIO, scenario_id))
            self.canbus.send(msg)
            return True
        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error sending message: {msg}: {exc}")
            return False

    def restartComponent(self, component_id) -> bool:
        print(f"restartComponent({component_id})")
        try:
            msg = Message(arbitration_id=ccan.CAN_ID_CMD_RESTART,
                        data=struct.pack(ccan.CAN_FORMAT_CMD_RESTART, component_id))
            self.canbus.send(msg)
            return True
        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error sending message: {msg}: {exc}")
            return False

    def hackOta(self) -> str:
        print(f"hackOta()")
        return "TODO"

    def hackInfotainment(self, hack_id) -> str:
        print(f"hackInfotainment({hack_id})")
        return "TODO"

    def hackEcu(self, hack_id) -> str:
        print(f"hackEcu({hack_id})")
        return "TODO"

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    listener.exit()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    listener = HackerKiosk()
    listener.start()
