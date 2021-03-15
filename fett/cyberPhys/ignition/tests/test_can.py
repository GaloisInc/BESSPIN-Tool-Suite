"""
Project: SSITH CyberPhysical Demonstrator
Name: test_can.py
Author: Ethan Lew
Date: 06 January 2021

Tests for cyberphys CAN objects
"""
import socket
import pytest
import cyberphys.can as ccan
from can import Message


class ExampleTestListener(ccan.CanListener):
    """test listener object for testing can network objects"""
    def __init__(self, name: str):
        super().__init__(name)
        self.reset()

    def reset(self):
        self.did_receive = False
        self.id = None
        self.data_len = None
        self.bytes = None

    def recv(self, id: int, data_len: int, bytes_in):
        """add members that signal that store arguments for test assertions"""
        self.id = id
        self.data_len = data_len
        self.bytes = bytes_in
        self.did_receive = True


def test_udp_bus():
    """test the udp manager with can like data tranmission

    operational tests:
        1. loopback: sender and receiver recover same data
    failure mode tests:
            1. no data
            2. invalid can address
    """
    # simple loopback test
    msg_send = Message(arbitration_id=234, data=b'12', is_extended_id=True)
    udpb = ccan.UDPBus(4505, "")
    udpb.send(msg_send)
    msg = udpb.recv()
    # not all message fields are expected to be equivalent
    assert msg.arbitration_id == 234
    assert msg.data == b'12'
    assert msg.dlc == 2

    # attempt to send empty message -- defined to be invalid
    msg_empty = Message(arbitration_id=234, data=b'', is_extended_id=True)
    with pytest.raises(ccan.InvalidCanMessageError):
        udpb.send(msg_empty)

    #test address too big
    msg_send = Message(arbitration_id=0xAAAAAAAAAA, data=b'12', is_extended_id=True)
    with pytest.raises(ccan.InvalidCanMessageError):
        udpb.send(msg_send)


def test_can_network():
    """test the udp can network object

    operational tests:
        1. send / receiver between two network elements
        2. test ip blacklisting / whitelisting
    failure mode tests:
        1. Invalid address sent to blacklist / whitelist
    """
    # test simple send/receive with a test listener
    cnet = ccan.CanUdpNetwork("candump", 223, "")
    csend= ccan.CanUdpNetwork("cansend", 223, "")
    tl = ExampleTestListener("t1")
    cnet.register(tl)
    assert tl.did_receive == False
    csend.send(123, b'12')
    cnet.recv()
    assert tl.did_receive == True

    # test blacklist -- expect timeout
    tl.did_receive = False
    cnet.blacklist = [socket.gethostbyname(socket.gethostname())]
    csend.send(123, b'12')
    cnet.recv(timeout=0.1)
    assert tl.did_receive == False

    # test whitelist -- expect timeout
    tl.did_receive = False
    cnet.whitelist = ['0.0.0.0']
    csend.send(123, b'12')
    cnet.recv(timeout=0.1)
    assert tl.did_receive == False

    # test whitelist/blacklist sanitization
    cnet.blacklist = ["127.0.0.1", "192.168.0.1"]
    cnet.whitelist = ["127.0.0.1", "192.168.0.1"]
    with pytest.raises(ValueError):
        cnet.blacklist = [89, "invalid"]
    with pytest.raises(ValueError):
        cnet.blacklist= [89, "invalid"]


def test_can_multiverse():
    """test the can network "multiverse" (mux)

    operational tests:
        1. send / receiver between a can network element and a
            network managed by the Multiverse
    """
    # test that listeners in networks only receive if active
    t1 = ExampleTestListener("t1")
    tm = ExampleTestListener("tm")
    csend= ccan.CanUdpNetwork("cansend", 223, "")
    cnet0 = ccan.CanUdpNetwork("can0", 223, "")
    cnet1 = ccan.CanUdpNetwork("can1", 223, "")
    cnet1.register(t1)
    cmult = ccan.CanMultiverse("multiverse",
                               [cnet0, cnet1],
                               "can0")

    cmult.register(tm)

    assert t1.did_receive == False
    assert tm.did_receive == False
    csend.send(123, b'12')
    cmult.recv()
    assert t1.did_receive == False
    assert tm.did_receive == True
    cmult.select("can1")
    csend.send(123, b'12')
    cmult.recv()
    assert t1.did_receive == True

    tm.did_receive = False
    cmult.start()
    assert tm.did_receive == False
    csend.send(123, b'12')
    while not tm.did_receive:
        pass
    cmult.exit()
    cmult.join()
