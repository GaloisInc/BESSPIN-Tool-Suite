#!/usr/env/python3
"""
Project: SSITH CyberPhysical Demonstrator
Name: draw_director.py
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Date: 08 August 2021

Draw the ignition state machine director for documentation
"""
if __name__ == "__main__":
    # Project libs
    from cyberphyslib.demonstrator import director
    director.IgnitionDirector.draw_graph("../specs/state_machine_ignition_implemented.png")

