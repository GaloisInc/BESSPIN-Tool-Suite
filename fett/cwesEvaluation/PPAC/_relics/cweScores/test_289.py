from fett.base.utils.misc import *
from fett.cwesEvaluation.PPAC.cweScores.helpers import *

def test_289 (logTest,testsDir):
    testNum = 289
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)
    
    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #Part01: Use a fake username. Attempt to authenticate
        partsScores[1] = scoreGrantedDenied (SCORES, partsLines[1])
        if ((partsScores[1] != SCORES.FAIL) and (partsScores[1] != SCORES.CALL_ERR)):
            if (partsScores[1]):
                partsScores[1] = SCORES.V_LOW
            else:
                partsScores[1] = SCORES.NONE

        #Part02: Rename username. Attempt to authenticate
        partsScores[2] = scoreGrantedDenied (SCORES, partsLines[2])
        if ((partsScores[2] != SCORES.FAIL) and (partsScores[2] != SCORES.CALL_ERR)):
            if (partsScores[2]):
                partsScores[2] = SCORES.V_HIGH
            else:
                partsScores[2] = SCORES.NONE

        if osImage == 'debian':
            #Part03: Change the bash. Attempt to authenticate
            partsScores[3] = scoreGrantedDenied (SCORES, partsLines[3])
            if ((partsScores[3] != SCORES.FAIL) and (partsScores[3] != SCORES.CALL_ERR)):
                if (partsScores[3]):
                    partsScores[3] = SCORES.V_HIGH
                else:
                    partsScores[3] = SCORES.NONE

    elif (osImage == 'FreeBSD'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #Part01: Sanity Check. FAIL if not granted.
        partsScores[1] = scoreGrantedDenied (SCORES, partsLines[1])
        if ((partsScores[1] != SCORES.FAIL) and (partsScores[1] != SCORES.CALL_ERR)):
            if (partsScores[1]):
                partsScores[1] = SCORES.FAIL
            else:
                partsScores[1] = SCORES.NONE

        #Part02: Block a fake group. MED if granted.
        partsScores[2] = scoreGrantedDenied (SCORES, partsLines[2])
        if ((partsScores[2] != SCORES.FAIL) and (partsScores[2] != SCORES.CALL_ERR)):
            if (partsScores[2]):
                partsScores[2] = SCORES.MED
            else:
                partsScores[2] = SCORES.NONE

        #Part03: Block a real group, but rename it.
        partsScores[3] = scoreGrantedDenied (SCORES, partsLines[3])
        if ((partsScores[3] != SCORES.FAIL) and (partsScores[3] != SCORES.CALL_ERR)):
            if (partsScores[3]):
                partsScores[3] = SCORES.V_HIGH
            else:
                partsScores[3] = SCORES.NONE

    elif (osImage == 'FreeRTOS'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}
        
        #part01: Valid permissions. Do not list the username or the task.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[1]), SendRecvCheck(partsLines[1],testNum=testNum)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[1] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): # granted
            partsScores[1] = SCORES.V_LOW
        else:
            partsScores[1] = SCORES.NONE

        #part02: List the username. Use a different capitalization username.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[2]), SendRecvCheck(partsLines[2],testNum=testNum)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[2] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[2] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #granted
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.NONE

            
        #part03: List the task name. Create a child task.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[3]), SendRecvCheck(partsLines[3],testNum=testNum)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[3] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[3] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #granted
            partsScores[3] = SCORES.V_HIGH
        else:
            partsScores[3] = SCORES.NONE

    else:
        errorAndLog (f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)
