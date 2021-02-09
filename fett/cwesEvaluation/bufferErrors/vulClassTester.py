#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom bufferError methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer

BOF_OUTPUT_FILE = "bof-output.txt"

class vulClassTester(testgenTargetCompatibilityLayer):
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

        if isEqSetting("osImage", "debian"):
            # On debian, kmesg output can interleave with test output and break
            # scoring.  To fix this, redirect test stdout to a separate file,
            # then concatinate it with any kmesg output that printed during the
            # run.  Test output must come before kmesg output to allow scoring
            # to deduce where in the run an error was detected.
            kmesg_output = self.typCommand(f"./{binTest} > {BOF_OUTPUT_FILE}")
            test_output = self.typCommand(f"cat {BOF_OUTPUT_FILE}")
            return test_output + kmesg_output
        else:
            return self.typCommand(f"./{binTest}")
