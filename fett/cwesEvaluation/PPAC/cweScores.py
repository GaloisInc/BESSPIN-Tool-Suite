"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for PPAC
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests

@decorate.debugWrap
def scoreAllTests(logs):
    return defaultSelfAssessmentScoreAllTests("PPAC", logs)