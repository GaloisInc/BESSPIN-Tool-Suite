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

class RelayManagerComponent(ccomp.Component):
    """Relay control"""
    ## Relay interface and control parameters
    # Relays here are Amazon ASIN B01CN7E0RQ
    relay_usb_product_id = "29987"  # note, this is a USB product ID, not a process ID
    relay_baud = 9600
    relay_on = b'\xA0\x01\x01\xA2'
    relay_off = b'\xA0\x01\x00\xA1'
    relay_delay = 0.1

    def __init__(self, *args):
        super(RelayManagerComponent, self).__init__(*args)

    @staticmethod
    def iterate_relays():
        """iterator to fetch all usb relays"""
        # get all connected serial devices
        usb_devices = list(serial.tools.list_ports_posix.comports())

        for usb_device in usb_devices:
            if RelayManagerComponent.relay_usb_product_id in str(usb_device.pid):

                usb_relay = serial.Serial(port=usb_device.device,
                                          baudrate=RelayManagerComponent.relay_baud,
                                          timeout=0.5)
                yield usb_relay

    @staticmethod
    def turn_on_relays() -> None:
        """turn on all led manager relays"""
        for relay in RelayManagerComponent.iterate_relays():
            print("Turn on USB relay at " + str(relay.port))
            relay.flushInput()
            relay.write(RelayManagerComponent.relay_on)

    @staticmethod
    def turn_off_relays() -> None:
        """turn off all led manager relays"""
        for relay in RelayManagerComponent.iterate_relays():
            print("Turn off USB relay at " + str(relay.port))
            relay.flushInput()
            relay.write(RelayManagerComponent.relay_off)


    @recv_topic("reset")
    def _(self, msg, t):
        """a topic level callback"""
        print("Reset requested")
        self.turn_on_relays()
        time.sleep(self.relay_delay)
        self.turn_off_relays()



def test_relay_manager():
    master = ccomp.Component("master", [], [(44556, 'reset')])
    slave = RelayManagerComponent("slave", [(44556, 'reset')], [])
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


class DummyComponent(ccomp.Component):
    """example component to test the topic callback system"""
    def __init__(self, *args):
        super(DummyComponent, self).__init__(*args)
        print(print(f"{self.name} initialized"))

    @recv_topic("test-topic")
    def _(self, msg, t):
        """a topic level callback"""
        print(f"{self.name} got message: {msg}")


def test_multiple_components():
    """
    The goal is to test inter-connections of multiple components
    """
    # in_socks: connects to them
    # out_socks: binds to them
    RELAY_MANAGER_PORT = 44001
    COMMANDER_PORT = 44002
    HEARTBEAT_MONITOR_PORT = 44003
    N_TARGETS = 2
    WATCHDOG_PORTS = [p+45000 for p in range(1,N_TARGETS+1)]

    ALL_PORTS = WATCHDOG_PORTS + [RELAY_MANAGER_PORT] + [COMMANDER_PORT] + [HEARTBEAT_MONITOR_PORT]
    print(ALL_PORTS)

    components = []

    # # Connect it all together
    # # relay_manager
    # in_socks = [(p,'test-topic') for p in ALL_PORTS if p != RELAY_MANAGER_PORT]
    # out_socks = [(RELAY_MANAGER_PORT, 'test-topic')]
    # print(f"in_socks={in_socks}")
    # print(f"out_socks={out_socks}")
    # relay_manager = DummyComponent("relay-manager", in_socks, out_socks)
    # components.append(relay_manager)

    # # commander
    # in_socks = [(p,'test-topic') for p in ALL_PORTS if p != COMMANDER_PORT]
    # out_socks = [(COMMANDER_PORT, 'test-topic')]
    # print(f"in_socks={in_socks}")
    # print(f"out_socks={out_socks}")
    # commander = DummyComponent("commander", in_socks, out_socks)
    # components.append(commander)

    # # heartbeat-monitor
    # in_socks = [(p,'test-topic') for p in ALL_PORTS if p != HEARTBEAT_MONITOR_PORT]
    # out_socks = [(HEARTBEAT_MONITOR_PORT, 'test-topic')]
    # print(f"in_socks={in_socks}")
    # print(f"out_socks={out_socks}")
    # heartbeat_monitor = DummyComponent("heartbeat_monitor", in_socks, out_socks)
    # components.append(heartbeat_monitor)

    # watchdogs
    wgs = []
    for targetId in range(1,N_TARGETS+1):
        wg_port = WATCHDOG_PORTS[targetId-1]
        in_socks = [(p,'test-topic') for p in ALL_PORTS if p != wg_port]
        out_socks = [(wg_port, 'test-topic')]
        print(f"in_socks={in_socks}")
        print(f"out_socks={out_socks}")
        wg = DummyComponent(f"wg-{targetId}", in_socks, out_socks)
        wgs.append(wg)

    # start + init
    for c in components:
        c.start()
    for wg in wgs:
        wg.start()

    # tear down
    for c in components:
        c.exit()
    for wg in wgs:
        wg.exit()

    for c in components:
        c.join()
    for wg in wgs:
        wg.join()
