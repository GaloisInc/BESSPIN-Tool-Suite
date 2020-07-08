from .helpers import *

def test_761 (SCORES, customScorer, logTest,testsDir):
    testNum = 761
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        part01 = partitionLines(testLines,"<contains_char_valid_success>", "<contains_char_valid_failure>",testNum=testNum)
        part02 = partitionLines(testLines,"<contains_char_valid_failure>", "<contains_char_malicious_success>",testNum=testNum)
        part03 = partitionLines(testLines,"<contains_char_malicious_success>", "<contains_char_malicious_failure>",testNum=testNum)
        part04 = partitionLines(testLines,"<contains_char_malicious_failure>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (not doesKeywordExist(part01,"<MATCHED_CHAR>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part02,"<VALID_RETURN_FAILURE>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part03,"<MATCHED_CHAR>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part04,"<ERROR-SEGFAULT>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 4
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (not doesKeywordExist(partsLines[1],"<MATCHED_CHAR>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.NONE
        if (doesKeywordExist(partsLines[2],"<VALID_RETURN_FAILURE>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.HIGH

        if (not doesKeywordExist(partsLines[3],"<MATCHED_CHAR>")):
            partsScores[3] = SCORES.V_HIGH
        else:
            partsScores[3] = SCORES.NONE

        if (doesKeywordExist(partsLines[4],"<DEREFERENCE_VIOLATION_PASSED_SUCCESSFULLY>")):
            partsScores[4] = SCORES.V_HIGH
        else:
            partsScores[4] = SCORES.HIGH

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)