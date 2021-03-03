#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom PPAC methods to for runTests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer

from fett.base.utils.misc import *
from fett.cwesEvaluation.PPAC import cweTests

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__ (self,target):
        super().__init__(target)
        self.vulClass = "PPAC"
        return

    def executeTest (self,binTest):
        outLog = ''
        testName = binTest.split('.')[0]
        
        outLog += "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        if (hasattr(cweTests,testName)):
            outLog += getattr(getattr(cweTests,testName),testName)(self)
        else:
            self.terminateAndExit(f"Failed to find method <{testName}>.",exitCode=EXIT.Dev_Bug)
        
        return outLog


