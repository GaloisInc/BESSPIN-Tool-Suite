from .helpers import *

def test_290(SCORES, customScorer, logTest,testsDir):
    testNum = 290
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)
    if (osImage in ['debian','FreeBSD']):
        return overallScore (SCORES, [],testNum,msgIfNotImplemented="Covered by TEST-294")

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #Part01: Baseline sanity check. No spoofing.
        partsScores[1] = scoreGrantedDenied (SCORES, partsLines[1])
        if ((partsScores[1] != SCORES.FAIL) and (partsScores[1] != SCORES.CALL_ERR)): #it's true or false
            if (not doesKeywordExist(partsLines[1], '<TARGET-RECV>:JEDI CLNT')):
                partsScores[1] = SCORES.CALL_ERR
            elif (partsScores[1]):
                partsScores[1] = SCORES.MED
            else:
                partsScores[1] = SCORES.NONE

        #Part02: Don't authorize the IP. Try to spoof it.
        partsScores[2] = scoreGrantedDenied (SCORES, partsLines[2])
        if ((partsScores[2] != SCORES.FAIL) and (partsScores[2] != SCORES.CALL_ERR)): #it's true or false
            if (not doesKeywordExist(partsLines[2], '<TARGET-RECV>:SSITH LORD')):
                partsScores[2] = SCORES.CALL_ERR
            elif (partsScores[2]):
                partsScores[2] = SCORES.V_HIGH
            else:
                partsScores[2] = SCORES.NONE

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)