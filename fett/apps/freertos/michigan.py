#! /usr/bin/env python3
"""
This is executed after loading the app on the target to execute FreeRTOS app for Michigan
"""

from fett.base.utils.misc import *
import time, subprocess

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
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

    # Curl the help page -- note that it returns exit code 8. suprocess.getoutput ignores return code by default
    curlOut = subprocess.getoutput(f"curl -L -s -X GET -m 10 -I http://{serverUrl}/{curlTestPath}")
    reportTestResult ("Curl HTTP test page",("HTTP/1.0 200 OK" in curlOut))
    
    # lynx tests
    def lynxTest (query, testNum):
        command = ['lynx', '-source', f"\"http://{serverUrl}/{query}\""]
        printAndLog(f"Lynx test-{testNum}: {' '.join(command)}",doPrint=False,tee=getSetting('appLog'))
        try:
            outLynx = str(subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=30),'utf-8')
            printAndLog(outLynx,doPrint=False,tee=getSetting('appLog'))
        except Exception as exc:
            target.shutdownAndExit (f"Test [query-{testNum}] - FAILED!",exc=exc,exitCode=EXIT.Run)

        reportTestResult (f"query-{testNum}",(('error' not in outLynx) and ('ERROR' not in outLynx)))

    for iQuery,xQuery in enumerate(lynxTestQueries):
        lynxTest(xQuery,iQuery)

    return 


@decorate.debugWrap
@decorate.timeWrap
def terminateAppStack (target):
    if (not isEqSetting('target','aws')):
        target.shutdownAndExit (f"<terminateAppStack> is not implemented for Michigan on <{getSetting('target')}>",exitCode=EXIT.Implementation)

    setAdaptorUpDown(getSetting('awsTapAdaptorName'), 'down') #This will ensure that the researcher don't have access anymore
    
    return True