"""
Project: SSITH CyberPhysical Demonstrator
Name: test_sim.py
Author: Ethan Lew
Date: 11 January 2021
Tests for the cyberphys BeamNG sim component
"""
import cyberphyslib.demonstrator.simulator as csim
import cyberphyslib.demonstrator.component as ccomp
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
    csim.Sim.kill_beamng(1)
    handler = ComponentHandler()
    msg = handler.start_component(csim.Sim())
    assert msg == ccomp.ComponentStatus.READY

    # enable / disable autopilot
    time.sleep(1.0)
    sim: csim.Sim = handler["beamng"]
    msg = sim.enable_autopilot_command()
    assert msg == csim.BeamNgStatus.READY
    time.sleep(3.0)
    msg = sim.disable_autopilot_command()
    assert msg == csim.BeamNgStatus.READY

    # restart scenario
    msg = sim.restart_command()
    assert msg == csim.BeamNgStatus.RESTART_FINISHED
    time.sleep(1.0)

    handler.exit()
