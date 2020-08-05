from .helpers import *

def test_288(SCORES, customScorer, logTest,testsDir):
    testNum = 288
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian'):
        nParts = 5
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        def scoreKeyAuth (lines):
            #One <KeyAuth> gives granted. One <NoKey> gives denied.
            isKeyAuth = False
            isTestLegit = False
            for line in lines:
                if ("<KEYAUTH>" in line):
                    isTestLegit = True
                    isKeyAuth = True
                    break
                if ("<NOKEY>" in line):
                    isTestLegit = True
                    isKeyAuth = False #to make the code more readable
                    break
            if (isTestLegit):
                return isKeyAuth
            else:
                return SCORES.FAIL

        #part01: Valid Keyring. No key. Wrong Password.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[1],lastGranted=True), scoreKeyAuth (partsLines[1])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[1] = SCORES.CALL_ERR
        elif (tempScoreSheet[0] or tempScoreSheet[1]): #Granted or KeyAuth
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.NONE

        #part02: Valid Keyring. No key. Correct Password.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[2],lastGranted=True), scoreKeyAuth (partsLines[2])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[2] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[2] = SCORES.CALL_ERR
        elif (tempScoreSheet[1]): #KeyAuth
            partsScores[2] = SCORES.V_HIGH
        elif (not tempScoreSheet[0]): #not Granted
            partsScores[2] = SCORES.DOS
        else:
            partsScores[2] = SCORES.NONE

        #part03: Valid Keyring. Valid key. Wrong Password.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[3],lastGranted=True), scoreKeyAuth (partsLines[3])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[3] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[3] = SCORES.CALL_ERR
        elif (not tempScoreSheet[1]): #No Key
            partsScores[3] = SCORES.DOS
        elif (tempScoreSheet[0]): #Granted
            partsScores[3] = SCORES.MED
        else:
            partsScores[3] = SCORES.NONE

        #part04: Valid Keyring. Local key. Wrong Password.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[4],lastGranted=True), scoreKeyAuth (partsLines[4])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[4] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[4] = SCORES.CALL_ERR
        elif (tempScoreSheet[1]): #KeyAuth
            partsScores[4] = SCORES.HIGH
        elif (tempScoreSheet[0]): #Granted && NoKey
            partsScores[4] = SCORES.V_HIGH
        else:
            partsScores[4] = SCORES.NONE

        #part05: Local Keyring. Local key. Wrong Password.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[5],lastGranted=True), scoreKeyAuth (partsLines[5])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[5] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[5] = SCORES.CALL_ERR
        elif (tempScoreSheet[0] or tempScoreSheet[1]): #Granted or KeyAuth
            partsScores[5] = SCORES.V_HIGH
        else:
            partsScores[5] = SCORES.NONE

    elif (osImage == 'FreeBSD'):
        nParts = 2
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        # Part01: Attempt to authenticate against pam_deny.so
        # (We're expecting this to fail, so V_HIGH if granted)
        partsScores[1] = scoreGrantedDenied (SCORES, partsLines[1])
        if ((partsScores[1] != SCORES.FAIL) and (partsScores[1] != SCORES.CALL_ERR)):
            if (partsScores[1]):
                partsScores[1] = SCORES.V_HIGH
            else:
                partsScores[1] = SCORES.NONE

        #  Part02: Run the test from a "trusted" directory.
        # If granted, V_HIGH
        partsScores[2] = scoreGrantedDenied (SCORES, partsLines[2])
        if ((partsScores[2] != SCORES.FAIL) and (partsScores[2] != SCORES.CALL_ERR)):
            if (partsScores[2]):
                partsScores[2] = SCORES.V_HIGH
            else:
                partsScores[2] = SCORES.NONE

    elif (osImage == 'FreeRTOS'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #part01: Valid permissions. List the username.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[1], lastGranted=True), SendRecvCheck(partsLines[1],testNum=testNum)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[1] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #granted
            partsScores[1] = SCORES.V_LOW
        else:
            partsScores[1] = SCORES.NONE

        #part02: Valid permissions. Do not list the username.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[2], lastGranted=True), SendRecvCheck(partsLines[2],testNum=testNum)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[2] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[2] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #granted
            partsScores[2] = SCORES.CALL_ERR
        else:
            partsScores[2] = SCORES.NONE

        #part03: List the username, do not verify the client.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[3], lastGranted=True), SendRecvCheck(partsLines[3],testNum=testNum)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[3] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[3] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #granted
            partsScores[3] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[3], '<ALTERNATE-PATH>')):
            partsScores[3] = SCORES.MED
        else:
            partsScores[3] = SCORES.NONE

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)
