from fett.cwesEvaluation.resourceManagement.customCweScores.helpers import *

def test_822 (logLines):
    testNum = 822

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
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([], testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores , testNum)