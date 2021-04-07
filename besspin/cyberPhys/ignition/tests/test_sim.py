"""
Project: SSITH CyberPhysical Demonstrator
Name: test_sim.py
Author: Ethan Lew
Date: 11 January 2021

Tests for the cyberphys BeamNG sim component
"""
import cyberphyslib.demonstrator.simulator as csim
from cyberphyslib.demonstrator.handler import ComponentHandler
import time


def test_sim():
    """test the simulation service

    operational tests:
        1. start / stop
        2. enable / disable autopilot test
        3. restart scenario
    failure mode tests:
        <None>
    """
    # simple start / stop
    handler = ComponentHandler()
    msg = handler.start_component(csim.Sim())
    assert msg == csim.BeamNgStatus.READY

    # enable / disable autopilot
    time.sleep(1.0)
    msg = handler.message_component("beamng", csim.BeamNgCommand.ENABLE_AUTOPILOT)
    assert msg == csim.BeamNgStatus.READY
    time.sleep(3.0)
    msg = handler.message_component("beamng", csim.BeamNgCommand.DISABLE_AUTOPILOT)
    assert msg == csim.BeamNgStatus.READY

    # restart scenario
    msg = handler.message_component("beamng", csim.BeamNgCommand.RESTART)
    assert msg == csim.BeamNgStatus.RESTART_FINISHED
    time.sleep(1.0)

    handler.exit()
