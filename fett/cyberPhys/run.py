#! /usr/bin/env python3
""" 
The main file for running cyberPhys
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def runCyberPhys(xTarget):
    # here anything that needs to be done on the targets before handing the user the prompt
    return

@decorate.debugWrap
@decorate.timeWrap
def watchdog(targetId):
    """
    This function keeps monitoring the target, and if it goes down, it resets it
    " There are 3 things that we need to make sure while developing this:
    " 1. Can watch
    " 2. resets
    " 3. Is able to exit
    """
    return
