"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for injection
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
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
        scoreInfo = scoreControlFlowTest(logLines, name)
        ret.append(scoreInfo)
    return ret

def scoreControlFlowTest(logLines, testName):
    """
    This scoring function works for all tests that use injection to modify the
    control flow of the test program.  Tests should print
    "<EXECUTING_BENIGN_CODE>" when control flow is not modified, and
    "<EXECUTING_MALICIOUS_CODE>" when control flow is modified.
    """

    testNum = testName[5:].upper().replace("_", "-")
    info = getSettingDict(VULCLASS, ["testsInfo", testName, "cweText"])

    if "<FAIL>" in logLines:
        score = SCORES.FAIL
    elif "<QEMU_NOT_IMPLEMENTED>" in logLines:
        score = SCORES.NOT_IMPLEMENTED
        info = "Not implemented on QEMU."
    elif "<INVALID>" in logLines:
        score = SCORES.INVALID
    elif "<EXECUTING_MALICIOUS_CODE>" in logLines:
        score = SCORES.HIGH
    elif "<EXECUTING_BENIGN_CODE>" in logLines:
        score = SCORES.NONE
    else:
        score = SCORES.FAIL

    return [f"TEST-{testNum}", adjustToCustomScore(logLines, score), info]
