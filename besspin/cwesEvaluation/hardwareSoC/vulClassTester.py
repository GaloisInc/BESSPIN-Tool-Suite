#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom hardwareSoC methods for runTests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from besspin.cwesEvaluation.compat import cwesEvaluationCompatibilityLayer

from besspin.base.utils.misc import *

class vulClassTester(cwesEvaluationCompatibilityLayer):
    def __init__(self, target):
        super().__init__(target)
        self.vulClass = "hardwareSoC"
        return
