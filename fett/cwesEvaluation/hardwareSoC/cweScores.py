"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for hardwareSoC
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests

@decorate.debugWrap
def scoreAllTests(logs):
    return defaultSelfAssessmentScoreAllTests("hardwareSoC", logs)
