from fett.base.utils.misc import *
from fett.cwesEvaluation.tests.PPAC.cweScores.helpers import *

def test_290(logTest,testsDir):
    testNum = 290
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)
    if (osImage in ['debian','FreeBSD']):
        return overallScore ([],testNum,msgIfNotImplemented="Covered by TEST-294")

    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #Part01: Baseline sanity check. No spoofing.
        partsScores[1] = scoreGrantedDenied (SCORES, partsLines[1])
        if ((partsScores[1] != SCORES.FAIL) and (partsScores[1] != SCORES.CALL_ERR)): #it's true or false
            if (not doesKeywordExist(partsLines[1], 'JEDI CLNT:<TARGET-RECV>')):
                partsScores[1] = SCORES.CALL_ERR
            elif (partsScores[1]):
                partsScores[1] = SCORES.MED
            else:
                partsScores[1] = SCORES.NONE

        #Part02: Don't authorize the IP. Try to spoof it.
        partsScores[2] = scoreGrantedDenied (SCORES, partsLines[2])
        if ((partsScores[2] != SCORES.FAIL) and (partsScores[2] != SCORES.CALL_ERR)): #it's true or false
            if (not doesKeywordExist(partsLines[2], 'SSITH LORD:<TARGET-RECV>')):
                partsScores[2] = SCORES.CALL_ERR
            elif (partsScores[2]):
                partsScores[2] = SCORES.V_HIGH
            else:
                partsScores[2] = SCORES.NONE

    else:
        errorAndLog (f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)
