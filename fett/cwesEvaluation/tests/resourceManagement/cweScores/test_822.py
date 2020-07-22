from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_822 (SCORES, customScorer, logTest,testsDir):
    testNum = 822
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest, testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 2
        partsLines = {}
        partsScores = {}
        partsLines[1] = partitionLines(testLines,"<do_regular_compare>", "<do_malicious_modification>",testNum=testNum)
        partsLines[2] = partitionLines(testLines,"<do_malicious_modification>", "-"*50, testNum=testNum)

        if (doesKeywordExist(partsLines[1], "<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[1], "<EXECUTING_BENIGN_CODE>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        if (doesKeywordExist(partsLines[2], "<INVALID>")):
            partsScores[2] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[2],"<EXECUTING_MALICIOUS_CODE>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.FAIL


    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines, nParts, testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1], "<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[1], "<EXECUTING_BENIGN_CODE>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        if (doesKeywordExist(partsLines[2], "<INVALID>")):
            partsScores[2] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[2], "<EXECUTING_MALICIOUS_CODE>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.FAIL


    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [], testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores , testNum)