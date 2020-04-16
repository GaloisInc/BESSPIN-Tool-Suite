#! /usr/bin/env python3
""" 
The main file to start launching fett
"""

from fett.base.utils.misc import *
import sys

@decorate.debugWrap
@decorate.timeWrap
def launchFett ():
    #check we're in nix
    if (sys.executable.split('/')[1] != 'nix'):
        logAndExit(f"Please run within a nix shell. [Run <nix-shell> in target-fett directory].")