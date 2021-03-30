"""
Project: SSITH CyberPhysical Demonstrator
Name: test_sim.py
Author: Ethan Lew
Date: 11 January 2021

Tests for the cyberphys BeamNG sim component
"""
import cyberphyslib.demonstrator.simulator as csim


def test_sim():
    """test the simulation service

    operational tests:
        1. start / stop
    failure mode tests:
        <None>
    """
    # simple start / stop
    sim = csim.Sim()
    sim.start()
    sim.exit()
    sim.join()

