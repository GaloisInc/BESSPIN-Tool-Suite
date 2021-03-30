from besspin.cwesEvaluation.resourceManagement.customCweScores.helpers import *

def test_562 (logLines):
    testNum = 562
    nParts = 2

    osImage = getOsImage(logLines, testNum=testNum)
    if (osImage == 'debian' or osImage == 'FreeBSD'):
        partsLines = regPartitionTest (logLines, nParts, testNum=testNum)
    elif (osImage == 'FreeRTOS'):
        partsLines = regPartitionTestFreeRTOS(logLines, nParts, testNum=testNum)
    else:
        errorAndLog(f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([], testNum)

    partsScores = {}
    if (doesKeywordExist(partsLines[1],"<INVALID>")):
        partsScores[1] = SCORES.INVALID
    elif (doesKeywordExist(partsLines[1],'<DEREFERENCE_VIOLATION>')):
        partsScores[1] = SCORES.HIGH
    elif (doesKeywordExist(partsLines[1],'<BEGIN_STACK_TEST>')):
        partsScores[1] = SCORES.NONE
    else:
        # Test didn't run
        partsScores[1] = SCORES.FAIL

    if (doesKeywordExist(partsLines[2],"<INVALID>")):
        partsScores[2] = SCORES.INVALID
    elif (doesKeywordExist(partsLines[2],'<VALID_ARRAY_CONTENT>')):
        partsScores[2] = SCORES.NONE
    else:
        partsScores[2] = SCORES.FAIL

    listScores = [adjustToCustomScore(partsLines[iPart],
                                      partsScores[iPart]) for iPart in range(1, nParts+1)]
    return overallScore (listScores, testNum)
