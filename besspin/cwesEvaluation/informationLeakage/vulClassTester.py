#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom informationLeakage methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import glob, os
import re
from besspin.base.utils.misc import *
from besspin.cwesEvaluation.compat import testgenTargetCompatibilityLayer
from besspin.cwesEvaluation.multitasking.multitasking import multitaskingPart, multitaskingTest

INFO_OUTPUT_FILE = "info-output.txt"

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "informationLeakage"
        return

    def executeTest(self, binTest):
        try:
            testName = binTest.split('.')[0]
        except Exception as exc:
            self.terminateAndExit (f"executeTest: Failed to parse <{binTest}>.",exc=exc,exitCode=EXIT.Dev_Bug)

        if (isEnabledDict(self.vulClass,'useSelfAssessment')):
            return "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        textBack = self.typCommand(f"./{binTest} {self.redirectOp} {INFO_OUTPUT_FILE}")
        outLog = self.typCommand(f"cat {INFO_OUTPUT_FILE}")
        outLog += textBack
        return outLog

    def testToMultitaskingObj(self, binTest):
        return multitaskingTest(
                self.vulClass,
                "",
                [multitaskingPart("", "", f"./{binTest}")])


