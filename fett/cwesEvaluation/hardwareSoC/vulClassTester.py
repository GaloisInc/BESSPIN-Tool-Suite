#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom hardwareSoC methods for runTests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer
from fett.base.utils.misc import *

class vulClassTester(testgenTargetCompatibilityLayer):
    def executeTest (self,binTest):
        self.shutdownAndExit("<executeTest> is not yet implemented for <hardwareSoC>.",exitCode=EXIT.Implementation)
        return
