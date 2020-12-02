from fett.base.utils.misc import *
from fett.cwesEvaluation.PPAC.cweScores.helpers import *

def test_384 (logTest,testsDir):
    testNum = 384
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)
    osImage = getOsImage(testLines,testNum=testNum)
    ## V_HIGH if the session strings are the same
    if osImage in ['debian', 'FreeBSD']:
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        testLines = partsLines[1]
        partsScores = {}
        if doesKeywordExist(testLines, "<INVALID>"):
            partsScores[1] = SCORES.CALL_ERR
        else:
            try:
                rootMatch,userMatch = list(matchLines(testLines, r"(?P<user>.*)\.SESSION_ID=(?P<val>.*)"))
                if rootMatch.group("user") == userMatch.group("user"):
                    # Something went wrong, the calling user should
                    # be different
                    partsScores[1] = SCORES.FAIL
                if rootMatch.group("val") == userMatch.group("val"):
                    partsScores[1] = SCORES.V_HIGH
                else:
                    partsScores[1] = SCORES.NONE
            except:
                partsScores[1] = SCORES.FAIL

        listScores = [adjustToCustomScore(testLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
        return overallScore (listScores ,testNum)

    elif (osImage == 'FreeRTOS'):
        return overallScore ([],testNum,msgIfNotImplemented="Not Applicable To FreeRTOS")

    else:
        errorAndLog (f"parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)
