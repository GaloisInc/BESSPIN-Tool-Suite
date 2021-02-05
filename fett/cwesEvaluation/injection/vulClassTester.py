#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom resourceManagement methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import re

from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer

from fett.base.utils.misc import *

###############################################################################
#### INJ-1 Constants
###############################################################################

# Opcode of EBREAK instruction
EBREAK_OPCODE = int('00000000000100000000000001110011', 2)

# Minimum return pointer offset to try.  Set to first value out of bounds for
# `buf`.
MIN_RETURN_POINTER_OFFSET = 2

# Maximum return pointer offset to try.
MAX_RETURN_POINTER_OFFSET = 8

###############################################################################
#### INJ-2 Constants
###############################################################################

# Each GNU malloc allocation places a 64 bit size header before the returned
# pointer.  `untrusted1` is a buffer of 64-bit ints, so the offset into this
# header is -1.
BLOCK_SIZE_OFFSET = -1

# Additional bytes beyond the size of `untrusted1` that the test allocates for
# `untrusted2`.
UNTRUSTED2_BYTES_INCREASE = 32

# This is the index to write in `untrusted2` to overwrite the `trusted`
# integer.  It is 16 bytes from the end of the old `untrusted1` buffer, which
# puts it exactly on top of `trusted`.
TRUSTED_OVERWRITE_INDEX = 10

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

    def executeInj1TestPart(self, binTest, returnPointerOffset):
        leakTextBack, isTimeout, address = self.executeUpToLeak(binTest,
                                                                "buffer address")
        if address is None:
            return (leakTextBack, isTimeout)

        _, injectionTextBack, isTimeout, _ = self.runCommand(
                f"0\n{EBREAK_OPCODE}\n{returnPointerOffset}\n{address}\n",
                exitOnError=False,
                suppressErrors=True)
        return (leakTextBack + injectionTextBack), isTimeout

    def executeInj1Test(self, binTest):
        textBack = ""
        for returnPointerOffset in range(MIN_RETURN_POINTER_OFFSET,
                                         MAX_RETURN_POINTER_OFFSET+1):
            textBack += f"\n<OFFSET {returnPointerOffset}>\n";
            partTextBack, isTimeout = \
                    self.executeInj1TestPart(binTest, returnPointerOffset)
            textBack += partTextBack
            if isTimeout:
                textBack += "\n<TIMEOUT>\n"
        return textBack, False

    def executeInj2Test(self, binTest):
        if isEqSetting("osImage", "FreeBSD"):
            return ("<FREEBSD_NOT_IMPLEMENTED>\n"
                    "Inj-2 test is not implemented on FreeBSD\n",
                    False)
        _, leakTextBack, isTimeout, _ = self.runCommand(
                f"./{binTest}",
                endsWith="<READY FOR INPUT>",
                exitOnError=False,
                suppressErrors=True)
        if isTimeout:
            return (leakTextBack, isTimeout)

        _, injectionTextBack, isTimeout, _ = self.runCommand(
                f"{BLOCK_SIZE_OFFSET}\n"
                f"{UNTRUSTED2_BYTES_INCREASE}\n"
                f"{TRUSTED_OVERWRITE_INDEX}\n"
                "1\n",
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
        elif testName == "test_inj_2":
            textBack, isTimeout = self.executeInj2Test(binTest)
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
