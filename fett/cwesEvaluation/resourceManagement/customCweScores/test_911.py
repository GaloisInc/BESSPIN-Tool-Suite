from fett.cwesEvaluation.multipartLogHelpers import *

def test_911 (logLines):
    testNum = 911

    osImage = getOsImage(logLines, testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 2
        partsLines = regPartitionTest(logLines, nParts, testNum=testNum)
        partsScores = {}
        
        if (doesKeywordExist(partsLines[1], "INVALID")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[1], "<REFERENCE_COUNTER_DECREASED_BY_ONE_FIRST_TIME>") and 
            doesKeywordExist(partsLines[1], "<REFERENCE_COUNTER_DECREASED_BY_ONE_SECOND_TIME>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        if (doesKeywordExist(partsLines[2], "INVALID")):
            partsScores[2] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[2], "<UNKNOWN_REFERENCE_COUNTER_AFTER_CHUNK_FREE>") or
            doesKeywordExist(partsLines[2], "<UNKNOWN_REFERENCE_COUNTER_AFTER_UNION_DATA_SET_TO_ONE>")):
            partsScores[2] = SCORES.HIGH
        elif (doesKeywordExist(partsLines[2],'Segmentation fault') or doesKeywordExist(partsLines[2],'Aborted')):
            partsScores[2] = SCORES.HIGH
        else:
            partsScores[2] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(logLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1], "<REFERENCE_COUNTER_DECREASED_BY_ONE_FIRST_TIME>") and 
            doesKeywordExist(partsLines[1], "<REFERENCE_COUNTER_DECREASED_BY_ONE_SECOND_TIME>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        if (doesKeywordExist(partsLines[2], "<UNKNOWN_REFERENCE_COUNTER_AFTER_CHUNK_FREE>") or
            doesKeywordExist(partsLines[2], "<UNKNOWN_REFERENCE_COUNTER_AFTER_UNION_DATA_SET_TO_ONE>")):
            partsScores[2] = SCORES.HIGH
        elif (doesKeywordExist(partsLines[2], "<GDB-SIGINT>") or doesKeywordExist(partsLines[2],"<TIMEOUT>")):
            partsScores[2] = SCORES.HIGH
        else:
            partsScores[2] = SCORES.FAIL

    else:
        print(f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)