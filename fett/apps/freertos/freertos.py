#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute FreeRTOS app
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def deploy(target):
    return ''

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    return deploymentTest(target)

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    # target is a fett target object
    outLog = ''
    outLog += target.runCommand("runFreeRTOSapps",endsWith=">>>End of Fett<<<",erroneousContents=['(Error)','EXIT: exiting FETT with code <1>'],timeout=getSetting('appTimeout'))[1]
    return outLog