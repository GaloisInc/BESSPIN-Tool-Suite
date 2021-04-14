"""
Project: SSITH CyberPhysical Demonstrator
Name: test_component.py
Author: Ethan Lew
Date: 06 January 2021

Tests for cyberphys base component object type
"""
import demonstrator.component as ccomp
from relaymanager import RelayManager

import time
import serial, serial.tools.list_ports_posix

import canlib as ccan

def test_tcpbus():
    IP_ADMIN_PC = "127.0.0.1:5030"
    IP_HACKER_KIOSK = "127.0.0.1:5557"
    nodes = [IP_ADMIN_PC,IP_HACKER_KIOSK]
    admin_pc = ccan.TcpBus(IP_ADMIN_PC, nodes)
    kiosk = ccan.TcpBus(IP_HACKER_KIOSK, nodes)
    tx = ccan.Message(arbitration_id=0XAAFEEB04, dlc=1, data=b'x')
    admin_pc.send(tx)
    msg = kiosk.recv(timeout=0.1)
    print(f"KIOSK RX: {msg}")
    admin_pc.send(tx)
    msg = kiosk.recv(timeout=0.1)
    print(f"KIOSK RX: {msg}")
    kiosk.send(tx)
    msg = admin_pc.recv(timeout=0.1)
    print(f"ADMINPC RX: {msg}")
    kiosk.send(tx)
    msg = admin_pc.recv(timeout=0.1)
    print(f"ADMINPC RX: {msg}")
    print("Done!")


def test_relay_manager():
    master = ccomp.Component("master", [], [(44556, 'base-topic')])
    slave = RelayManager("slave", [(44556, 'base-topic')], [])
    master.start()
    slave.start()
    while not master._ready:
        pass
    time.sleep(1.0)
    print("Ready!")
    master.send_message(ccomp.Message("RESET 0"), "base-topic")
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
        super().__init__(*args)
        print(print(f"{self.name} initialized"))

    @recv_topic("test-topic")
    def _(self, msg, t):
        """a topic level callback"""
        print(f"{self.name} got message: {msg}")

    @recv_topic("test-topic","RESET !c")
    def _(self, data):
        """a topic level callback with specified message"""
        print(f"{self.name} Resetting target {data}!")
        self.send_message(ccomp.Message("RESET DONE"), "test-topic")

def test_multiple_components():
    """
    The goal is to test inter-connections of multiple components
    """
    # in_socks: connects to them
    # out_socks: binds to them
    RELAY_MANAGER_PORT = 44001
    COMMANDER_PORT = 44002
    HEARTBEAT_MONITOR_PORT = 44003
    N_TARGETS = 6
    WATCHDOG_PORTS = [p+45000 for p in range(1,N_TARGETS+1)]

    ALL_PORTS = [RELAY_MANAGER_PORT] + [COMMANDER_PORT] + [HEARTBEAT_MONITOR_PORT] + WATCHDOG_PORTS
    print(ALL_PORTS)

    components = []

    # Connect it all together
    # relay_manager
    in_socks = [(p,'test-topic') for p in ALL_PORTS if p != RELAY_MANAGER_PORT]
    out_socks = [(RELAY_MANAGER_PORT, 'test-topic')]
    print(f"in_socks={in_socks}")
    print(f"out_socks={out_socks}")
    relay_manager = DummyComponent("relay-manager", in_socks, out_socks)
    components.append(relay_manager)

    # commander
    in_socks = [(p,'test-topic') for p in ALL_PORTS if p != COMMANDER_PORT]
    out_socks = [(COMMANDER_PORT, 'test-topic')]
    print(f"in_socks={in_socks}")
    print(f"out_socks={out_socks}")
    commander = DummyComponent("commander", in_socks, out_socks)
    components.append(commander)

    # heartbeat-monitor
    in_socks = [(p,'test-topic') for p in ALL_PORTS if p != HEARTBEAT_MONITOR_PORT]
    out_socks = [(HEARTBEAT_MONITOR_PORT, 'test-topic')]
    print(f"in_socks={in_socks}")
    print(f"out_socks={out_socks}")
    heartbeat_monitor = DummyComponent("heartbeat_monitor", in_socks, out_socks)
    components.append(heartbeat_monitor)

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
        while not c._ready:
            pass

    time.sleep(1)
    commander.send_message(ccomp.Message(1), "test-topic")
    time.sleep(1)
    for wg in wgs:
        wg.start()
        while not wg._ready:
            pass
    commander.send_message(ccomp.Message("RESET 1"), "test-topic")

    time.sleep(1)
    print("Tearing down!")
    # tear down
    for c in components:
        print(f"Calling exit on {c.name}")
        c.exit()
    for wg in wgs:
        wg.exit()

    for c in components:
        print(f"Calling join on {c.name}")
        c.join()
    for wg in wgs:
        wg.join()

    print("Done")