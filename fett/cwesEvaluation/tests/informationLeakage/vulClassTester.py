#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom informationLeakage methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import glob, os
import re

from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer

class vulClassTester(testgenTargetCompatibilityLayer):
    def __init__(self,settings):
        super().__init__(settings)
        return

    def executeTest(self, binTest):
        return self.typCommand(f"./{binTest}")