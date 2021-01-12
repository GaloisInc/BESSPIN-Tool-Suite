#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom resourceManagement methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer

from fett.base.utils.misc import *

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "injection"
        return

    def executeInj3Test(self, binTest):
        _, leakTextBack, isTimeout, _ = self.runCommand(
                f"./{binTest}",
                endsWith="<LEAKED>",
                exitOnError=False,
                suppressErrors=True)
        if isTimeout:
            return (leakTextBack, True)

        # Address is one line before "<LEAKED>".  Send it back to test over stdin.
        address = leakTextBack.split("\n")[-2]
        _, injectionTextBack, isTimeout, _ = self.runCommand(
                address,
                exitOnError=False,
                suppressErrors=True)
        return (leakTextBack + injectionTextBack), isTimeout

    def executeTest (self,binTest):
        outLog = ''
        testName = binTest.split('.')[0]

        if (isEnabledDict(self.vulClass,'useSelfAssessment')):
            return "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        if (not isEnabled('isUnix')):
            self.terminateAndExit (f"<executeTest> for FreeRTOS should never be called.",exitCode=EXIT.Dev_Bug)

        outLog = "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"
        outLog += f"\n<OSIMAGE={getSetting('osImage')}>\n"

        if testName == "test_inj_3":
            textBack, isTimeout = self.executeInj3Test(binTest)
        else:
            self.terminateAndExit(f"<executeTest> Unknown test <{testName}>.",
                                  exitCode=EXIT.Dev_Bug)

        outLog += textBack
        if (isTimeout):
            outLog += "\n<TIMEOUT>\n"
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += self.getGdbOutput()

        outLog += "-"*60 + "\n\n\n"

        return outLog
