from .helpers import *

def test_911 (SCORES, customScorer, logTest, testsDir):
    testNum = 911
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest, testsDir)

    osImage = getOsImage(testLines, testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest(testLines, nParts, testNum=testNum)
        partsScores = {}
        part01 = partitionLines(testLines,"<correct_implicit_reference_count>", "<unknown_reference_count>", testNum=testNum)
        part02 = partitionLines(testLines,"<unknown_reference_count>", "-"*50, testNum=testNum)

        if (doesKeywordExist(testLines, "INVALID")):
            partsScores[1] = SCORES.CALL_ERR
        elif (not doesKeywordExist(part01, "<REFERENCE_COUNTER_DECREASED_BY_ONE_FIRST_TIME>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part01, "<REFERENCE_COUNTER_DECREASED_BY_ONE_SECOND_TIME>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part02, "<UNKNOWN_REFERENCE_COUNTER_AFTER_CHUNK_FREE>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part02, "<UNKNOWN_REFERENCE_COUNTER_AFTER_UNION_DATA_SET_TO_ONE>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1], "<REFERENCE_COUNTER_DECREASED_BY_ONE_FIRST_TIME>")):
            partsScores[1] = SCORES.NONE
        elif (doesKeywordExist(partsLines[1], "<REFERENCE_COUNTER_DECREASED_BY_ONE_SECOND_TIME>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        if (doesKeywordExist(partsLines[2], "<UNKNOWN_REFERENCE_COUNTER_AFTER_CHUNK_FREE>")):
            partsScores[2] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[2], "<UNKNOWN_REFERENCE_COUNTER_AFTER_UNION_DATA_SET_TO_ONE>")):
            partsScores[2] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[2], "<GDB-SIGINT>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.FAIL

    else:
        print(f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)