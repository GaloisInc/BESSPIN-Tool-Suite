from .helpers import *

def test_762 (SCORES, customScorer, logTest,testsDir):
    testNum = 762
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        part01 = partitionLines(testLines,"<correct_memory_free>", "<wrong_memory_free>",testNum=testNum)
        part02 = partitionLines(testLines,"<wrong_memory_free>", "<array_allocated_globally>",testNum=testNum)
        part03 = partitionLines(testLines,"<array_allocated_globally>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (not doesKeywordExist(part01,"<MEMORY_FREE_CORRECTLY>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part02,"<ERROR-SIGABRT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part02,"<INVALID_FREE_OF_STACK>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part03,"<ERROR-SIGABRT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part03,"<INVALID_FREE_OF_MEMORY>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL


    elif (osImage == 'FreeRTOS'):
        nParts = 3
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (not doesKeywordExist(partsLines[1],"<MEMORY_FREE_CORRECTLY>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.NONE
        if (doesKeywordExist(partsLines[2],"<INVALID_FREE_OF_STACK>")):
            partsScores[2] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[2],"<GDB-SIGTRAP>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.HIGH

        if (doesKeywordExist(partsLines[3],"<INVALID_FREE_OF_MEMORY>")):
            partsScores[3] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[3],"<GDB-SIGTRAP>")):
            partsScores[3] = SCORES.V_HIGH
        else:
            partsScores[3] = SCORES.HIGH

    else:
        print(f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)