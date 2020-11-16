#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom hardwareSoC methods for runTests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer
import fett.cwesEvaluation.hardwareSoC.cweTests as cweTests
from fett.base.utils.misc import *
import pexpect

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        return

    def executeTest (self,binTest):
        outLog = ''
        try:
            testName = binTest.split('.')[0]
            testNum = int(testName.split('_')[1])
        except Exception as exc:
            self.terminateAndExit (f"executeTest: Failed to parse <{binTest}>.",exc=exc,exitCode=EXIT.Dev_Bug)

        outLog = "\n" + '*'*30 + f" TEST {testNum} " + '*'*30 + "\n\n"
        outLog += f"<OSIMAGE={self.osImage}>\n"
        outLog += f"<XLEN={self.xlen}>\n"

        if (self.getTestInfo(testName,'gdb') and (not self.hasGdbAccess())):
            warnAndLog (f"Test <{testNum}> requires GDB access!")
            outLog += f"<NOGDB>\n"
            return outLog

        if (self.getTestInfo(testName,'hasMethod')):
            if (hasattr(cweTests,testName)):
                outLog += getattr(getattr(cweTests,testName),testName)(self,binTest)
            else:
                self.terminateAndExit (f"Calling unknown method <{testName}>.",exitCode=EXIT.Dev_Bug)
        else:
            outLog = self.defaultTest(testNum, binTest)

        return outLog

    def getTestInfo (self,testName,infoName):
        return (getSettingDict("hardwareSoC",["testsInfo",testName,infoName])==1)

    def defaultTest(self, testNum, binTest):
        self.terminateAndExit (f"<defaultTest> is not yet implemented for <hardwareSoC>.",exitCode=EXIT.Implementation)
        return

    def endFreeRTOSTest (self):
        textBack,wasTimeout,idxReturn = self.expectFromTarget([">>>End of Fett<<<", pexpect.EOF],
                    "End FreeRTOS Test", exitOnError=False, timeout=getSetting('FreeRTOStimeout'))
        if (idxReturn == 1):
            self.terminateAndExit("<runTests> Unexpected EOF during test run.", exitCode=EXIT.Dev_Bug)
        elif (wasTimeout):
            textBack += "\n<TIMEOUT>\n"

        return textBack

class inGdbTest: 
    def __init__(self,target):
        self.target = target
          
    def __enter__(self): 
        # Pause the OS
        self.target.interruptGdb()
        return self
      
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        # Resume the OS
        self.target.continueGdb()