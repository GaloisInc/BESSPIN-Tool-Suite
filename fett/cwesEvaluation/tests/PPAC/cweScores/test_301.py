from .helpers import *

def test_301(SCORES, customScorer, logTest,testsDir):
    testNum = 301
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)
    if (osImage in ['debian','FreeBSD']):
        return overallScore (SCORES, [],testNum,msgIfNotImplemented="Not Implemented -- Protocol Level")

    elif (osImage == 'FreeRTOS'):
        nParts = 3
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        def specialSendRecvCheck (lines, pairsList):
            for keywordTarget, keywordHost in pairsList:
                targetHash = ''
                hostHash = ''
                for line in lines:
                    targetMatch = re.match(rf'^<(?P<targetGroup>[0-9a-f]+)>:<{keywordTarget}>$',line)
                    hostMatch = re.match(rf'^<(?P<hostGroup>[0-9a-f]+)>:<{keywordHost}>$',line)
                    if (targetMatch is not None):
                        targetHash = targetMatch.group('targetGroup')
                    elif (hostMatch is not None):
                        hostHash = hostMatch.group('hostGroup')
                    
                    if ((len(targetHash)>0) and (len(hostHash)>0)):
                        break
                if ((targetHash!=hostHash) or (len(targetHash)==0)):
                    return False
            return True

        #part01: DH protocol. Diff key-pair.
        pairs01 = []
        pairsSecret12 = []
        for i in range(2):
            pairs01 += [(f"HOST-GEN-{i}-PUB-KEY",f"TARGET-RECV-{i}-PUB-KEY")]
            pairs01 += [(f"TARGET-GEN-{i}-PUB-KEY",f"HOST-RECV-{i}-PUB-KEY")]
            pairsSecret12 += [(f"HOST-GEN-{i}-SECRET",f"TARGET-GEN-{i}-SECRET")]

        if (doesKeywordExist(partsLines[1],'<INVALID>')):
            partsScores[1] = SCORES.CALL_ERR
        elif (not specialSendRecvCheck(partsLines[1],pairs01)):
            partsScores[1] = SCORES.CALL_ERR
        elif (specialSendRecvCheck(partsLines[1],pairsSecret12)):
            partsScores[1] = SCORES.MED
        else:
            partsScores[1] = SCORES.NONE

        #Part02: DH protocol. Same key-pair.
        pairs02 = []
        for i in range(2):
            pairs02 += [(f"HOST-GEN-{i}-PUB-KEY",f"TARGET-RECV-{i}-PUB-KEY")]
            pairs02 += [(f"TARGET-GEN-S-PUB-KEY",f"HOST-RECV-{i}-PUB-KEY")]

        if (doesKeywordExist(partsLines[2],'<INVALID>')):
            partsScores[2] = SCORES.CALL_ERR
        elif (not specialSendRecvCheck(partsLines[2],pairs02)):
            partsScores[2] = SCORES.CALL_ERR
        elif (specialSendRecvCheck(partsLines[2],pairsSecret12)):
            partsScores[2] = SCORES.HIGH
        else:
            partsScores[2] = SCORES.NONE

        #Part03: DH-style protocol. Reflection attack.
        pairs03 = []
        for i in range(2):
            pairs03 += [(f"HOST-GEN-{i}-CHALLENGE",f"TARGET-RECV-{i}-CHALLENGE")]
            pairs03 += [(f"HOST-RECV-{i}-ANSWER",f"TARGET-GEN-{i}-RESPONSE")]
            pairs03 += [(f"HOST-RECV-{i}-CHALLENGE",f"TARGET-GEN-{i}-CHALLENGE")]
            pairs03 += [(f"HOST-GEN-{i}-RESPONSE",f"TARGET-RECV-{i}-ANSWER")]

        if (doesKeywordExist(partsLines[3],'<INVALID>')):
            partsScores[3] = SCORES.CALL_ERR
        elif (not specialSendRecvCheck(partsLines[3],pairs03)):
            partsScores[3] = SCORES.CALL_ERR
        elif ((not doesKeywordExist(partsLines[3],'<TARGET-GEN-0-ANSWER>')) or (not doesKeywordExist(partsLines[3],'<TARGET-GEN-1-ANSWER>'))):
            partsScores[3] = SCORES.CALL_ERR
        elif (not doesKeywordExist(partsLines[3],'<DENIED-1>')):
            partsScores[3] = SCORES.CALL_ERR
        elif (doesKeywordExist(partsLines[3],'<GRANTED-0>')):
            partsScores[3] = SCORES.V_HIGH
        elif (doesKeywordExist(partsLines[3],'<DENIED-0>')):
            partsScores[3] = SCORES.NONE
        else:
            partsScores[3] = SCORES.FAIL

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)