from besspin.cwesEvaluation.resourceManagement.customCweScores.helpers import *

def test_761 (logLines):
    testNum = 761

    osImage = getOsImage(logLines,testNum=testNum)
    nParts = 2
    if (osImage == 'debian' or osImage == 'FreeBSD'):
        partsLines = regPartitionTest (logLines,nParts,testNum=testNum)
    elif (osImage == 'FreeRTOS'):
        partsLines = regPartitionTestFreeRTOS(logLines,nParts,testNum=testNum)
    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    partsScores = {}

    if (doesKeywordExist(partsLines[1],"<INVALID>")):
        partsScores[1] = SCORES.CALL_ERR
    elif (doesKeywordExist(partsLines[1],'<MATCHED_CHAR>')):
        partsScores[1] = SCORES.NONE
    else:
        partsScores[1] = SCORES.FAIL

    if (doesKeywordExist(partsLines[2],"<INVALID>")):
        partsScores[2] = SCORES.CALL_ERR
    elif (doesKeywordExist(partsLines[2],'<DEREFERENCE-VIOLATION>')):
        partsScores[2] = SCORES.HIGH
    elif (
            doesKeywordExist(partsLines[2],'Segmentation fault') or 
            doesKeywordExist(partsLines[2],'Abort') or
            doesKeywordExist(partsLines[2],'Aborted') or
            doesKeywordExist(partsLines[2],'<QEMU ABORTED>') or
            doesKeywordExist(partsLines[2],'<GDB-SIGTRAP>')
        ):
        partsScores[2] = SCORES.HIGH
    else:
        partsScores[2] = SCORES.FAIL

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)
