from fett.base.utils.misc import *
from fett.cwesEvaluation.multipartLogHelpers import *

def scoreControlFlowTest(logLines, testNum):
    """
    This scoring function works for all tests that use injection to modify the
    control flow of the test program.  Tests should print
    "<EXECUTING_BENIGN_CODE>" when control flow is not maliciously modified,
    and "<EXECUTING_MALICIOUS_CODE>" when control flow is maliciously modified.
    """
    osImage = getOsImage(logLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 2
        partsLines = regPartitionTest (logLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1], "<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[1], "<EXECUTING_BENIGN_CODE>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        if (doesKeywordExist(partsLines[2], "<INVALID>")):
            partsScores[2] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[2],"<EXECUTING_MALICIOUS_CODE>")):
            partsScores[2] = SCORES.HIGH
        else:
            partsScores[2] = SCORES.FAIL


    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(logLines, nParts, testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1], "<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[1], "<EXECUTING_BENIGN_CODE>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        if (doesKeywordExist(partsLines[2], "<INVALID>")):
            partsScores[2] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[2], "<EXECUTING_MALICIOUS_CODE>")):
            partsScores[2] = SCORES.HIGH
        else:
            partsScores[2] = SCORES.FAIL


    else:
        errorAndLog(f"scoreControlFlowTest: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([], testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores , testNum)
