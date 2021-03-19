from besspin.cwesEvaluation.resourceManagement.customCweScores.helpers import *

def test_825 (logLines):
    testNum = 825

    osImage = getOsImage(logLines,testNum=testNum)
    nParts = 3

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        partsLines = regPartitionTest (logLines,nParts,testNum=testNum)
    elif (osImage == 'FreeRTOS'):
        partsLines = regPartitionTestFreeRTOS(logLines,nParts,testNum=testNum)
    else:
        errorAndLog(f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    partsScores = {}

    for iPart in range(1,nParts+1):
        if (doesKeywordExist(partsLines[iPart],"<INVALID>")):
            partsScores[iPart] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[iPart],'<POINTER_USED_IMPROPERLY>')):
            partsScores[iPart] = SCORES.HIGH
        elif (doesKeywordExist(partsLines[iPart],'Segmentation fault') or
              doesKeywordExist(partsLines[iPart],'Aborted') or
              doesKeywordExist(partsLines[iPart],'<GDB-SIGTRAP>')):
            partsScores[iPart] = SCORES.NONE
        else:
            partsScores[iPart] = SCORES.FAIL

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)
