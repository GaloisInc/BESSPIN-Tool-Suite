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