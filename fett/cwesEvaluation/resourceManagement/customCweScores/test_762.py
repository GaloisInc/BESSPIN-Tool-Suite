from fett.cwesEvaluation.resourceManagement.customCweScores.helpers import *

def test_762 (logLines):
    testNum = 762

    osImage = getOsImage(logLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 3
        partsLines = regPartitionTest (logLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[1],'<MEMORY_FREE_CORRECTLY>')):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        for iPart in range(2,nParts+1):
            if (doesKeywordExist(partsLines[iPart],"<INVALID>")):
                partsScores[iPart] = SCORES.CALL_ERR
            elif (doesKeywordExist(partsLines[iPart],'<INVALID_FREE_OF_')):
                partsScores[iPart] = SCORES.HIGH
            elif (doesKeywordExist(partsLines[iPart],'Segmentation fault') or 
                    doesKeywordExist(partsLines[iPart],'Abort') or
                    doesKeywordExist(partsLines[iPart],'Aborted') or
                    doesKeywordExist(partsLines[iPart],'Abort trap') ):
                partsScores[iPart] = SCORES.HIGH
            else:
                partsScores[iPart] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 3
        partsLines = regPartitionTestFreeRTOS(logLines,nParts,testNum=testNum)
        partsScores = {}

        if (not doesKeywordExist(partsLines[1],"<MEMORY_FREE_CORRECTLY>")):
            partsScores[1] = SCORES.HIGH
        else:
            partsScores[1] = SCORES.NONE
        if (doesKeywordExist(partsLines[2],"<INVALID_FREE_OF_STACK>")):
            partsScores[2] = SCORES.HIGH
        elif(doesKeywordExist(partsLines[2],"<GDB-SIGTRAP>")):
            partsScores[2] = SCORES.HIGH
        else:
            partsScores[2] = SCORES.HIGH

        if (doesKeywordExist(partsLines[3],"<INVALID_FREE_OF_MEMORY>")):
            partsScores[3] = SCORES.HIGH
        elif(doesKeywordExist(partsLines[3],"<GDB-SIGTRAP>")):
            partsScores[3] = SCORES.HIGH
        else:
            partsScores[3] = SCORES.HIGH

    else:
        print(f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)