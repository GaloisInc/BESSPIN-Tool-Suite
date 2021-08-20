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
import unittest

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


class HackerKioskUnitTests(unittest.TestCase):
    DEFAULT_DELAY_S = 10
    SHORT_DElAY_S = 5
    LONG_DELAY_S = 30

    def run_reset(self, t: TestHackerKiosk):
        print("Pressing reset")
        t.do_button_pressed_reset("")
        # This takes ~20s to reset the two components
        # OTA_SERVER_3 and INFO_SERVER_3
        time.sleep(HackerKioskUnitTests.LONG_DELAY_S)

    def run_introduction(self, t: TestHackerKiosk):
        print("Introduction")

        print("Pressing NEXT")
        t.do_button_pressed_next("")
        time.sleep(HackerKioskUnitTests.DEFAULT_DELAY_S)

        print("Pressing NEXT. Will hack OTA -> Upload successful!")
        t.do_button_pressed_next("")
        time.sleep(HackerKioskUnitTests.DEFAULT_DELAY_S)

        print("Pressing NEXT. Gets you to the OTA hacking screen")
        t.do_button_pressed_next("")
        time.sleep(HackerKioskUnitTests.DEFAULT_DELAY_S)


    def run_infotainment_exploits(self, t: TestHackerKiosk):
        print("Infotainment exploits")

        print("Pressing volumeUp")
        t.do_button_pressed_info_exploit("volumeUp")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        print("Pressing volumeDown")
        t.do_button_pressed_info_exploit("volumeDown")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        print("Pressing exfil")
        t.do_button_pressed_info_exploit("exfil")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        print("Pressing changeStation_1")
        t.do_button_pressed_info_exploit("changeStation_1")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        print("Pressing changeStation_2")
        t.do_button_pressed_info_exploit("changeStation_2")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        print("Pressing changeStation_3")
        t.do_button_pressed_info_exploit("changeStation_3")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        time.sleep(HackerKioskUnitTests.DEFAULT_DELAY_S)
        print("Infotainment exploits done")


    def run_critical_exploits(self, t: TestHackerKiosk):
        print("Critical exploits")

        print("disable brakes")
        t.do_button_pressed_critical_exploit("brakes")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)
        print("enable brakes")
        t.do_button_pressed_critical_exploit("brakes")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        print("full throttle")
        t.do_button_pressed_critical_exploit("throttle")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)
        print("nominal throttle")
        t.do_button_pressed_critical_exploit("throttle")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        print("lkas hacked")
        t.do_button_pressed_critical_exploit("lkas")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)
        print("lkas nominal")
        t.do_button_pressed_critical_exploit("lkas")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        print("transmission hacked")
        t.do_button_pressed_critical_exploit("transmission")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)
        print("transmission nominal")
        t.do_button_pressed_critical_exploit("transmission")
        time.sleep(HackerKioskUnitTests.SHORT_DElAY_S)

        time.sleep(HackerKioskUnitTests.DEFAULT_DELAY_S)
        print("Critical exploits done")


    def test_scenario_baseline_to_secure_infotainment(self):
        t = TestHackerKiosk()

        self.run_introduction(t)

        self.run_infotainment_exploits(t)

        self.run_critical_exploits(t)

        print("Pressing next, goes to SECURE_INTO_SCENARIO")
        t.do_button_pressed_next("")
        # This takes 38s to reset OTA_SERVER_1 + INFO_SERVER_1 + Target1
        time.sleep(HackerKioskUnitTests.DEFAULT_DELAY_S)
        time.sleep(HackerKioskUnitTests.LONG_DELAY_S)

        print("Choosing SSITH infotainment scenario")
        t.do_button_pressed_ssith_infotainment("")

        self.run_infotainment_exploits(t)

        self.run_reset(t)


    def test_scenario_baseline_to_secure_ecu(self):
        t = TestHackerKiosk()

        self.run_introduction(t)

        self.run_infotainment_exploits(t)

        self.run_critical_exploits(t)

        print("Pressing next, goes to SECURE_INTO_SCENARIO")
        t.do_button_pressed_next("")
        # This takes 38s to reset OTA_SERVER_1 + INFO_SERVER_1 + Target1
        time.sleep(HackerKioskUnitTests.DEFAULT_DELAY_S)
        time.sleep(HackerKioskUnitTests.LONG_DELAY_S)

        print("Choosing SSITH ecu scenario")
        t.do_button_pressed_ssith_ecu("")

        self.run_infotainment_exploits(t)

        self.run_reset(t)

    def run_scenarios(self):
        iter_max = 100
        for i in range(1,iter_max):
            print(f"Launching iteration {i}")
            print("Lanching BASELINE->SECURE_ECU scenario")
            self.test_scenario_baseline_to_secure_ecu()
            print("Fnished BASELINE->SECURE_ECU scenario")
            print("Lanching BASELINE->SECURE_INFOTAINMENT scenario")
            self.test_scenario_baseline_to_secure_infotainment()
            print("Finished BASELINE->SECURE_INFOTAINMENT scenario")
            print(f"Finished iteration {i}")
        print("Done")
