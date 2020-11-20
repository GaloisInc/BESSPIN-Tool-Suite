#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom PPAC methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import sys, os
from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer
from fett.cwesEvaluation.PPAC import cweTests

from fett.base.utils.misc import *

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__ (self,target):
        super().__init__(target)
        self.vulClass = "PPAC"
        return

    def executeTest (self,binTest):
        outLog = ''
        try:
            testName = binTest.split('.')[0]
            testNum = testName.split('test_')[1]
        except Exception as exc:
            self.terminateAndExit (f"executeTest: Failed to parse <{binTest}>.",exc=exc,exitCode=EXIT.Dev_Bug)

        outLog = "\n" + '*'*30 + f" TEST {testNum} " + '*'*30 + "\n\n"
        outLog += f"<OSIMAGE={self.osImage}>\n"

        if (self.isTestInfoEnabled(testName,'recommendation')):
            outLog += self.recommendationTest (testName)
        elif (self.isTestInfoEnabled(testName,'hasMethod')):
            if (hasattr(cweTests,testName)):
                outLog += getattr(getattr(cweTests,testName),testName)(self,binTest)
            else:
                self.terminateAndExit (f"Calling unknown method <{testName}>.",exitCode=EXIT.Dev_Bug)
        else:
            outLog += self.defaultTest(testNum, binTest)

        return outLog
