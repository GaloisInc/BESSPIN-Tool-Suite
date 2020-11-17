from fett.base.utils.misc import *
from fett.cwesEvaluation.PPAC.cweScores.helpers import *

def test_521 (logTest,testsDir):
    testNum = 521
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)
    
    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage in ['debian', 'FreeBSD']):
        nParts = 4
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #Part01: short username
        partsScores[1] = scoreGrantedDenied (SCORES, partsLines[1])
        if ((partsScores[1] != SCORES.FAIL) and (partsScores[1] != SCORES.CALL_ERR)):
            if (partsScores[1]):
                partsScores[1] = SCORES.V_HIGH
            else:
                partsScores[1] = SCORES.NONE

        #Part02: No special characters
        partsScores[2] = scoreGrantedDenied (SCORES, partsLines[2])
        if ((partsScores[2] != SCORES.FAIL) and (partsScores[2] != SCORES.CALL_ERR)):
            if (partsScores[2]):
                partsScores[2] = SCORES.V_HIGH
            else:
                partsScores[2] = SCORES.NONE

        #Part03: First phase of reuse -- this should succeed
        partsScores[3] = scoreGrantedDenied (SCORES, partsLines[3])
        if ((partsScores[3] != SCORES.FAIL) and (partsScores[3] != SCORES.CALL_ERR)):
            if (partsScores[3]):
                partsScores[3] = SCORES.NONE
            else:
                partsScores[3] = SCORES.DOS

        #Part04: Second phase of reuse -- this should fail
        partsScores[4] = scoreGrantedDenied (SCORES, partsLines[4])
        if ((partsScores[4] != SCORES.FAIL) and (partsScores[4] != SCORES.CALL_ERR)):
            if (partsScores[4]):
                partsScores[4] = SCORES.V_HIGH
            else:
                partsScores[4] = SCORES.NONE

    elif (osImage == 'FreeRTOS'):
        return overallScore ([],testNum,msgIfNotImplemented="Not Applicable To FreeRTOS")

    else:
        errorAndLog (f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)
