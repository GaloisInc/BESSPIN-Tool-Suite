"""
Project: SSITH CyberPhysical Demonstrator
Name: test_canout.py
Author: Ethan Lew
Date: 08 April 2021

Tests for the cyberphys can location poller
"""
import cyberphyslib.demonstrator.can_out as ccout
from cyberphyslib.demonstrator.handler import ComponentHandler
import time


def test_canout():
    """test the canout service

    operational tests:
        1. start / stop
    failure mode tests:
        <None>
    """
    # simple start / stop
    # TODO: conduct more tests
    handler = ComponentHandler()
    msg = handler.start_component(ccout.CanOutPoller(None))
    assert msg == ccout.CanOutStatus.READY
    handler.exit()
