#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom PPAC methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import sys, os
from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer
from fett.cwesEvaluation.PPAC import cweTests

from fett.base.utils.misc import *

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__ (self,settings):
        super().__init__(settings)
        return

    def executeTest (self,binTest):
        testName = binTest.split('.')[0]
        if (hasattr(cweTests,testName)):
            outLog = getattr(getattr(cweTests,testName),testName)(self,binTest)
        elif (isEnabled('pocExploitsMode')):
            self.terminateAndExit('<pocExploitsMode> not implemented',
                       exitCode=EXIT.Implementation)
        else:
            self.terminateAndExit(f"Calling unknown method <{testName}>.",exitCode=EXIT.Dev_Bug)
            outLog = ''
        return outLog

    def executeOnRoot (self,commands):
        switchBack = not self.isCurrentUserRoot
        if (switchBack): #only do this if user is not root
            self.switchUser()
        for command in commands:
            self.runCommand (command)
        if (switchBack):
            self.switchUser()
        return
