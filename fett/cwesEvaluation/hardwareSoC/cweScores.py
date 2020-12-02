"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for hardwareSoC
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
from fett.cwesEvaluation.hardwareSoC.customCweScores import *
from fett.cwesEvaluation.utils.scoringAux import defaultRecommendationText

@decorate.debugWrap
def scoreAllTests(logs):
    ret = []
    for name, log in logs:
        dispName = name.replace('_','-').upper()
        if (isTestInfoEnabled("hardwareSoC",name,"recommendation")):
            ret.append(defaultRecommendationText(dispName, log))
            continue
        #else: custom score
        logText = ftReadLines(log,splitLines=False)
        try:
            testScorerFunc = getattr(globals()[name],name)
        except Exception as exc:
            errorAndLog(f"scoreAllTests-hardwareSoC: Could not locate the scorer function for <{name}>",exc=exc)
            ret.append([dispName, SCORES.FAIL, "Failed to Score!"])
            continue
        ret.append(testScorerFunc(dispName,logText))
    return ret