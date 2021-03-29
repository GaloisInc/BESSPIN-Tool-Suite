"""
Project: SSITH CyberPhysical Demonstrator
Name: test_infotainment.py
Author: Ethan Lew
Date: 21 January 2021

Tests for the cyberphys BeamNG sim component
"""
import time
import cyberphys.infotainment as cinfo


def test_sim():
    """test the infotainment proxy service

    operational tests:
        1. start / stop
    failure mode tests:
        <None>
    """
    # simple start / stop
    sim = cinfo.InfotainmentUi(None)
    sim.start()
    sim.exit()
    sim.join()
