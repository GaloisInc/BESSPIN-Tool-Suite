#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring functions for CWE tests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """


from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore

@decorate.debugWrap
def scoreAllTests(logs, testsDir):
    logAndExit("<scoreAllTests> is not yet implemented for <hardwareSoC>.",exitCode=EXIT.implementation)