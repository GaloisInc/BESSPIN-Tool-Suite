#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom numericErrors methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import os

from besspin.cwesEvaluation.compat import testgenTargetCompatibilityLayer
from besspin.cwesEvaluation.multitasking.multitasking import multitaskingPart, multitaskingTest
from besspin.base.utils.misc import *

## All tests are assumed to have 1 part except for the following:
partCount = {"test_456" : 3,
             "test_457" : 2,
             "test_665" : 2,
             "test_824" : 2}

NE_OUTPUT_FILE = "ne-output.txt"

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "numericErrors"
        return

    def getTestInfo(self, binTest):
        try:
            testName = binTest.split('.')[0]
            testNum = testName.split('_')[1]
        except Exception as exc:
            self.terminateAndExit (f"executeTest: Failed to parse <{binTest}>.",exc=exc,exitCode=EXIT.Dev_Bug)
        if testName in partCount:
            numParts = partCount [testName]
        else:
            numParts = 1

        return (testName, testName, numParts)

    def getTestHeader(self, numParts):
        return f"<NUMPARTS={numParts}>\n"

    def getPartHeader(self, testNum, part):
        return f"TEST {testNum} PART P0{part + 1}\n"

    def executeTest (self,binTest):
        testName, testNum, numParts = self.getTestInfo(binTest)
        if (isEnabledDict(self.vulClass,'useSelfAssessment')):
            return "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        outLog = self.getTestHeader(numParts)
        for p in range (numParts):
            # Add "TEST xxx PART P0y" to the log. This is recognized in
            # ./cweScores.py to signal the start of a test part's log
            outLog += self.getPartHeader(testNum, p)
            command = f"./{binTest} {p + 1} {self.redirectOp} {NE_OUTPUT_FILE}"
            textBack = self.runCommand (command)[1]
            outLog += self.typCommand(f"cat {NE_OUTPUT_FILE}")
            outLog += textBack
            if (isEnabled('useCustomScoring')): #will need the gdb output here
                outLog += self.getGdbOutput()

        return outLog

    def testToMultitaskingObj(self, binTest):
        testName, testNum, numParts = self.getTestInfo(binTest)
        parts = []
        for p in range(numParts):
            parts.append(multitaskingPart(self.getPartHeader(testNum, p),
                                          "",
                                          f"./{binTest} {p + 1}"))
        return multitaskingTest(self.vulClass,
                                self.getTestHeader(numParts),
                                parts)

