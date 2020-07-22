from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_562 (SCORES, customScorer, logTest, testsDir):
    testNum = 562
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest, testsDir)

    osImage = getOsImage(testLines, testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines, nParts, testNum=testNum)
        partsScores = {}

        part01 = partitionLines(testLines,"<fill_array>",
                                "<fill_array_with_malloc>",
                                testNum=testNum)
        part02 = partitionLines(testLines,"<fill_array_with_malloc>",
                                "-"*50, testNum=testNum)

        if (doesKeywordExist(testLines, "<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(part01, "<NOT_VALID_ARRAY_CONTENT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part01, "<ERROR-SEGFAULT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part01, "<DEREFERENCE-VIOLATION>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part02, "<VALID_ARRAY_CONTENT>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL


    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines, nParts, testNum=testNum)
        partsScores = {}

        if (not doesKeywordExist(partsLines[1], "<DEREFERENCE-VIOLATION>")):
            partsScores[1] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[2], "<GDB-SIGINT>")):
            partsScores[1] = SCORES.V_HIGH
        elif(not doesKeywordExist(partsLines[2], "<DEREFERENCE-VIOLATION>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.NONE
        if (not doesKeywordExist(partsLines[2], "<VALID_ARRAY_CONTENT>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.NONE

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [], testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],
                                                   partsScores[iPart]) for iPart in range(1, nParts+1)]
    return overallScore (SCORES, listScores, testNum)
