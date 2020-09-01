from fett.base.utils.misc import *
from fett.cwesEvaluation.tests.PPAC.cweScores.helpers import *

def test_284(logTest,testsDir):
    testNum = 284
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage in ['debian', 'FreeBSD']):
        nParts = 4
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        def scoreLogged (partLines):
            checkAuthLog = partitionLines(partLines, "x"*5, "-"*50,testNum=testNum)
            for line in checkAuthLog:
                valueMatch = re.match (r'^nOccurrences=(?P<nOccurrences>[\d]+)$',line) 
                if (valueMatch != None):
                    try:
                        return (int(valueMatch.group('nOccurrences')) > 0)
                    except:
                        pass
            errorAndLog(f"in scoring test_{testNum}: could not match nOccurrences.")
            return SCORES.FAIL

        #part01: Valid permissions. List the username
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[1]), scoreLogged (partsLines[1])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[1] = SCORES.CALL_ERR
        elif (not tempScoreSheet[0]): #not granted
            partsScores[1] = SCORES.DOS
        elif (not tempScoreSheet[1]): #not logged
            partsScores[1] = SCORES.MED
        else: #granted + logged
            partsScores[1] = SCORES.NONE

        #part02: Valid permissions. Do not list username
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[2]), scoreLogged (partsLines[2])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[2] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[2] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #breached
            partsScores[2] = SCORES.V_HIGH
        elif (not tempScoreSheet[1]): #not logged
            partsScores[2] = SCORES.MED
        else: #not breached + logged
            partsScores[2] = SCORES.NONE

        #part03: Use an exposed test284users. Attemp to breach.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[3]), scoreLogged (partsLines[3])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[3] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[3] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #breached
            partsScores[3] = SCORES.V_HIGH
        elif (not tempScoreSheet[1]): #not logged
            partsScores[3] = SCORES.MED
        else: #not breached + logged
            partsScores[3] = SCORES.NONE

        #part04: Add user to list. Use an exposed auth.log to delete traces.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[4]), scoreLogged (partsLines[4])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[4] = SCORES.FAIL
        elif (SCORES.CALL_ERR in tempScoreSheet):
            partsScores[4] = SCORES.CALL_ERR
        elif (not tempScoreSheet[1]): #not logged
            partsScores[4] = SCORES.HIGH
        elif (tempScoreSheet[0]): #granted
            partsScores[4] = SCORES.V_LOW
        else: #not granted + logged
            partsScores[4] = SCORES.NONE

    elif (osImage == 'FreeRTOS'):
        nParts = 4
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}
        
        def scoreLogQueue (partLines):
            checkLog = partitionLines(partLines, "x"*5, "-"*50,testNum=testNum)
            if (len(checkLog) == 0):
                return SCORES.FAIL
            for line in checkLog:
                logMatch = re.match (r'^<logQueue>: <[\w,\s]+>:<[0,1]>$',line) 
                if (logMatch != None):
                    return True
            return False

        #part01: Valid permissions. Do not list username
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[1]), SendRecvCheck(partsLines[1],testNum=testNum), scoreLogQueue (partsLines[1])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[1] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[1] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #granted
            partsScores[1] = SCORES.V_HIGH
        elif (not tempScoreSheet[2]): #not logged
            partsScores[1] = SCORES.MED
        else:
            partsScores[1] = SCORES.NONE

        #part02: Valid permissions. List the username.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[2]), SendRecvCheck(partsLines[2],testNum=testNum), scoreLogQueue (partsLines[2])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[2] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[2] = SCORES.CALL_ERR
        elif (not tempScoreSheet[0]): #not granted
            partsScores[2] = SCORES.DOS
        elif (not tempScoreSheet[2]): #not logged
            partsScores[2] = SCORES.MED
        else:
            partsScores[2] = SCORES.NONE

        #part03: Use an exposed usersList. Attempt to breach.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[3]), SendRecvCheck(partsLines[3],testNum=testNum), scoreLogQueue (partsLines[3])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[3] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[3] = SCORES.CALL_ERR
        elif (tempScoreSheet[0]): #granted, i.e. breached
            partsScores[3] = SCORES.V_HIGH 
        elif (doesKeywordExist(partsLines[3], '<BREACHED-LIST>')): #got the handle
            partsScores[3] = SCORES.HIGH
        elif (not tempScoreSheet[2]): #not logged
            partsScores[3] = SCORES.MED
        else:
            partsScores[3] = SCORES.NONE

        #part04: Use an exposed logQueue. Attempt to delete traces.
        tempScoreSheet = [scoreGrantedDenied (SCORES, partsLines[4]), SendRecvCheck(partsLines[4],testNum=testNum), scoreLogQueue (partsLines[4])]
        if (SCORES.FAIL in tempScoreSheet):
            partsScores[4] = SCORES.FAIL
        elif ((SCORES.CALL_ERR in tempScoreSheet) or (not tempScoreSheet[1])): #request received
            partsScores[4] = SCORES.CALL_ERR
        elif (not tempScoreSheet[2]): #not logged
            partsScores[4] = SCORES.HIGH
        elif (doesKeywordExist(partsLines[3], '<BREACHED-LOG>')): #got the handle
            partsScores[4] = SCORES.MED        
        elif (tempScoreSheet[0]): #granted
            partsScores[4] = SCORES.V_LOW 
        else:
            partsScores[4] = SCORES.NONE

    else:
        errorAndLog (f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)
