"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for injection
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import re

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
from besspin.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests

VULCLASS = "injection"

@decorate.debugWrap
def scoreAllTests(logs):
    if (isEnabledDict(VULCLASS,"useSelfAssessment")):
        return defaultSelfAssessmentScoreAllTests(VULCLASS, logs)

    ret = []

    # Score the log files
    for name, log in logs:
        logLines = ftReadLines(log)
        if name == 'test_INJ_1':
            scoreInfo = scoreInj1Test(logLines, name)
        else:
            scoreInfo = scoreControlFlowTest(logLines, name)
        ret.append(scoreInfo)
    return ret

def getTestNumAndInfo(testName):
    testNum = testName.split("test_")[1].replace("_", "-")
    info = getSettingDict(VULCLASS, ["testsInfo", testName, "cweText"])
    return (testNum, info)

def scoreInj1TestPart(logLines, testNum, info):
    if "<QEMU_NOT_IMPLEMENTED>" in logLines:
        score = SCORES.NOT_IMPLEMENTED
        info = "Not implemented on QEMU."
    elif "<BEGIN_INJECTION_TEST>" not in logLines:
        # Test did not run
        score = SCORES.FAIL
    elif "<INVALID>" in logLines or "<RETURNING>" not in logLines:
        score = SCORES.CALL_ERR
    elif ("<END_INJECTION_TEST>" in logLines):
        score = SCORES.NONE
    else:
        score = SCORES.HIGH

    return [f"TEST-{testNum}", adjustToCustomScore(logLines, score), info]

def scoreInj1Test(logLines, testName):
    testNum, info = getTestNumAndInfo(testName)

    # Get indices for each test part
    indices = [x[1] for x in zip(logLines, range(len(logLines))) if
               re.match("<OFFSET [0-9]+>", x[0])]
    indices.append(len(logLines))

    # Score each part
    scores = {}
    for i in range(len(indices)-1):
        score = scoreInj1TestPart(logLines[indices[i]:indices[i+1]], testNum, info)
        # Only need one of each score, so it's OK that they get potentially
        # overwritten
        scores[score[1]] = score

    # Order is significant here.  For example, if one of the parts scores HIGH
    # and the others score NONE and DETECTED, then the overall score is HIGH.
    for score in [SCORES.NOT_IMPLEMENTED, SCORES.HIGH, SCORES.DETECTED, SCORES.NONE]:
        if score in scores:
            return scores[score]

    # A valid offset was never found
    return [f"TEST-{testNum}", adjustToCustomScore(logLines, SCORES.FAIL), info]

def scoreControlFlowTest(logLines, testName):
    """
    This scoring function works for all tests that use injection to modify the
    control flow of the test program.  Tests should print
    "<EXECUTING_BENIGN_CODE>" when control flow is not modified, and
    "<EXECUTING_MALICIOUS_CODE>" when control flow is modified.
    """

    testNum, info = getTestNumAndInfo(testName)

    if "<QEMU_NOT_IMPLEMENTED>" in logLines:
        score = SCORES.NOT_IMPLEMENTED
        info = "Not implemented on QEMU."
    elif "<FREEBSD_NOT_IMPLEMENTED>" in logLines:
        score = SCORES.NOT_IMPLEMENTED
        info = "Not implemented on FreeBSD."
    elif "<BEGIN_INJECTION_TEST>" not in logLines:
        # Test did not run
        score = SCORES.FAIL
    elif "<INVALID>" in logLines:
        score = SCORES.CALL_ERR
    elif "<EXECUTING_BENIGN_CODE>" in logLines:
        score = SCORES.NONE
    else:
        score = SCORES.HIGH

    return [f"TEST-{testNum}", adjustToCustomScore(logLines, score), info]
