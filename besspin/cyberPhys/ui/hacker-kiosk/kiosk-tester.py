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
        else:
            return (True, inp)


    def do_button_pressed_critical_exploit(self,inp):
        """
        Simulates pressing "CRITICAL EXPLOIT" button
        """
        req = {}
        req['func'] = "critical_exploit"
        req['args'] = inp
        self.sendJson(req)

    def do_button_pressed_info_exploit(self,inp):
        """
        Simulates pressing "INFO EXPLOIT" button
        """
        req = {}
        req['func'] = "info_exploit"
        req['args'] = inp
        self.sendJson(req)

    def do_button_pressed_reset(self,inp):
        """
        Simulates pressing "RESET" button
        """
        req = {}
        req['func'] = "reset"
        req['args'] = {}
        self.sendJson(req)

    def do_button_pressed_next(self,inp):
        """
        Simulates pressing "NEXT" button
        """
        req = {}
        req['func'] = "next"
        req['args'] = {}
        self.sendJson(req)

    def do_button_pressed_ssith_infotainment(self,inp):
        """
        Simulates pressing "SSIH_INFOTAINMENT" button
        """
        req = {}
        req['func'] = "ssith_infotainment"
        req['args'] = {}
        self.sendJson(req)


    def do_button_pressed_ssith_ecu(self,inp):
        """
        Simulates pressing "SSIH_ECU" button
        """
        req = {}
        req['func'] = "ssith_ecu"
        req['args'] = {}
        self.sendJson(req)

if __name__ == '__main__':
    t = TestHackerKiosk()
    t.cmdloop()

