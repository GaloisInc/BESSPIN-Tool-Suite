#!/usr/env/python3
"""
Project: SSITH CyberPhysical Demonstrator
Name: ignition.py
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Date: 15 April 2021

"""
# Project libs
from cyberphyslib.demonstrator import director


if __name__ == "__main__":
    ignition = director.IgnitionDirector()
    ignition.run()

