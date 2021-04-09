"""
Project: SSITH CyberPhysical Demonstrator
Name: test_component.py
Author: Ethan Lew
Date: 06 January 2021

Tests for cyberphys base component object type
"""
import demonstrator.component as ccomp
import time

import serial, serial.tools.list_ports_posix

class LedManagerComponent(ccomp.Component):
    """Relay control"""
        ## Relay interface and control parameters
    # Relays here are Amazon ASIN B01CN7E0RQ
    relay_usb_product_id = "29987"  # note, this is a USB product ID, not a process ID
    relay_baud = 9600
    relay_on = b'\xA0\x01\x01\xA2'
    relay_off = b'\xA0\x01\x00\xA1'
    relay_delay = 1.0

    def __init__(self, *args):
        super(LedManagerComponent, self).__init__(*args)


    @staticmethod
    def iterate_relays():
        """iterator to fetch all usb relays"""
        # get all connected serial devices
        usb_devices = list(serial.tools.list_ports_posix.comports())

        for usb_device in usb_devices:
            if LedManagerComponent.relay_usb_product_id in str(usb_device.pid):

                usb_relay = serial.Serial(port=usb_device.device,
                                          baudrate=LedManagerComponent.relay_baud,
                                          timeout=0.5)
                yield usb_relay

    @staticmethod
    def turn_on_relays(relay_pause: float = 4.0) -> None:
        """turn on all led manager relays"""
        for relay in LedManagerComponent.iterate_relays():
            print("Turn on USB relay at " + str(relay.port))
            relay.flushInput()
            relay.write(LedManagerComponent.relay_on)
            #time.sleep(relay_pause) # NOTE: needed?

    @staticmethod
    def turn_off_relays() -> None:
        """turn off all led manager relays"""
        for relay in LedManagerComponent.iterate_relays():
            print("Turn off USB relay at " + str(relay.port))
            relay.flushInput()
            relay.write(LedManagerComponent.relay_off)


    @recv_topic("reset")
    def _(self, msg, t):
        """a topic level callback"""
        print("Reset requested")
        self.turn_on_relays()
        time.sleep(self.relay_delay)
        self.turn_off_relays()



def test_ledmanager():
    master = ccomp.Component("master", [], [(44556, 'reset')])
    slave = LedManagerComponent("slave", [(44556, 'reset')], [])
    master.start()
    slave.start()
    while not master._ready:
        pass
    time.sleep(1.0)
    print("Ready!")
    master.send_message(ccomp.Message(0xA), "reset")
    time.sleep(0.1)
    master.exit()
    slave.exit()
    master.join()
    slave.join()
    print("Done")


class ExampleTestComponent(ccomp.Component):
    """example component to test the topic callback system"""
    def __init__(self, *args):
        super(ExampleTestComponent, self).__init__(*args)
        self.reset()

    def reset(self):
        self.test_a = False
        self.test_b = False

    @recv_topic("test-topic")
    def _(self, msg, t):
        """a topic level callback"""
        self.test_a = True

    @recv_topic("test-topic", 0xA)
    def _(self, t):
        """a topic with specified message callback"""
        self.test_b = True


def test_thread_exiting():
    """test the stoppable thread object

    operational tests:
        1. launch thread, wait, and exit it
    failure mode tests:
        <None>
    """
    # test simple create and exit
    te = ccomp.ThreadExiting("test-component")
    te.start()
    assert te.stopped == False
    te.exit()
    assert te.stopped == True


def test_component():
    """test the component object

    operational tests:
        1. Start / exit
        2. Test component messaging by creating a connection and sending a small message
        3. Test topic, message level messaging
        4. Check callback properties
    failure mode tests:
    """
    # test exiting
    c = ccomp.Component("c", [], [])
    c.start()
    c.exit()
    c.join()
    assert c.stopped == True

    # test message send / receive
    ca = ccomp.Component("compa", [], [(44556, 'test-topic')])
    cb = ExampleTestComponent("compb", [(44556, 'test-topic')], [])
    ca.start()
    cb.start()
    while not ca._ready:
        pass
    ca.send_message(ccomp.Message(0xC), "test-topic")
    time.sleep(0.1)
    assert cb.test_a == True
    assert cb.test_b == False

    cb.reset()
    # should trigger two receives -- test-topic and (test-topic, 0xA)
    ca.send_message(ccomp.Message(0xA), "test-topic")
    time.sleep(0.1)
    assert cb.test_a == True
    assert cb.test_b == True
    ca.exit()
    cb.exit()
    ca.join()
    cb.join()

    # check properties
    assert set(cb.recv_can_methods) == set()
    assert set(cb.recv_methods) == {("test-topic",), ("test-topic", 0xA)}
