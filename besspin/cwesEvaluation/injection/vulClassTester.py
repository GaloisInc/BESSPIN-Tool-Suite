#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom resourceManagement methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import re

from besspin.cwesEvaluation.compat import cwesEvaluationCompatibilityLayer

from besspin.base.utils.misc import *

INJ_OUTPUT_FILE = "inj-output.txt"

###############################################################################
#### INJ-1 Constants
###############################################################################

# Opcode of EBREAK instruction
EBREAK_OPCODE = int('00000000000100000000000001110011', 2)

# Minimum return pointer offset to try.  Set to first value out of bounds for
# `buf`.  The debian and FreeRTOS tests have the same
# MAX_RETURN_POINTER_OFFSET, but the debian test's MIN_RETURN_POINTER_OFFSET is
# one larger than on FreeRTOS.  This is because `buf` on debian is 2 elements,
# but it is only a single integer on FreeRTOS.  Therefore, the test on debian
# skips testing with an offset of 1 because it's known to be part of `buf` and
# cannot be the return pointer.  As a result, the Debian test has 7 parts while
# the FreeRTOS test has 8 parts.
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

class vulClassTester(cwesEvaluationCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "injection"
        return

    def executeUpToLeak(self, binTest, leakId):
        """
        Execute binTest until it prints <LEAKED>, then extract the address
        identified by leakId
        """
        # Information is leaked over stderr.  Redirect all other output to a
        # file to prevent interleaving with kmesg/shell output.
        _, leakTextBack, isTimeout, _ = self.runCommand(
                f"./{binTest} > {INJ_OUTPUT_FILE}",
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
                f"0\n{EBREAK_OPCODE}\n{returnPointerOffset}\n{address}",
                exitOnError=False,
                suppressErrors=True)
        testStdout = self.typCommand(f"cat {INJ_OUTPUT_FILE}")
        return (leakTextBack + testStdout + injectionTextBack), isTimeout

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
                f"./{binTest} > {INJ_OUTPUT_FILE}",
                endsWith="<READY FOR INPUT>",
                exitOnError=False,
                suppressErrors=True)
        if isTimeout:
            testStdout = self.typCommand(f"cat {INJ_OUTPUT_FILE}")
            return (testStdout + leakTextBack, isTimeout)

        _, injectionTextBack, isTimeout, _ = self.runCommand(
                f"{BLOCK_SIZE_OFFSET}\n"
                f"{UNTRUSTED2_BYTES_INCREASE}\n"
                f"{TRUSTED_OVERWRITE_INDEX}\n"
                "1",
                exitOnError=False,
                suppressErrors=True)
        testStdout = self.typCommand(f"cat {INJ_OUTPUT_FILE}")
        return (leakTextBack + testStdout + injectionTextBack), isTimeout

    def executeInj3Test(self, binTest):
        leakTextBack, isTimeout, address = self.executeUpToLeak(binTest,
                                                                "malicious address")
        if address is None:
            return (leakTextBack, isTimeout)

        _, injectionTextBack, isTimeout, _ = self.runCommand(
                address,
                exitOnError=False,
                suppressErrors=True)
        testStdout = self.typCommand(f"cat {INJ_OUTPUT_FILE}")
        return (leakTextBack + testStdout + injectionTextBack), isTimeout

    def executeTest (self,binTest):
        outLog = ''
        testName = binTest.split('.')[0]

        if (isEnabledDict(self.vulClass,'useSelfAssessment')):
            return "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        if (not isEnabled('isUnix')):
            self.terminateAndExit (f"<executeTest> for FreeRTOS should never be called.",exitCode=EXIT.Dev_Bug)

        outLog = "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"
        outLog += f"\n<OSIMAGE={getSetting('osImage')}>\n"

        if testName == "test_INJ_1":
            textBack, isTimeout = self.executeInj1Test(binTest)
        elif testName == "test_INJ_2":
            textBack, isTimeout = self.executeInj2Test(binTest)
        elif testName == "test_INJ_3":
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
