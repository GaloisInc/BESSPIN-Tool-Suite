#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom bufferError methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.compat import cwesEvaluationCompatibilityLayer
from besspin.cwesEvaluation.multitasking.multitasking import multitaskingPart, multitaskingTest

BOF_OUTPUT_FILE = "bof-output.txt"

class vulClassTester(cwesEvaluationCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "bufferErrors"
        return

    def executeTest(self, binTest):
        try:
            testName = binTest.split('.')[0]
        except Exception as exc:
            self.terminateAndExit (f"executeTest: Failed to parse <{binTest}>.",exc=exc,exitCode=EXIT.Dev_Bug)

        if (isEnabledDict(self.vulClass,'useSelfAssessment')):
            return "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        # TTY output (like kmesg output) can interleave with test output and
        # break scoring.  To fix this, redirect test stdout to a separate file,
        # then concatinate it with any TTY output that printed during the run.
        # Test output must come before TTY output to allow scoring to deduce
        # where in the run an error was detected.
        textBack = self.typCommand(f"./{binTest} {self.redirectOp} {BOF_OUTPUT_FILE}")
        outLog = self.typCommand(f"cat {BOF_OUTPUT_FILE}")
        outLog += textBack
        return outLog

    def testToMultitaskingObj(self, binTest):
        return multitaskingTest(
                self.vulClass,
                "",
                [multitaskingPart("", "", f"./{binTest}")])
