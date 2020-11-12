from fett.cwesEvaluation.resourceManagement.cweScores.helpers import *

def test_771 (logTest,testsDir):
    testNum = 771
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        return overallScore ([],testNum)

    elif (osImage == 'FreeRTOS'):
        nParts = 5
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<F_MALLOC_SUCCEEDED>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.NONE
        if (doesKeywordExist(partsLines[2],"<POINTER_IS_NULL>")):
            partsScores[2] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[2],"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.HIGH

        if (doesKeywordExist(partsLines[3],"<POINTER_IS_NULL>")):
            partsScores[3] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[3],"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[3] = SCORES.V_HIGH
        else:
            partsScores[3] = SCORES.HIGH

        if (doesKeywordExist(partsLines[4],"<POINTER_IS_NULL>")):
            partsScores[4] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[4],"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[4] = SCORES.V_HIGH
        else:
            partsScores[4] = SCORES.HIGH

        if (doesKeywordExist(partsLines[5],"<POINTER_IS_NULL>")):
            partsScores[5] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[5],"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[5] = SCORES.V_HIGH
        else:
            partsScores[5] = SCORES.HIGH

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)