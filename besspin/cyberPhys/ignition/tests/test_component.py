"""
Project: SSITH CyberPhysical Demonstrator
Name: test_component.py
Author: Ethan Lew
Date: 06 January 2021

Tests for cyberphys base component object type
"""
import cyberphyslib.demonstrator.component as ccomp
import time


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
