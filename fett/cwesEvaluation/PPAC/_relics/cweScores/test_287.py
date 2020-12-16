from fett.base.utils.misc import *
from fett.cwesEvaluation.PPAC.cweScores.helpers import *

def test_287(logTest,testsDir):
    testNum = 287
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)
    isSshTest = doesKeywordExist(testLines,'<SSH-TEST>')
    if ((osImage == 'debian') and (not isSshTest)):
        nParts = 3
        partsLines = {} #custom parititioning
        partsScores = {}
        subPartsScores = {}

        def scoreLoginAndSu (lines):
            #Tuples: (granted/denied, isFound)
            isLoginUserGranted = (None, False)
            isSuRootGranted = (None, False)
            isLoginRootGranted = (None, False)
            for line in lines:
                if ("<INVALID>" in line):
                    return SCORES.CALL_ERR
                if ("<loginUser-GRANTED>" in line):
                    isLoginUserGranted = (True, True)
                if ("<loginUser-DENIED>" in line):
                    isLoginUserGranted = (False, True)
                if ("<suRoot-GRANTED>" in line):
                    isSuRootGranted = (True, True)
                if ("<suRoot-DENIED>" in line):
                    isSuRootGranted = (False, True)
                if ("<loginRoot-GRANTED>" in line):
                    isLoginRootGranted = (True, True)
                if ("<loginRoot-DENIED>" in line):
                    isLoginRootGranted = (False, True)

            if (isLoginUserGranted[1] and isSuRootGranted[1] and isLoginRootGranted[1]):
                if (isSuRootGranted[0] or isLoginRootGranted[0]):
                    return SCORES.V_HIGH
                elif (isLoginUserGranted[0]):
                    return SCORES.HIGH
                else:
                    return SCORES.NONE
            else:
                return SCORES.FAIL

        def findPermissionsAndGroup (lines):
            for line in lines:
                lineMatch = re.match(r'^(?P<permissions>[drwx-]{10}) \d+ \w+ (?P<xGroup>\w+) .*$',line)
                if (lineMatch is not None):
                    permBin = [(x!='-') for x in lineMatch.group('permissions')]
                    return [permBin, lineMatch.group('xGroup')]
            return [None, None]

        def findUserGroups (lines):
            for line in lines:
                lineMatch = re.match(r'^[\w-]+ (?P<xGroup>\w+)$',line)
                if (lineMatch is not None):
                    return lineMatch.group('xGroup')
            return None

        partsLines[1] = {}
        partsLines[1]['a'] = partitionLines(testLines,"---Part01a:", "---Part01b:",testNum=testNum)
        partsLines[1]['b'] = partitionLines(testLines,"---Part01b:", "---Part02:",testNum=testNum)
        partsLines[2] = {}
        partsLines[2]['ini'] = partitionLines(testLines,"---Part02:", "---Part02a:",testNum=testNum)
        partsLines[2]['a'] = partitionLines(testLines,"---Part02a:", "---Part02b:",testNum=testNum)
        partsLines[2]['b'] = partitionLines(testLines,"---Part02b:", "---Part03:",testNum=testNum)
        partsLines[3] = {}
        partsLines[3]['ini'] = partitionLines(testLines,"---Part03:", "---Part03a:",testNum=testNum)
        partsLines[3]['a'] = partitionLines(testLines,"---Part03a:", "---Part03b:",testNum=testNum)
        partsLines[3]['b'] = partitionLines(testLines,"---Part03b:", "-"*50,testNum=testNum)

        subPartsScores[1] = [scoreLoginAndSu(partsLines[1]['a']), scoreLoginAndSu(partsLines[1]['b'])]
        tempPartsScoresAdjusted = [adjustToCustomScore(partsLines[1]['a'],subPartsScores[1][0]),
                                  adjustToCustomScore(partsLines[1]['b'],subPartsScores[1][1])]
        partsScores[1] = SCORES.minScore(tempPartsScoresAdjusted)

        p2Perm, p2PermGroup = findPermissionsAndGroup(partsLines[2]['ini'])
        p2UserGroup = findUserGroups(partsLines[2]['ini'])
        if ((p2Perm is None) or (p2PermGroup is None)):
            p2ScoreIni = SCORES.FAIL
        elif (p2UserGroup is None):
            p2ScoreIni = SCORES.DOS
        elif (p2UserGroup == p2PermGroup):
            if (p2Perm[5]): #S_IWGRP
                p2ScoreIni = SCORES.HIGH
            else:
                p2ScoreIni = SCORES.MED
        else:
            p2ScoreIni = SCORES.NONE

        subPartsScores[2] = [p2ScoreIni, scoreLoginAndSu(partsLines[2]['a']), scoreLoginAndSu(partsLines[2]['b'])]
        tempPartsScoresAdjusted = [adjustToCustomScore(partsLines[2]['ini'],subPartsScores[2][0]),
                                  adjustToCustomScore(partsLines[2]['a'],subPartsScores[2][1]),
                                  adjustToCustomScore(partsLines[2]['b'],subPartsScores[2][2])]
        partsScores[2] = SCORES.minScore(tempPartsScoresAdjusted)

        p3Perm, p3PermGroup = findPermissionsAndGroup(partsLines[3]['ini'])
        if ((p3Perm is None) or (p3PermGroup is None)):
            p3ScoreIni = SCORES.FAIL
        elif (p3Perm[8]): #S_IWOTH
            p3ScoreIni = SCORES.HIGH
        else:
            p3ScoreIni = SCORES.NONE

        subPartsScores[3] = [p2ScoreIni, scoreLoginAndSu(partsLines[3]['a']), scoreLoginAndSu(partsLines[3]['b'])]
        tempPartsScoresAdjusted = [adjustToCustomScore(partsLines[3]['ini'],subPartsScores[3][0]),
                                  adjustToCustomScore(partsLines[3]['a'],subPartsScores[3][1]),
                                  adjustToCustomScore(partsLines[3]['b'],subPartsScores[3][2])]
        partsScores[3] = SCORES.minScore(tempPartsScoresAdjusted)

        listScores = list(partsScores.values())

    elif ((osImage == 'FreeBSD') or ((osImage == 'debian') and isSshTest)):
        nParts = 2
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        allowedScore = {1:SCORES.CALL_ERR, 2:SCORES.V_HIGH}
        for iPart in range(1,nParts+1):
            partsScores[iPart] = scoreGrantedDenied(SCORES,partsLines[iPart])
            if ((partsScores[iPart] != SCORES.FAIL) and (partsScores[iPart] != SCORES.CALL_ERR)): #it's true or false
                if (not partsScores[iPart]): #if not granted
                    partsScores[iPart] = SCORES.NONE
                else:
                    partsScores[iPart] = allowedScore[iPart]

        listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]

    elif (osImage == 'FreeRTOS'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #part01: Valid permissions. List the username.     
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[1]), SendRecvCheck(partsLines[1],testNum=testNum)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[1] = SCORES.CALL_ERR
        elif (not tempScoreSheet[0]): #not granted
            partsScores[1] = SCORES.DOS
        else:
            partsScores[1] = SCORES.NONE

        #part02: Valid permissions. Do not list the username.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[2]), SendRecvCheck(partsLines[2],testNum=testNum)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[2] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[2] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #granted
            partsScores[2] = SCORES.CALL_ERR
        else:
            partsScores[2] = SCORES.NONE

        #part03: List the username, do not verify the client.
        partsScores[3] = scoreGrantedDenied (SCORES, partsLines[3])
        if ((partsScores[3] != SCORES.FAIL) and (partsScores[3] != SCORES.CALL_ERR)): #it's true or false
            if (not doesKeywordExist(partsLines[3], '<HOST-RECV>:Jedi Order CLNT')):
                partsScores[3] = SCORES.CALL_ERR
            elif (partsScores[3]):
                partsScores[3] = SCORES.V_HIGH
            else:
                partsScores[3] = SCORES.NONE

        listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]

    else:
        errorAndLog (f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    return overallScore (listScores ,testNum)
