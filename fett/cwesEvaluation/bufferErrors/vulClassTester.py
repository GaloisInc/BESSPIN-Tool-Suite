#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom bufferError methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "bufferError"
        return

    def executeTest(self, binTest):
        if isEqSetting("osImage", "debian"):
            # Run test, and if it returns 11, then echo "Segmentation fault".
            # This is needed because the debian buffer errors tests catch
            # SIGSEGV to prevent the kernel from printing debug info that can
            # interleave with test output.  A side effect of catching SIGSEGV
            # is that the normal "Segmentation fault" message is not printed,
            # so we must print it as part of the run command.
            return self.typCommand(f"./{binTest} ; "
                                   "[ $? -eq 11 ] && "
                                   "echo 'Segmentation fault'")
        else:
            return self.typCommand(f"./{binTest}")
