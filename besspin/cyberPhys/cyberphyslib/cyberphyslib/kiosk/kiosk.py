"""
Project: SSITH CyberPhysical Demonstrator
director.py
Author: Michal Podhradsky <mpodhradsky@galois.com>, Ethan Lew <elew@galois.com>
Date: 06/09/2021
Python 3.8.3
O/S: Windows 10

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
import struct
from can import Message

import cyberphyslib.canlib as ccan


class HackerKiosk:
    """
    TODO: switch to StoppableThread to avoid duplication
    TODO: implement a can send method to cut down on redundant code
    TODO: fold this into the KioskDirector for the state transitions
    """
    CMD_PORT = 5041
    ZMQ_PORT = 5091
    ZMQ_POLL_TIMEOUT = 0.1

    def __init__(self, dnc):
        # TODO: not a thread Threading
        #super().__init__(name="HackerKiosk", daemon=False)

        # CMD network init
        self.can_port = dnc.network_ports['canbusPort']
        self.host_name = 'InfotainmentThinClient' # NOTE: is this wrong?
        self.host = f"{dnc.nodes[self.host_name]}:{self.can_port}"
        self.nodes = [f'{v}:{self.can_port}' for k,v in dnc.nodes.items() if v != dnc.nodes[self.host_name]]
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
        self.allowed_func_calls = {
            "switchActiveScenario": (self.switch_active_scenario, True),
            "restartComponent": (self.restart_component, True),
            "hackOta": (self.hack_ota, False),
            "hackInfotainment": (self.hack_infotainment, True),
            "hackEcu": (self.hack_ecu, True),
            "sendHackActiveMsg": (self.send_hack_active_message, True)
        }

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

        if func in self.allowed_func_calls:
            # Attempt to evaluate
            try:
                fp,hasArg = self.allowed_func_calls[func]
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
            # TODO: what is this?
            resp['retval'] = self.serveScenarioStatus()

        print(f"<{self.__class__.__name__}> Responding with {resp}")
        self.socket.send_json(resp)

    def process_cmd_msg(self, msg):
        """
        process CMD message
        """
        cid, data = msg.arbitration_id, msg.data

        try:
            # TODO
            print(f"<{self.__class__.__name__}> CAN_ID={cid}, data={data}")

        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

    def switch_active_scenario(self, scenario_id) -> bool:
        print(f"switchActiveScenario({scenario_id})")
        return self.send_can_msg("CMD_ACTIVE_SCENARIO", scenario_id)

    def restart_component(self, component_id) -> bool:
        print(f"restartComponent({component_id})")
        return self.send_can_msg("CMD_RESTART", component_id)

    def hack_ota(self) -> str:
        print(f"hackOta()")
        return "TODO"

    def hack_infotainment(self, hack_id) -> str:
        print(f"hackInfotainment({hack_id})")
        return "TODO"

    def hack_ecu(self, hack_id) -> str:
        print(f"hackEcu({hack_id})")
        return "TODO"

    def send_hack_active_message(self, hack_id) -> bool:
        print(f"sendHackActiveMsg({hack_id})")
        return self.send_can_msg("CMD_HACK_ACTIVE", hack_id)

    def send_can_msg(self, pack_name, data):
        msg = None
        arb_id = getattr(ccan, f"CAN_ID_{pack_name}")
        format = getattr(ccan, f"CAN_FORMAT_{pack_name}")
        try:
            msg = Message(arbitration_id=arb_id,
                          data=struct.pack(format, data))
            self.canbus.send(msg)
            return True
        except Exception as exc:
            print(f"<{self.__class__.__name__}> Error sending message: {msg}: {exc}")
            return False


