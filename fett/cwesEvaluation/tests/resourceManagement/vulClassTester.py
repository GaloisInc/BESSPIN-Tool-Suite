#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom resourceManagement methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from fett.cwesEvaluation.tests.resourceManagement import cweTests
from fett.cwesEvaluation.compat import testgenTargetCompatabilityLayer

from fett.base.utils.misc import *

# FreeRTOS numTests in case we ever needed to customize that here too
testsInfo = {
    188: { 'unix' : 6, 'FreeRTOS' : 3 }
}

class vulClassTester(testgenTargetCompatabilityLayer):
    def __init__(self, target):
        super().__init__(target)
        return

    def executeTest (self,binTest):
        outLog = ''
        testName = binTest.split('.')[0]
        testNum = testName.split('_')[1]

        if (not isEnabled('isUnix')):
            target.shutdownAndExit (f"<executeTest> for FreeRTOS should never be called.",exitCode=EXIT.Dev_Bug)

        if (testNum not in testsInfo):
            target.shutdownAndExit(f"<{testNum}> is missing from <testsInfo>.",exitCode=EXIT.Dev_Bug)
        
        if (testsInfo[testNum]['unix'] == 'method'):
            if (hasattr(cweTests,testName)):
                outLog = getattr(getattr(cweTests,testName),testName)(self,binTest)
            else:
                target.shutdownAndExit (f"Calling unknown method <{testName}>.",exitCode=EXIT.Dev_Bug)
        else:
            outLog = self.defaultUnixTest(testNum)

        return outLog

    def defaultUnixTest(self,testNum):
        outLog = "\n" + '*'*30 + f" TEST {testNum} " + '*'*30 + "\n\n"
        outLog += f"\n<OSIMAGE={getSetting('osImage')}>\n"

        for iPart in testsInfo[testsInfo]['unix']:
            outLog += "-"*20 + "Part{:02d}: <TEST>".format(iPart+1) + "-"*20 + "\n"
            outLog += self.typCommand(f"./{binTest} {iPart+1}")
            
            if (isEnabled('useCustomScoring')): #will need the gdb output here
                outLog += self.getGdbOutput()

            outLog += "-"*60 + "\n\n\n"
            time.sleep (1)
        return outLog