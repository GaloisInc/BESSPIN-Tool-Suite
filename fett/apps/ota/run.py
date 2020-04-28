#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app (OTA)
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def runApp (target):
    # target is a fett target object
    outLog = ''
    outLog += target.runCommand("runOta",endsWith=">>>End of Fett<<<",timeout=15)
    return outLog