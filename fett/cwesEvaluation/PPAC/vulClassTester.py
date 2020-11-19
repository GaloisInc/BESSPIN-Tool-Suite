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

        if (self.getTestInfo(testName,'recommendation')):
            outLog += self.recommendationTest (testName)
        elif (self.getTestInfo(testName,'hasMethod')):
            if (hasattr(cweTests,testName)):
                outLog += getattr(getattr(cweTests,testName),testName)(self,binTest)
            else:
                self.terminateAndExit (f"Calling unknown method <{testName}>.",exitCode=EXIT.Dev_Bug)
        else:
            outLog += self.defaultTest(testNum, binTest)

        return outLog

    def getTestInfo (self,testName,infoName):
        return (getSettingDict("PPAC",["testsInfo",testName,infoName])==1)

    def defaultTest(self, testNum, binTest):
        self.terminateAndExit (f"<defaultTest> is not yet implemented for <PPAC>.",exitCode=EXIT.Implementation)
        return

    def recommendationTest(self, testName):
        return f'<TEXT={getSettingDict("PPAC",["testsInfo",testName,"text"])}>\n'
