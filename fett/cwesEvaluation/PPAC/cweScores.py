"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for PPAC
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests, doKeywordsExistInText
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore

VULCLASS = "PPAC"

scoreVectors = {
    "test_PPAC_2" : [
        (SCORES.CALL_ERR, ["<INVALID>"]),
        (SCORES.HIGH, ["<ROOT-GRANTED>"]),
        (SCORES.LOW, ["<ROOT-DENIED>", "<USER-GRANTED>"]),
        (SCORES.NONE, ["<USER-DENIED>"])
    ]
}

@decorate.debugWrap
def scoreAllTests(logs):
    if (isEnabledDict(VULCLASS,"useSelfAssessment")):
        return defaultSelfAssessmentScoreAllTests(VULCLASS, logs)

    ret = []
    for testName, log in logs:
        logText = ftReadLines(log, splitLines=False)

        score = SCORES.FAIL
        try:
            for xScore, keywords in scoreVectors[testName]:
                if (len(keywords)==0):
                    raise Exception(f"Empty keywords for {xScore}.")
                if (all(doKeywordsExistInText(logText,keywords).values())):
                    score = xScore
                    break
        except Exception as exc:
            errorAndLog(f"Failed to score <{VULCLASS}:{testName}>.",exc=exc)

        ret.append([
            f"{testName.replace('_','-').upper()}", 
            adjustToCustomScore(logText.splitlines(),score), 
            getSettingDict(VULCLASS, ["testsInfo", testName, "cweText"])])

    return ret
