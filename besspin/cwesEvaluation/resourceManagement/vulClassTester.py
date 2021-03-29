#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom resourceManagement methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from besspin.cwesEvaluation.resourceManagement import cweTests
from besspin.cwesEvaluation.compat import testgenTargetCompatibilityLayer
from besspin.cwesEvaluation.multitasking.multitasking import hasMultitaskingException, multitaskingPart, multitaskingTest

from besspin.base.utils.misc import *

RM_OUTPUT_FILE = "rm-output.txt"

class vulClassTester(testgenTargetCompatibilityLayer):
    PART_FOOTER = "-"*60 + "\n\n\n"

    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "resourceManagement"
        return

    def getTestNameAndInfoSection(self, binTest):
        testName = binTest.split('.')[0]
        testsInfoSection = "testsInfo" if (testName in getSettingDict(self.vulClass,"testsInfo")) else "funcTestsInfo"
        return (testName, testsInfoSection)

    def executeTest (self,binTest):
        outLog = ''
        testName, testsInfoSection = self.getTestNameAndInfoSection(binTest)

        if (isEnabledDict(self.vulClass,'useSelfAssessment')):
            return "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        if (not isEnabled('isUnix')):
            self.terminateAndExit (f"<executeTest> for FreeRTOS should never be called.",exitCode=EXIT.Dev_Bug)
        
        if (isEqSettingDict(self.vulClass,[testsInfoSection,testName,"unix"],"method")):
            if (hasattr(cweTests,testName)):
                outLog = getattr(getattr(cweTests,testName),testName)(self,binTest)
            else:
                self.terminateAndExit (f"Calling unknown method <{testName}>.",exitCode=EXIT.Dev_Bug)
        else:
            outLog = self.defaultUnixTest(testName, binTest, testsInfoSection)

        return outLog

    def getTestHeader(self, testName):
        header = "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"
        header += f"\n<OSIMAGE={getSetting('osImage')}>\n"
        return header

    def getPartHeader(self, iPart):
        return "-"*20 + "Part{:02d}: <TEST>".format(iPart+1) + "-"*20 + "\n"

    def defaultUnixTest(self, testName, binTest, testsInfoSection):
        outLog = self.getTestHeader(testName)

        for iPart in range(getSettingDict(self.vulClass,[testsInfoSection,testName,"unix"])):
            outLog += self.getPartHeader(iPart)
            if ("extraUnixTimeout" in getSettingDict(self.vulClass,[testsInfoSection,testName])):
                timeout = 120
            else:
                timeout = 60
            # Redirect test output to a file to separate test output from kmesg
            # and shell output
            _,textBack,isTimeout,_ = self.runCommand(f"./{binTest} {iPart+1} "
                                                     f"{self.redirectOp} {RM_OUTPUT_FILE}",
                                        exitOnError=False,suppressErrors=True,timeout=timeout)
            # Add test output to log before any kmesg or shell output
            outLog += self.typCommand(f"cat {RM_OUTPUT_FILE}")
            outLog += textBack
            if (isTimeout):
                outLog += "\n<TIMEOUT>\n"
            if (isEnabled('useCustomScoring')): #will need the gdb output here
                outLog += self.getGdbOutput()

            outLog += self.PART_FOOTER
            time.sleep (1)
        return outLog

    def testToMultitaskingObj(self, binTest):
        testName, testsInfoSection = self.getTestNameAndInfoSection(binTest)
        if (hasMultitaskingException(self.vulClass,
                                     [testsInfoSection, testName])):
            # Test is disabled for multitasking on this OS
            return None
        parts = []
        for iPart in range(getSettingDict(self.vulClass,[testsInfoSection,testName,"unix"])):
            parts.append(multitaskingPart(self.getPartHeader(iPart),
                                          self.PART_FOOTER,
                                          f"./{binTest} {iPart+1}"))
        return multitaskingTest(self.vulClass,
                                self.getTestHeader(testName),
                                parts)
