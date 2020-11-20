#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom bufferError methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "bufferError"
        return

    def executeTest(self, binTest):
        return self.typCommand(f"./{binTest}")
