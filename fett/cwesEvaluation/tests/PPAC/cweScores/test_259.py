from .helpers import *

def test_259 (SCORES, customScorer, logTest,testsDir):
    testNum = 259
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)
    if (osImage in ['debian','FreeBSD']):
        return overallScore (SCORES, [],testNum,msgIfNotImplemented="Covered by TEST-257")

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #Part01: Inbound Test
        if (doesKeywordExist(partsLines[1],'<INVALID>')):
            partsScores[1] = SCORES.CALL_ERR
        elif (not doesKeywordExist(partsLines[1], '<HOST-RECV-0>:')) or (not doesKeywordExist(partsLines[1], '<HOST-RECV-1>:')):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[1],'<GRANTED-ADMIN>')):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[1],'<GRANTED-USER>')):
            partsScores[1] = SCORES.MED
        elif (doesKeywordExist(partsLines[1],'<DENIED>') and doesKeywordExist(partsLines[1],'<HOST-RECV-0>:DENIED') and doesKeywordExist(partsLines[1],'<HOST-RECV-1>:DENIED')):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.FAIL

        #Part02: Outbound Test
        if (doesKeywordExist(partsLines[2],'<INVALID>')):
            partsScores[2] = SCORES.CALL_ERR
        elif (not doesKeywordExist(partsLines[2], '<HOST-RECV>:')):
            partsScores[2] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[2],'<HOST-RECV>:Jedi Order CLNT/joy@Work_1999')):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.NONE

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)