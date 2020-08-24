from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_761 (logTest,testsDir):
    testNum = 761
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 4
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[1],'<MATCHED_CHAR>')):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        if (doesKeywordExist(partsLines[2],"<INVALID>")):
            partsScores[2] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[2],'<VALID_RETURN_FAILURE>')):
            partsScores[2] = SCORES.NONE
        else:
            partsScores[2] = SCORES.FAIL

        if (doesKeywordExist(partsLines[3],"<INVALID>")):
            partsScores[3] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[3],'<MATCHED_CHAR>') or doesKeywordExist(partsLines[3],'<DEREFERENCE-VIOLATION>')):
            partsScores[3] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[3],'Segmentation fault') or doesKeywordExist(partsLines[3],'Aborted')):
            partsScores[3] = SCORES.HIGH
        else:
            partsScores[3] = SCORES.FAIL

        if (doesKeywordExist(partsLines[4],"<INVALID>")):
            partsScores[4] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[4],'<DEREFERENCE-VIOLATION>')):
            partsScores[4] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[4],'Segmentation fault') or doesKeywordExist(partsLines[4],'Aborted')):
            partsScores[4] = SCORES.HIGH
        else:
            partsScores[4] = SCORES.FAIL

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
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)