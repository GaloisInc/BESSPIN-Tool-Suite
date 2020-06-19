#! /usr/bin/env python3
"""
This is executed after loading the app on the target to execute FreeRTOS app for Michigan
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target, curlTest, WEB_REPLY_OK):
    if (not isEqSetting('target','aws')):
        target.shutdownAndExit (f"<deploymentTest> is not implemented for Michigan on <{getSetting('target')}>",exitCode=EXIT.Implementation)

    serverUrl = f"{target.ipTarget}:{getSettingDict('michiganInfo',['httpPort'])}"
    curlTestPath = getSettingDict('michiganInfo',['curlTestPath'])
    lynxTestQueries = getSettingDict('michiganInfo',['lynxTestQueries'])

    def reportTestResult (testName,isSuccess):
        if (isSuccess):
            printAndLog(f"Test [{testName}] - OK!",doPrint=True,tee=getSetting('appLog'))
        else:
            target.shutdownAndExit (f"Test [{testName}] - FAILED!",exitCode=EXIT.Run)

    # Curl the help page
    contentLength,code = curlTest(target, f"http://{serverUrl}/{curlTestPath}")
    reportTestResult("Curl HTTP test page", code==WEB_REPLY_OK)

    # lynx tests

    return 


@decorate.debugWrap
@decorate.timeWrap
def terminateAppStack (target):
    if (not isEqSetting('target','aws')):
        target.shutdownAndExit (f"<terminateAppStack> is not implemented for Michigan on <{getSetting('target')}>",exitCode=EXIT.Implementation)

    setAdaptorUpDown(getSetting('awsTapAdaptorName'), 'down') #This will ensure that the researcher don't have access anymore
    
    return True