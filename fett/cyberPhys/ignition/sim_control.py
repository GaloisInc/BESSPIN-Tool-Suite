#!/usr/bin/env python
"""
Project: SSITH CyberPhysical Demonstrator
Name: sim_control.py
Author: Ethan Lew <elew@galois.com>
Date: 01 October 2020

Interactive Script to Show Simulator Service Control
"""
import cyberphys.simulator as simulator
import cyberphys.component as component
import cyberphys.config as config
import cyberphys.message as message

import time
import logging


def print_commands():
    """print available commands"""
    print("Commands:")
    print("\n".join([f"\t{c.name}" for c in simulator.BeamNgCommand]))


class StateListen(component.Component):
    """simple component to wait on beamng state messages"""
    def __init__(self):
        super().__init__("recv", [(5006, 'beamng-state')], [(5005, 'beamng-commands')])

    @recv_topic("beamng-state")
    def _(self, msg, t):
        print(f"StateListen Received State {msg}")


# disable logger, so that console doesn't get messy
logger = logging.getLogger()
logger.disabled = True

# create components
bng = simulator.Sim()
comp = StateListen()

# start threads
bng.start()
comp.start()

# startup message
print("Interact Simulator Service")
print_commands()

# simple console to send commands to service
while(True):
    usr_in = input(">")
    comm = getattr(simulator.BeamNgCommand, usr_in.upper(), None)
    if comm is None:
        print(f"Error! {comm} is not a recognized command")
        print_commands()
    else:
        comp.send_message(message.Message(comm),
                         "beamng-commands", message.MessageLevel.NORMAL)
        comp.send_message(message.Message(simulator.BeamNgCommand.REQUEST_STATE),
                         "beamng-commands", message.MessageLevel.NORMAL)
        time.sleep(0.5)
