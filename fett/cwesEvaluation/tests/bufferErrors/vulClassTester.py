#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom bufferError methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.cwesEvaluation.compat import testgenTargetCompatabilityLayer

class vulClassTester(testgenTargetCompatabilityLayer):
    def __init__(self,settings):
        super().__init__(settings)
        return

    def executeTest(self, binTest):
        return self.typCommand(f"./{binTest}")
