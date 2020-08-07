from fett.base.utils.misc import *
from fett.cwesEvaluation.tests.PPAC.cweScores.helpers import *

def test_799 (logTest,testsDir):
    testNum = 799
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)
    if (osImage == 'debian'):
        nParts = 6
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #part01: PAM w/ exposed test799users and manipulate it
        specialPart1 = partitionLines(partsLines[1],"./test_799.riscv", "NotRealUser",testNum=testNum)
        specialPart2 = partitionLines(partsLines[1],"NotRealUser", "x"*5,testNum=testNum)
        tempScoreSheet = [scoreGrantedDenied (SCORES, specialPart1), scoreGrantedDenied (SCORES, specialPart2)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[1] = SCORES.CALL_ERR
        elif (tempScoreSheet[1]):
            partsScores[1] = SCORES.V_HIGH
        elif (tempScoreSheet[0]): #still malicious
            partsScores[1] = SCORES.V_LOW
        else: #all denied
            partsScores[1] = SCORES.NONE

        #part02: PAM w/ exposed limits and a longer queue
        partsScores[2] = scoreGrantedDenied (SCORES, partsLines[2])
        if ((partsScores[2] != SCORES.FAIL) and (partsScores[2] != SCORES.CALL_ERR)):
            #valid
            if (partsScores[2]):
                partsScores[2] = SCORES.LOW
            else:
                partsScores[2] = SCORES.NONE

        #part03: PAM w/ exposed limits and a wider queue
        partsScores[3] = scoreGrantedDenied (SCORES, partsLines[3])
        if ((partsScores[3] != SCORES.FAIL) and (partsScores[3] != SCORES.CALL_ERR)):
            #valid
            if (partsScores[3]):
                partsScores[3] = SCORES.V_LOW
            else:
                partsScores[3] = SCORES.NONE

        #part04: Valid protection using limits and lisfile. Attempt a long queue.
        partsScores[4] = scoreGrantedDenied (SCORES, partsLines[4])
        if ((partsScores[4] != SCORES.FAIL) and (partsScores[4] != SCORES.CALL_ERR)):
            #valid
            if (partsScores[4]):
                partsScores[4] = SCORES.HIGH
            else:
                partsScores[4] = SCORES.NONE

        #part05: Valid protection using limits and lisfile. Attempt an extra token.
        partsScores[5] = scoreGrantedDenied (SCORES, partsLines[5])
        if ((partsScores[5] != SCORES.FAIL) and (partsScores[5] != SCORES.CALL_ERR)):
            #valid
            if (partsScores[5]):
                partsScores[5] = SCORES.V_HIGH
            else:
                partsScores[5] = SCORES.NONE

        #part05: Valid protection using limits and lisfile. No breaching.
        partsScores[6] = scoreGrantedDenied (SCORES, partsLines[6])
        if ((partsScores[6] != SCORES.FAIL) and (partsScores[6] != SCORES.CALL_ERR)):
            #valid
            if (partsScores[6]):
                partsScores[6] = SCORES.NONE
            else:
                partsScores[6] = SCORES.DOS

    elif (osImage == 'FreeBSD'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #part01: Get all tokens, then ask for more.
        firstSubPart01 = partitionLines(partsLines[1],"Executing test_799 on user","End of test_799 on user",testNum=testNum)
        tempScoreSheet = [scoreGrantedDenied (SCORES, firstSubPart01), scoreGrantedDenied (SCORES, partsLines[1])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[1] = SCORES.CALL_ERR
        elif ((not tempScoreSheet[0]) or (tempScoreSheet[1])):
            partsScores[1] = SCORES.CALL_ERR
        else:
            partsScores[1] = SCORES.NONE

        #part02: Attempt an extra token.
        partsScores[2] = scoreGrantedDenied (SCORES, partsLines[2])
        if ((partsScores[2] != SCORES.FAIL) and (partsScores[2] != SCORES.CALL_ERR)):
            #valid
            if (partsScores[2]):
                partsScores[2] = SCORES.V_HIGH
            else:
                partsScores[2] = SCORES.NONE

        #part03: Breaching.
        firstSubPart03 = partitionLines(partsLines[3],"Executing test_799 on user","End of test_799 on user",testNum=testNum)
        tempScoreSheet = [scoreGrantedDenied (SCORES, firstSubPart03), scoreGrantedDenied (SCORES, partsLines[3],lastGranted=True)]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[3] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[3] = SCORES.CALL_ERR
        elif (tempScoreSheet[1]): #the breach attempt
            partsScores[3] = SCORES.V_HIGH
        elif (tempScoreSheet[0]): #It was exposed
            partsScores[3] = SCORES.HIGH
        else:
            partsScores[3] = SCORES.NONE

    elif (osImage == 'FreeRTOS'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        def scorePart (part,specialKeywords):
            #returns a list: listofSendRecvChec + listOfGrantedDenied + listOfSpecialKeywordsExistence
            tryN = partitionLines(part,"<request(N+0)>", "<request(N+1)>",testNum=testNum)
            tryNp1 = partitionLines(part,"<request(N+1)>", "-"*50,testNum=testNum)

            listOfGranted = [scoreGrantedDenied(SCORES,tryN), scoreGrantedDenied(SCORES,tryNp1)]

            listOfSendRecv = [SendRecvCheck (tryN+tryNp1,testNum=testNum), SendRecvCheck (tryNp1,testNum=testNum)]

            listOfSpecialKeywords = []
            for keyword in specialKeywords:
                listOfSpecialKeywords.append(doesKeywordExist(tryN+tryNp1, keyword))

            return listOfSendRecv + listOfGranted + listOfSpecialKeywords

        #part01: Baseline sanity check.
        tempScoreSheet = scorePart(partsLines[1],[])
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[0]) or (not tempScoreSheet[1])): #request received
            partsScores[1] = SCORES.CALL_ERR
        elif (tempScoreSheet[3]): #request N+1
            partsScores[1] = SCORES.V_HIGH
        elif (not tempScoreSheet[2]): #request N
            partsScores[1] = SCORES.DOS
        else: #all denied
            partsScores[1] = SCORES.NONE

        #part02: Using an exposed semaphore.
        tempScoreSheet = scorePart(partsLines[2],['<BREACHED-HANDLE>', '<BREACHED-TOKEN>'])
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[2] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[0]) or (not tempScoreSheet[1])): #request received
            partsScores[2] = SCORES.CALL_ERR
        elif (tempScoreSheet[3]): #request N+1
            partsScores[2] = SCORES.V_HIGH
        elif (tempScoreSheet[5]): #semaphore-token
            partsScores[2] = SCORES.HIGH
        elif (tempScoreSheet[4]): #semaphore handle
            partsScores[2] = SCORES.MED    
        elif (tempScoreSheet[2]): #request N
            partsScores[2] = SCORES.V_LOW
        else: #all denied
            partsScores[2] = SCORES.NONE

        #part03: Using an exposed structure.
        tempScoreSheet = scorePart(partsLines[3],['<BREACHED-STRUCT>'])
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[3] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[0]) or (not tempScoreSheet[1])): #request received
            partsScores[3] = SCORES.CALL_ERR
        elif (tempScoreSheet[3]): #request N+1
            partsScores[3] = SCORES.V_HIGH
        elif (tempScoreSheet[4]): #structure pointer
            partsScores[3] = SCORES.HIGH
        elif (tempScoreSheet[2]): #request N
            partsScores[3] = SCORES.V_LOW
        else: #all denied
            partsScores[3] = SCORES.NONE

    else:
        errorAndLog (f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)
