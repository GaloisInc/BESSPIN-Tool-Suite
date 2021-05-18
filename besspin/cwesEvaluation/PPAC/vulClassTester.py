#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom PPAC methods to for runTests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from besspin.cwesEvaluation.compat import cwesEvaluationCompatibilityLayer

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.PPAC import cweTests

class vulClassTester(cwesEvaluationCompatibilityLayer):
    def __init__ (self,target):
        super().__init__(target)
        self.vulClass = "PPAC"
        return

    def executeTest (self,binTest):
        outLog = ''
        testName = binTest.split('.')[0]

        outLog += "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        if (isEnabledDict(self.vulClass,'useSelfAssessment')):
            return outLog

        if (hasattr(cweTests,testName)):
            outLog += getattr(getattr(cweTests,testName),testName)(self)
        else:
            self.terminateAndExit(f"Failed to find method <{testName}>.",exitCode=EXIT.Dev_Bug)
        
        return outLog

    def getShells(self):
        shellRoot = self.getDefaultEndWith(userName='root')
        shellUser = self.getDefaultEndWith(userName=self.userName)
        if ((not isinstance(shellRoot,str)) or (not isinstance(shellUser,str))):
            self.terminateAndExit(f"Expected strings for <shellRoot> and <shellUser>",exitCode=EXIT.Dev_Bug)
        shellRoot = shellRoot.replace('~',f"/home/{self.userName}")
        return (shellRoot,shellUser)


