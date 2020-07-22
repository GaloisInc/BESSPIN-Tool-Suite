from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_468 (SCORES, customScorer, logTest,testsDir):
    testNum = 468
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        part01 = partitionLines(testLines,"<example-good-scaled>", "<example-bad-scaled>",testNum=testNum)
        part02 = partitionLines(testLines,"<example-bad-scaled>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (not doesKeywordExist(part01,"<CORRECT_SCALED>")):
            partsScores[1] = SCORES.INVALID
        elif (doesKeywordExist(part02,"<WRONG_OFFSET>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<CORRECT_SCALED>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL
        if (doesKeywordExist(partsLines[2],"<WRONG_OFFSET>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.FAIL


    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)