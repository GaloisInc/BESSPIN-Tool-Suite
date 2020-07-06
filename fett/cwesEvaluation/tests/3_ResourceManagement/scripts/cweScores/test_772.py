from .helpers import *

def test_772 (SCORES, customScorer, logTest,testsDir):
    testNum = 772
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        part1A1 = partitionLines(testLines,"<Function A1>", "<Function B>",testNum=testNum)
        part1B = partitionLines(testLines,"<Function B>", "<Function A2>",testNum=testNum)
        part1A2 = partitionLines(testLines,"<Function A2>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"INVALID")): 
            partsScores[1] = SCORES.CALL_ERR
        elif (not doesKeywordExist(part1A1,"<FILE-OPENED>")):
            partsScores[1] = SCORES.DOS
        elif (not doesKeywordExist(part1B,"<LIMIT-REACHED>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(part1A2,"<DOS-ACHIEVED>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part1A2,"<FILE-OPENED>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

    #elif (osImage == 'FreeBSD'):
       # return overallScore (SCORES, [],testNum)

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines, nParts, testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<LEAKED_BLOCK>")):
            partsScores[1] = SCORES.V_HIGH

        else:
            partsScores[1] = SCORES.FAIL
        if (doesKeywordExist(partsLines[2],"<EVERY_ALLOCATION_EXCEPT_THE_LAST_IS_LOST>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.FAIL

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)