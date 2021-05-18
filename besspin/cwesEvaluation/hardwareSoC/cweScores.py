"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for hardwareSoC
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests

@decorate.debugWrap
def scoreAllTests(logs):
    return defaultSelfAssessmentScoreAllTests("hardwareSoC", logs)
