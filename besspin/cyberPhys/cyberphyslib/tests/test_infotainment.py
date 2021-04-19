"""
Project: SSITH CyberPhysical Demonstrator
Name: test_infotainment.py
Author: Ethan Lew
Date: 21 January 2021

Tests for the cyberphys BeamNG sim component
"""
<<<<<<< HEAD
import demonstrator.infotainment as cinfo


def test_sim():
=======
import cyberphyslib.demonstrator.infotainment as cinfo
import cyberphyslib.demonstrator.can as ccan
import cyberphyslib.demonstrator.component as ccomp
import cyberphyslib.canlib.canspecs as cspecs
from cyberphyslib.demonstrator.handler import ComponentHandler

import struct
import time


def test_infotainment_ui():
>>>>>>> origin/cyberphys/feature/ignition-state-machine
    """test the infotainment proxy service

    operational tests:
        1. start / stop
    failure mode tests:
        <None>
    """
    # simple start / stop
<<<<<<< HEAD
    sim = cinfo.InfotainmentUi(None)
    sim.start()
    sim.exit()
    sim.join()
=======
    ui = cinfo.InfotainmentUi(None)
    ui.start()
    ui.exit()
    ui.join()

    player = cinfo.InfotainmentPlayer(None)
    player.start()
    player.exit()
    player.join()


def test_infotainment_player_handler():
    """test the infotainment services

    operational tests:
        1. send can button presses and listen to the results
    failure mode tests:
        <None>
    """
    # create can network multiverse (mux)
    sip = "127.0.0.1"
    can_multiverse = ccan.CanMultiverse("multiverse", [ccan.CanUdpNetwork("base", 5009, sip)], default_network="base")

    # Start the infotainment mux
    info_net = ccan.CanUdpNetwork("info-net", 5010, sip)
    imux = cinfo.InfotainmentProxy(info_net, can_multiverse)

    # add the infotainment services
    can_multiverse.register(imux.info_ui)
    can_multiverse.register(imux.info_player)

    # startup the can multiverse and the infotainment pieces
    handler = ComponentHandler()
    msg = handler.start_component(ccan.CanMultiverseComponent(can_multiverse))
    assert msg == ccomp.ComponentStatus.READY

    msg = handler.start_component(imux.info_ui)
    assert msg == ccomp.ComponentStatus.READY

    msg = handler.start_component(imux.info_player)
    assert msg == ccomp.ComponentStatus.READY

    # send button presses
    can_multiverse.send(cspecs.CAN_ID_INFOTAINMENT_STATE, struct.pack("B", 0x3F))
    time.sleep(5.0)
    can_multiverse.send(cspecs.CAN_ID_INFOTAINMENT_STATE, struct.pack("B", 0x3B))
    time.sleep(5.0)

    # TODO: test UI?

    handler.exit()
>>>>>>> origin/cyberphys/feature/ignition-state-machine
