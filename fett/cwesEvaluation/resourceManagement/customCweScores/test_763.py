from fett.cwesEvaluation.resourceManagement.customCweScores.helpers import *

def test_763 (logLines):
    testNum = 763

    osImage = getOsImage(logLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 2
        partsLines = regPartitionTest (logLines,nParts,testNum=testNum)
        partsScores = {}

        for iPart in range(1,nParts+1):
            if (doesKeywordExist(partsLines[iPart],"<INVALID>")):
                partsScores[iPart] = SCORES.CALL_ERR
            elif (doesKeywordExist(partsLines[iPart],'<RELEASE_OF_INVALID_POINTER_ERROR>')):
                partsScores[iPart] = SCORES.HIGH
            elif (doesKeywordExist(partsLines[iPart],'Segmentation fault') or doesKeywordExist(partsLines[iPart],'Abort')):
                partsScores[iPart] = SCORES.HIGH
            else:
                partsScores[iPart] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(logLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<RELEASE_OF_INVALID_POINTER_PASSED_SUCCESSFULLY>")):
            partsScores[1] = SCORES.HIGH
        elif(doesKeywordExist(partsLines[1],"<GDB-SIGTRAP>")):
            partsScores[1] = SCORES.HIGH
        else:
            partsScores[1] = SCORES.HIGH
        if (doesKeywordExist(partsLines[2],"<RELEASE_OF_INVALID_POINTER_PASSED_SUCCESSFULLY>")):
            partsScores[2] = SCORES.HIGH
        elif(doesKeywordExist(partsLines[2],"<GDB-SIGTRAP>")):
            partsScores[2] = SCORES.HIGH
        else:
            partsScores[2] = SCORES.HIGH

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)