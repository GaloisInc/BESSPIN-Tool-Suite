#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom resourceManagement methods to run tests on qemu|fpga.
Note that the file will be loaded as a sourceFileModule, so using '.' is mandatory
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from . import cweTests

from fett.cwesEvaluation.compat import testgenTargetCompatabilityLayer

class vulClassTester(testgenTargetCompatabilityLayer):
    def __init__(self, target):
        super().__init__(target)
        return

    def executeTest (self,binTest):
        testName = binTest.split('.')[0]
        if (hasattr(cweTests,testName)):
            outLog = getattr(getattr(cweTests,testName),testName)(self,binTest)
        else:
            self.reportAndExit ("Error in {0}: Calling unknown method <{1}>.".format(self.filename,testName))
            outLog = ''
        return outLog
