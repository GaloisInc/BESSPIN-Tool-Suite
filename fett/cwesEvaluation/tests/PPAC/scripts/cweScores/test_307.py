from .helpers import *

def test_307 (SCORES, customScorer, logTest,testsDir):
    testNum = 307
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    def scorePart (part,checkSendRecv=False):
        try1 = partitionLines(part,"<authForNofAttempts(1)>", "<authForNofAttempts(N)>",testNum=testNum)
        tryN = partitionLines(part,"<authForNofAttempts(N)>", "<authForNofAttempts(N+1)>",testNum=testNum)
        tryNp1 = partitionLines(part,"<authForNofAttempts(N+1)>", "-"*50,testNum=testNum)

        grantedOrDenied = [scoreGrantedDenied(SCORES,try1,lastGranted=True), scoreGrantedDenied(SCORES,tryN,lastGranted=True), scoreGrantedDenied(SCORES,tryNp1,lastGranted=True)]
        if (checkSendRecv):
            if ((grantedOrDenied[0]==True) and (not SendRecvCheck (try1+tryN,testNum=testNum))):
                grantedOrDenied[0] = SCORES.CALL_ERR
            if ((grantedOrDenied[1]==True) and (not SendRecvCheck (tryN+tryNp1,testNum=testNum))):
                grantedOrDenied[1] = SCORES.CALL_ERR
            if ((grantedOrDenied[2]==True) and (not SendRecvCheck (tryNp1,testNum=testNum))):
                grantedOrDenied[2] = SCORES.CALL_ERR
        return grantedOrDenied

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian'):
        nParts = 4
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #part01: PAM with no tally
        tempScoreSheet = scorePart(partsLines[1])
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[1] = SCORES.CALL_ERR
        elif ((not tempScoreSheet[0]) or (not tempScoreSheet[1])):
            partsScores[1] = SCORES.DOS
        elif tempScoreSheet[2]: #granted is bad, but it is a very tough task
            partsScores[1] = SCORES.V_LOW
        else: #denied
            partsScores[1] = SCORES.NONE

        #part02: PAM with tally on non-existing file
        tempScoreSheet = scorePart(partsLines[2])
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[2] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[2] = SCORES.CALL_ERR
        elif ((not tempScoreSheet[0]) or (not tempScoreSheet[1])):
            partsScores[2] = SCORES.DOS
        elif tempScoreSheet[2]: #granted is bad
            partsScores[2] = SCORES.HIGH
        else: #denied
            partsScores[2] = SCORES.NONE
        
        #part03: PAM w/ correct and working tally
        tempScoreSheet = scorePart(partsLines[3])
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[3] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[3] = SCORES.CALL_ERR
        elif ((not tempScoreSheet[0]) or (not tempScoreSheet[1])):
            partsScores[3] = SCORES.DOS
        elif tempScoreSheet[2]: #granted is really bad
            partsScores[3] = SCORES.V_HIGH
        else: #denied
            partsScores[3] = SCORES.NONE

        #part04: PAM w/ local file and delete it
        tempScoreSheet = scorePart(partsLines[4])
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[4] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[4] = SCORES.CALL_ERR
        elif (tempScoreSheet[2]):
            partsScores[4] = SCORES.V_HIGH
        elif (tempScoreSheet[1]): #still malicious
            partsScores[4] = SCORES.V_LOW
        else: #all denied
            partsScores[4] = SCORES.NONE

    elif (osImage == 'FreeBSD'):
        if (doesKeywordExist(testLines, '<QEMU-N/A>')):
            return overallScore (SCORES, [],testNum,msgIfNotImplemented="Not Implemented on Qemu")

        nParts = 2
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        allowedScore = {1:SCORES.CALL_ERR, 2:SCORES.V_HIGH}
        for iPart in range(1,nParts+1):
            partsScores[iPart] = scoreGrantedDenied(SCORES,partsLines[iPart],lastGranted=True)
            if ((partsScores[iPart] != SCORES.FAIL) and (partsScores[iPart] != SCORES.CALL_ERR)): #it's true or false
                if (not partsScores[iPart]): #if not granted
                    partsScores[iPart] = SCORES.NONE
                else:
                    partsScores[iPart] = allowedScore[iPart]
        
    elif (osImage == 'FreeRTOS'):
        nParts = 2
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        #part01: The target is the server and the host machine is the client
        tempScoreSheet = scorePart(partsLines[1],checkSendRecv=True)
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[1] = SCORES.CALL_ERR
        elif ((not tempScoreSheet[0]) or (not tempScoreSheet[1])):
            partsScores[1] = SCORES.DOS
        elif tempScoreSheet[2]: #granted means breach at N+1
            partsScores[1] = SCORES.MED
        else: #denied
            partsScores[1] = SCORES.NONE

        #part02: The host machine is the server and the target is the client
        tempScoreSheet = scorePart(partsLines[2],checkSendRecv=True)
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[2] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[2] = SCORES.CALL_ERR
        elif ((not tempScoreSheet[0]) or (not tempScoreSheet[1])):
            partsScores[2] = SCORES.DOS
        elif tempScoreSheet[2]: #granted means breach at N+1
            partsScores[2] = SCORES.V_HIGH
        else: #denied
            partsScores[2] = SCORES.NONE

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)