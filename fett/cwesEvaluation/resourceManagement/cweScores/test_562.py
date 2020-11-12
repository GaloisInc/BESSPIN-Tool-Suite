from fett.cwesEvaluation.resourceManagement.cweScores.helpers import *

def test_562 (logTest, testsDir):
    testNum = 562
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest, testsDir)

    osImage = getOsImage(testLines, testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 2
        partsLines = regPartitionTest (testLines, nParts, testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[1],'<VALID_ARRAY_CONTENT>')):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[1],'<NOT_VALID_ARRAY_CONTENT>') or doesKeywordExist(partsLines[1],'Segmentation fault')):
            partsScores[1] = SCORES.HIGH
        else:
            partsScores[1] = SCORES.FAIL

        if (doesKeywordExist(partsLines[2],"<INVALID>") or 
            doesKeywordExist(partsLines[2],'Segmentation fault') or
            doesKeywordExist(partsLines[2],'<NOT_VALID_ARRAY_CONTENT>')):
            partsScores[2] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[2],'<VALID_ARRAY_CONTENT>')):
            partsScores[2] = SCORES.NONE
        else:
            partsScores[2] = SCORES.FAIL

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
        return overallScore ([], testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],
                                                   partsScores[iPart]) for iPart in range(1, nParts+1)]
    return overallScore (listScores, testNum)
