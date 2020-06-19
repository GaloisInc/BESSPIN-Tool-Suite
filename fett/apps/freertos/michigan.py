#! /usr/bin/env python3
"""
This is executed after loading the app on the target to execute FreeRTOS app for Michigan
"""

from fett.base.utils.misc import *
from fett.apps.freertos import freertos
from fett.target import aws

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    if (not isEqSetting('target','aws')):
        target.shutdownAndExit (f"<deploymentTest> is not implemented for Michigan on <{getSetting('target')}>",exitCode=EXIT.Implementation)

    return 


@decorate.debugWrap
@decorate.timeWrap
def terminateAppStack (target):
    if (not isEqSetting('target','aws')):
        target.shutdownAndExit (f"<terminateAppStack> is not implemented for Michigan on <{getSetting('target')}>",exitCode=EXIT.Implementation)

    aws.getTapAdaptorDown () #This will ensure that the researcher don't have access anymore
    
    return True