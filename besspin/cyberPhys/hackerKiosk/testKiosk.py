#!/usr/bin/env python3
"""
Hacker Kiosk tester

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
import cmd
import time
import zmq
import argparse

import cyberphyslib.canlib as ccan

class TestHackerKiosk(cmd.Cmd):
    intro = 'Welcome to test hacker interactive cmd shell. Type help or ? to list commands.\n'
    prompt = '(kiosk) '

    ZMQ_PORT = 5091
    ZMQ_POLL_TIMEOUT = 0.1

    def __init__(self):
        super(TestHackerKiosk, self).__init__()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.addr = f"tcp://localhost:{TestHackerKiosk.ZMQ_PORT}"
        print(f"Connecting to {self.addr}")
        self.socket.connect(self.addr)

    def preloop(self):
        self.name = "interactiveLoop"
        print(f"<{self.__class__.__name__}> Starting.")

    def postloop(self):
        print(f"<{self.__class__.__name__}> Terminating.")

    def precmd(self, line):
        if (line != 'EOF'):
            line = line.lower() #commands are case insensitive
        return line

    def emptyline(self): #to avoid repeating the last command on <enter>
        return

    def sendJson(self,req):
        self.socket.send_json(req)
        recv = self.socket.recv_json()
        print(f"{recv}")
    
    def parseInput(self,inp) -> (bool, int):
        if (len(inp.split(' '))>1) or inp=='':
            return (False, 0)
        try:
            inp_as_int = int(inp)
        except Exception as exc:
            try:
                inp_as_int = int(inp,16)
            except Exception as exc:
                return (False, 0)
        return (True, inp_as_int)



    def do_switch_scenario(self,inp):
        """switchActiveScenario SCENARIO_ID
        switches the active scenario with SCENARIO_ID"""
        ok, val = self.parseInput(inp)
        if not ok:
            print(self.do_restart.__doc__)
            return
        scenario_id = val
        req = {}
        req['func'] = "switchActiveScenario"
        req['args'] = {"scenario_id": scenario_id}
        self.sendJson(req)
        return

    def do_restart_component(self,inp):
        """restartComponent COMPONENT_ID
        restart a component with COMPONENT_ID"""
        ok, val = self.parseInput(inp)
        if not ok:
            print(self.do_restart.__doc__)
            return
        component_id = val
        req = {}
        req['func'] = "restartComponent"
        req['args'] = {"component_id": component_id}
        self.sendJson(req)
        return

    def do_hack_ota(self,inp):
        """hackOta
        hack OTA server"""
        req = {}
        req['func'] = "hackOta"
        req['args'] = {}
        self.sendJson(req)
        return

    def do_hack_infotainment(self,inp):
        """hackInfotainment HACK_ID
        hack infotainment with HACK_ID hack"""
        ok, val = self.parseInput(inp)
        if not ok:
            print(self.do_restart.__doc__)
            return
        hack_id = val
        req = {}
        req['func'] = "hackInfotainment"
        req['args'] = {"hack_id": hack_id}
        self.sendJson(req)
        return

    def do_hack_ecu(self,inp):
        """hackEcu HACK_ID
        hack ECU with HACK_ID hack"""
        ok, val = self.parseInput(inp)
        if not ok:
            print(self.do_restart.__doc__)
            return
        hack_id = val
        req = {}
        req['func'] = "hackEcu"
        req['args'] = {"hack_id": hack_id}
        self.sendJson(req)
        return

    def do_hack_active(self, inp):
        """hack_active HACK_ID
        send HACK_ACTIVE msg with  HACK_ID hack"""
        ok, val = self.parseInput(inp)
        if not ok:
            print(self.do_restart.__doc__)
            return
        hack_id = val
        req = {}
        req['func'] = "sendHackActiveMsg"
        req['args'] = {"hack_id": hack_id}
        self.sendJson(req)
        return

if __name__ == '__main__':
    t = TestHackerKiosk()
    t.cmdloop()

