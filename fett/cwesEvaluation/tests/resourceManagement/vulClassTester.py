#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom resourceManagement methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from fett.cwesEvaluation.tests.resourceManagement import cweTests
from fett.cwesEvaluation.compat import testgenTargetCompatabilityLayer

from fett.base.utils.misc import *

# FreeRTOS numTests in case we ever needed to customize that here too
testsInfo = {
    188 : { 'unix' : 6, 'FreeRTOS' : 3 },
    395 : { 'unix' : 2, 'FreeRTOS' : 2 },
    415 : { 'unix' : 2, 'FreeRTOS' : 2 },
    416 : { 'unix' : 2, 'FreeRTOS' : 2 },
    468 : { 'unix' : 2, 'FreeRTOS' : 2 },
    476 : { 'unix' : 3, 'FreeRTOS' : 2 },
    562 : { 'unix' : 2, 'FreeRTOS' : 2 },
    588 : { 'unix' : 2, 'FreeRTOS' : 2 },
    690 : { 'unix' : 2, 'FreeRTOS' : 2 },
    761 : { 'unix' : 4, 'FreeRTOS' : 4 },
    762 : { 'unix' : 3, 'FreeRTOS' : 3 },
    763 : { 'unix' : 2, 'FreeRTOS' : 2 },
    771 : { 'unix' : 5, 'FreeRTOS' : 1 }
}

class vulClassTester(testgenTargetCompatabilityLayer):
    def __init__(self, target):
        super().__init__(target)
        return

    def executeTest (self,binTest):
        outLog = ''
        try:
            testName = binTest.split('.')[0]
            testNum = int(testName.split('_')[1])
        except Exception as exc:
            self.target.shutdownAndExit (f"executeTest: Failed to parse <{binTest}>.",exitCode=EXIT.Dev_Bug)

        if (not isEnabled('isUnix')):
            self.target.shutdownAndExit (f"<executeTest> for FreeRTOS should never be called.",exitCode=EXIT.Dev_Bug)

        if (testNum not in testsInfo):
            self.target.shutdownAndExit(f"<{testNum}> is missing from <testsInfo>.",exitCode=EXIT.Dev_Bug)
        
        if (testsInfo[testNum]['unix'] == 'method'):
            if (hasattr(cweTests,testName)):
                outLog = getattr(getattr(cweTests,testName),testName)(self,binTest)
            else:
                self.target.shutdownAndExit (f"Calling unknown method <{testName}>.",exitCode=EXIT.Dev_Bug)
        else:
            outLog = self.defaultUnixTest(testNum, binTest)

        return outLog

    def defaultUnixTest(self,testNum, binTest):
        outLog = "\n" + '*'*30 + f" TEST {testNum} " + '*'*30 + "\n\n"
        outLog += f"\n<OSIMAGE={getSetting('osImage')}>\n"

        for iPart in range(testsInfo[testNum]['unix']):
            outLog += "-"*20 + "Part{:02d}: <TEST>".format(iPart+1) + "-"*20 + "\n"
            outLog += self.typCommand(f"./{binTest} {iPart+1}")
            
            if (isEnabled('useCustomScoring')): #will need the gdb output here
                outLog += self.getGdbOutput()

            outLog += "-"*60 + "\n\n\n"
            time.sleep (1)
        return outLog