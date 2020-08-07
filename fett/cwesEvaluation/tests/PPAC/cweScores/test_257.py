from fett.base.utils.misc import *
from fett.cwesEvaluation.tests.PPAC.cweScores.helpers import *

def test_257(logTest,testsDir):
    testNum = 257
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)
    if (osImage in ['debian', 'FreeBSD']):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        # Plaintext stored
        partsScores[1] = scoreGrantedDenied (SCORES, partsLines[1])
        if partsScores[1] not in [SCORES.FAIL, SCORES.CALL_ERR]:
            if partsScores[1]:
                partsScores[1] = SCORES.V_HIGH
            else:
                partsScores[1] = SCORES.NONE

    elif (osImage == 'FreeRTOS'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #Part01: sha256 hashes stored.
        partsScores[1] = scoreGrantedDenied (SCORES, partsLines[1],lastGranted=True)
        if ((partsScores[1] != SCORES.FAIL) and (partsScores[1] != SCORES.CALL_ERR)): #it's true or false
            if (not doesKeywordExist(partsLines[1], '<HOST-RECV-0>:DENIED')):
                partsScores[1] = SCORES.CALL_ERR
            elif (not doesKeywordExist(partsLines[1], '<HOST-RECV-1>')):
                partsScores[1] = SCORES.CALL_ERR
            elif (not partsScores[1]): #if not granted
                partsScores[1] = SCORES.DOS
            else:
                partsScores[1] = SCORES.NONE

        #Part02: base64 passwords stored.
        partsScores[2] = scoreGrantedDenied (SCORES, partsLines[2],lastGranted=True)
        if ((partsScores[2] != SCORES.FAIL) and (partsScores[2] != SCORES.CALL_ERR)): #it's true or false
            if (not doesKeywordExist(partsLines[2], '<HOST-RECV-0>:DENIED')):
                partsScores[2] = SCORES.CALL_ERR
            elif (not doesKeywordExist(partsLines[2], '<HOST-RECV-1>')):
                partsScores[2] = SCORES.CALL_ERR
            elif (partsScores[2]): #granted
                partsScores[2] = SCORES.V_HIGH
            else:
                partsScores[2] = SCORES.NONE

        #Part03: plaintext stored.
        partsScores[3] = scoreGrantedDenied (SCORES, partsLines[3],lastGranted=True)
        if ((partsScores[3] != SCORES.FAIL) and (partsScores[3] != SCORES.CALL_ERR)): #it's true or false
            if (not doesKeywordExist(partsLines[3], '<HOST-RECV-0>:DENIED')):
                partsScores[3] = SCORES.CALL_ERR
            elif (not doesKeywordExist(partsLines[3], '<HOST-RECV-1>')):
                partsScores[3] = SCORES.CALL_ERR
            elif (partsScores[3]): #granted
                partsScores[3] = SCORES.V_HIGH
            else:
                partsScores[3] = SCORES.NONE

    else:
        errorAndLog (f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)
