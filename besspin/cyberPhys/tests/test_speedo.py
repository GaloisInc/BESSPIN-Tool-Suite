"""
Project: SSITH CyberPhysical Demonstrator
Name: test_speedo.py
Author: Ethan Lew
Date: 06 January 2021

Tests for the cyberphys speedometer component
"""
import time
import demonstrator.speedometer as cspeed
import demonstrator.component as ccomp
import demonstrator.config as cconf


def test_speedo():
    """test the speedometer

    operational tests:
        1. start / stop
        2. Send sensor data and see speedometer change
    failure mode tests:
        <None>
    """
    # simple start / stop
    speedo = cspeed.Speedo()
    speedo.start()
    speedo.exit()

    # send stub message and see if speedo accepts it
    speedo = cspeed.Speedo()
    stub = ccomp.Component("speedo-stub", [], [cconf.BEAMNG_COMPONENT_OUTPUT[-1]])
    speedo.start()
    stub.start()
    state = {"wheelspeed": 30.0,
             "fuel": 0.0,
             "throttle": 0.5,
             "gear": "D",
             "oil": 34,
             "parkingbrake": 0.0,
             "highbeam": False,
             "headlights": False,
             "right_signal": 0.6,
             "left_signal": 0.6,
             "esc_active": False,
             "abs_active": False,
             "brake_lights": False}
    for i in range(10):
        time.sleep(0.1)
        state["fuel"] = i
        stub.send_message(ccomp.Message(state), "beamng-sensors")
    speedo.exit()
    stub.exit()
