from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_395 (logTest,testsDir):
    testNum = 395
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        partMalRead = partitionLines(testLines,"<try-catch-read>", "<try-catch-write>",testNum=testNum)
        partMalWrite = partitionLines(testLines,"<try-catch-write>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partMalRead,"<ERROR-SEGFAULT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(partMalRead,"<DEREFERENCE-VIOLATION>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(partMalWrite,"<ERROR-SEGFAULT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(partMalWrite,"<DEREFERENCE-VIOLATION>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<DEREFERENCE-VIOLATION_PASSED_SUCCESSFULLY>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[1],"<TIMEOUT>")): #timeout with no trapping
            partsScores[1] = SCORES.HIGH
        else:
            partsScores[1] = SCORES.FAIL
        if (doesKeywordExist(partsLines[2],"<DEREFERENCE-VIOLATION_PASSED_SUCCESSFULLY>")):
            partsScores[2] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[2],"<TIMEOUT>")): #timeout with no trapping
            partsScores[2] = SCORES.HIGH
        else:
            partsScores[2] = SCORES.FAIL

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)