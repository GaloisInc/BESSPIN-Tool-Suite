"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for resourceManagement
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
from fett.cwesEvaluation.resourceManagement.customCweScores import *

@decorate.debugWrap
def scoreAllTests(logs):
    ret = []
    for name, log in logs:
        logLines = ftReadLines(log)
        try:
            testScorerFunc = getattr(globals()[name],name)
        except Exception as exc:
            errorAndLog(f"scoreAllTests-resourceManagement: Could not locate the scorer function for <{name}>",exc=exc)
            ret.append([f"{name.replace('_','-').upper()}", SCORES.FAIL, "Failed to Score!"])
            continue
        ret.append(testScorerFunc(logLines))
    return ret