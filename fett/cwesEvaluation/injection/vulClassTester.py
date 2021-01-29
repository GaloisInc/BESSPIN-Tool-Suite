#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom resourceManagement methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import re

from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer

from fett.base.utils.misc import *

# Opcode of EBREAK instruction
EBREAK_OPCODE = int('00000000000100000000000001110011', 2)

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "injection"
        return

    def executeUpToLeak(self, binTest, leakId):
        """
        Execute binTest until it prints <LEAKED>, then extract the address
        identified by leakId
        """
        _, leakTextBack, isTimeout, _ = self.runCommand(
                f"./{binTest}",
                endsWith="<LEAKED>",
                exitOnError=False,
                suppressErrors=True)
        if isTimeout:
            return (leakTextBack, True, None)

        # Parse leaked address from output
        address_match = re.search(f'<{leakId} (0x[0-9a-f]+)>',
                                  leakTextBack)
        if address_match is None:
            # Test made it to <LEAKED> statement, but the address didn't leak.
            # Something went wrong with the test.
            return (leakTextBack + "\n<FAIL>\nCouldn't find leaked address.\n",
                    False,
                    None)

        return (leakTextBack, False, address_match.group(1))

    def executeInj1Test(self, binTest):
        leakTextBack, isTimeout, address = self.executeUpToLeak(binTest,
                                                                "buffer address")
        if address is None:
            return (leakTextBack, isTimeout)

        returnPointerOffset = getSettingDict(
                self.vulClass,
                ["testsInfo", "test_inj_1", "unixReturnPointerOffset"])
        _, injectionTextBack, isTimeout, _ = self.runCommand(
                f"0\n{EBREAK_OPCODE}\n{returnPointerOffset}\n{address}\n",
                exitOnError=False,
                suppressErrors=True)
        return (leakTextBack + injectionTextBack), isTimeout

    def executeInj3Test(self, binTest):
        leakTextBack, isTimeout, address = self.executeUpToLeak(binTest,
                                                                "malicious address")
        if address is None:
            return (leakTextBack, isTimeout)

        _, injectionTextBack, isTimeout, _ = self.runCommand(
                address,
                exitOnError=False,
                suppressErrors=True)
        return (leakTextBack + injectionTextBack), isTimeout

    def executeTest (self,binTest):
        outLog = ''
        testName = binTest.split('.')[0]

        if (isEnabledDict(self.vulClass,'useSelfAssessment')):
            return "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        if (not isEnabled('isUnix')):
            self.terminateAndExit (f"<executeTest> for FreeRTOS should never be called.",exitCode=EXIT.Dev_Bug)

        outLog = "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"
        outLog += f"\n<OSIMAGE={getSetting('osImage')}>\n"

        if testName == "test_inj_1":
            textBack, isTimeout = self.executeInj1Test(binTest)
        elif testName == "test_inj_3":
            textBack, isTimeout = self.executeInj3Test(binTest)
        else:
            self.terminateAndExit(f"<executeTest> Unknown test <{testName}>.",
                                  exitCode=EXIT.Dev_Bug)

        outLog += textBack
        if (isTimeout):
            outLog += "\n<TIMEOUT>\n"
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += self.getGdbOutput()

        outLog += "-"*60 + "\n\n\n"

        return outLog
