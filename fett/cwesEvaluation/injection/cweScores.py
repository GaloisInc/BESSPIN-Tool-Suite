"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for injection
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES
from fett.cwesEvaluation.injection.customCweScores import *
from fett.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests

VULCLASS = "injection"

@decorate.debugWrap
def scoreAllTests(logs):
    if (isEnabledDict(VULCLASS,"useSelfAssessment")):
        return defaultSelfAssessmentScoreAllTests(VULCLASS, logs)

    ret = []

    # Score the log files
    for name, log in logs:
        logLines = ftReadLines(log)
        try:
            testScorerFunc = getattr(globals()[name],name)
        except Exception as exc:
            errorAndLog(f"scoreAllTests-{VULCLASS}: Could not locate the scorer function for <{name}>",exc=exc)
            ret.append([f"{name.replace('_','-').upper()}", SCORES.FAIL, "Failed to Score!"])
            continue
        scoreInfo = testScorerFunc(logLines)
        ret.append(scoreInfo)
    return ret
