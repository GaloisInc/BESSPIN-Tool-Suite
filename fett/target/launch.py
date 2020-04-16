#! /usr/bin/env python3
""" 
The main file to start launching fett
"""

from fett.base.utils.misc import *
import sys

@decorate.debugWrap
@decorate.timeWrap
def launchFett ():
    # ------- Global/Misc sanity checks

    #check we're in nix
    if (sys.executable.split('/')[1] != 'nix'):
        logAndExit(f"Please run within a nix shell. [Run <nix-shell> in target-fett directory].")

    #Console mode on FreeRTOS?
    if (isSetting('osImage','FreeRTOS') and isSetting('openConsole',True)):
        warnAndLog (f"Unable to <openConsole> on FreeRTOS. This will be switched off.")
        setSetting('openConsole',False)


    

