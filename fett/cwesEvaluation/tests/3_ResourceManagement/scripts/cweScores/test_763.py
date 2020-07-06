from .helpers import *

def test_763 (SCORES, customScorer, logTest,testsDir):
    testNum = 763
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        part01 = partitionLines(testLines,"<wrong_shift_address_assignment>", "<wrong_address_assignment>",testNum=testNum)
        part02 = partitionLines(testLines,"<wrong_address_assignment>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(part01,"<ERROR-SIGABRT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part01,"<RELEASE_OF_INVALID_POINTER_ERROR>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part02,"<ERROR-SIGABRT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part02,"<RELEASE_OF_INVALID_POINTER_ERROR>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL


    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<RELEASE_OF_INVALID_POINTER_PASSED_SUCCESSFULLY>")):
            partsScores[1] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[1],"<GDB-SIGTRAP>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.HIGH
        if (doesKeywordExist(partsLines[2],"<RELEASE_OF_INVALID_POINTER_PASSED_SUCCESSFULLY>")):
            partsScores[2] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[2],"<GDB-SIGTRAP>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.HIGH

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)