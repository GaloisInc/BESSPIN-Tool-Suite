from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_825 (SCORES, customScorer, logTest,testsDir):
    testNum = 825
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        partDoubleFree = partitionLines(testLines,"<test-double-free>", "<test-free-no-longer-valid>",testNum=testNum)
        partNoLongerValid = partitionLines(testLines,"<test-free-no-longer-valid>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (not doesKeywordExist(partDoubleFree,"<REGULAR_PASSED>")):
            partsScores[1] = SCORES.FAIL
        elif (doesKeywordExist(partNoLongerValid,"<ERROR-SEGFAULT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(partNoLongerValid,"<POINTER_USED_IMPROPERLY>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL


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
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)