#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute FreeRTOS app
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def runFreeRTOSapps (target):
    # target is a fett target object
    outLog = ''
    outLog += target.runCommand("runFreeRTOSapps",endsWith=">>>End of Fett<<<",timeout=15)[1]
    return outLog