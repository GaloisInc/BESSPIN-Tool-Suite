from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *
import time

def test_476 (logTest,testsDir):
    testNum = 476
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)
    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        for iPart in range(1,nParts+1):
            if (doesKeywordExist(partsLines[iPart],"<INVALID>")):
                partsScores[iPart] = SCORES.CALL_ERR
            elif (doesKeywordExist(partsLines[iPart],'<DEREFERENCE-VIOLATION>')):
                partsScores[iPart] = SCORES.V_HIGH
            elif (doesKeywordExist(partsLines[iPart],'Segmentation fault')):
                partsScores[iPart] = SCORES.HIGH
            elif (doesKeywordExist(partsLines[iPart],'<REGULAR>') and (iPart==1)):
                partsScores[iPart] = SCORES.NONE
            else:
                partsScores[iPart] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<DEREFERENCE-VIOLATION_PASSED_SUCCESSFULLY>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[1],"<TIMEOUT>")): #timeout with no trapping
            partsScores[1] = SCORES.HIGH
        else:
            partsScores[1] = SCORES.FAIL
        if (doesKeywordExist(partsLines[2],"<DEREFERENCE-VIOLATION_PASSED_SUCCESSFULLY>")):
            partsScores[2] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[2],"<TIMEOUT>")): #timeout with no trapping
            partsScores[2] = SCORES.HIGH
        else:
            partsScores[2] = SCORES.FAIL

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)