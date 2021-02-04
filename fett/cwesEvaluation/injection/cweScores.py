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
        if name == 'test_inj_1':
            scoreInfo = scoreInj1Test(logLines, name)
        else:
            scoreInfo = scoreControlFlowTest(logLines, name)
        ret.append(scoreInfo)
    return ret

def getTestNumAndInfo(testName):
    testNum = testName[5:].upper().replace("_", "-")
    info = getSettingDict(VULCLASS, ["testsInfo", testName, "cweText"])
    return (testNum, info)

def scoreInj1Test(logLines, testName):
    testNum, info = getTestNumAndInfo(testName)

    if "<QEMU_NOT_IMPLEMENTED>" in logLines:
        score = SCORES.NOT_IMPLEMENTED
        info = "Not implemented on QEMU."
    elif "<BEGIN_INJECTION_TEST>" not in logLines:
        # Test did not run
        score = SCORES.FAIL
    elif "<INVALID>" in logLines or "<RETURNING>" not in logLines:
        score = SCORES.INVALID
    elif ("Segmentation fault" in logLines or
          "<END_INJECTION_TEST>" in logLines):
        # This is the expected result on unix, as the OS should detect the
        # attempt to execute from the stack and raise a segmentation fault.
        score = SCORES.NONE
    else:
        score = SCORES.HIGH

    return [f"TEST-{testNum}", adjustToCustomScore(logLines, score), info]

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
    elif "<BEGIN_INJECTION_TEST>" not in logLines:
        # Test did not run
        score = SCORES.FAIL
    elif "<INVALID>" in logLines:
        score = SCORES.INVALID
    elif "<EXECUTING_BENIGN_CODE>" in logLines:
        score = SCORES.NONE
    else:
        score = SCORES.HIGH

    return [f"TEST-{testNum}", adjustToCustomScore(logLines, score), info]
