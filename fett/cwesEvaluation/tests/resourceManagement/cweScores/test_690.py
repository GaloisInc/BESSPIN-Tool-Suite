from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_690 (logTest,testsDir):
    testNum = 690
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        part01 = partitionLines(testLines,"<test regular>", "<test malicious>",testNum=testNum)
        part02 = partitionLines(testLines,"<test malicious>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (not doesKeywordExist(part01,"<REGULAR_PASSED>")):
            partsScores[1] = SCORES.INVALID
        elif (doesKeywordExist(part02,"<ERROR-SEGFAULT>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part02,"<DEREFERENCE_VIOLATION_PASSED_SUCCESSFULLY>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL


    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<REGULAR_PASSED>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL
        if (doesKeywordExist(partsLines[2],"<DEREFERENCE_VIOLATION_PASSED_SUCCESSFULLY>") or doesKeywordExist(partsLines[2],"<GDB-SIGINT>")):
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