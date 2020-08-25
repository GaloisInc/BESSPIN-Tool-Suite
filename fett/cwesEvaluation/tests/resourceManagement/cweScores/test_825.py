from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_825 (logTest,testsDir):
    testNum = 825
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 2
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        for iPart in range(1,nParts+1):
            if (doesKeywordExist(partsLines[iPart],"<INVALID>")):
                partsScores[iPart] = SCORES.CALL_ERR
            elif (doesKeywordExist(partsLines[iPart],'<POINTER_USED_IMPROPERLY>')):
                partsScores[iPart] = SCORES.V_HIGH
            elif (doesKeywordExist(partsLines[iPart],'Segmentation fault') or doesKeywordExist(partsLines[iPart],'Aborted')):
                partsScores[iPart] = SCORES.HIGH
            elif (doesKeywordExist(partsLines[iPart],'<REGULAR_PASSED>')):
                partsScores[iPart] = SCORES.HIGH
            else:
                partsScores[iPart] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<REGULAR_PASSED>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.HIGH
        if (doesKeywordExist(partsLines[2],"<POINTER_USED_IMPROPERLY>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.HIGH

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)