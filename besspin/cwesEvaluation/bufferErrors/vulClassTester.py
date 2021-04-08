#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom bufferError methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.compat import cwesEvaluationCompatibilityLayer
from besspin.cwesEvaluation.multitasking.multitasking import multitaskingPart, multitaskingTest

BOF_OUTPUT_FILE = "bof-output.txt"

class vulClassTester(cwesEvaluationCompatibilityLayer):
    """
    This class provides the functionality required to run buffer errors tests
    on the target.
    """
    def __init__(self, target):
        """
        Construct a vulClassTester.

        ARGUMENTS:
        ----------
            target : commonTarget
                Target to run tests on.
        """
        super().__init__(target)
        self.vulClass = "bufferErrors"
        return

    def executeTest(self, binTest):
        """
        Run a single buffer errors test.

        ARGUMENTS:
        ----------
            binTest : String
                Test binary to execute.

        SIDE-EFFECTS:
        -------------
            - Executes <binTest> on the target.

        RETURNS:
        --------
            A string containing test log output.
        """
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
        """
        Generate a <multitaskingTest> object containing instructions for
        running a buffer errors test on <self.target>.  Unlike <executeTest>,
        this function does not execute anything on the target.

        ARGUMENTS:
        ----------
            binTest : String
                Test binary to generate execution instructions for.

        RETURNS:
        --------
            A multitaskingTest object describing how to execute <binTest> on
            <self.target>.
        """
        return multitaskingTest(
                self.vulClass,
                "",
                [multitaskingPart("", "", f"./{binTest}")])
