"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for resourceManagement
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
from fett.cwesEvaluation.resourceManagement.customCweScores import *
from fett.cwesEvaluation.resourceManagement.customCweScores.helpers import regPartitionTest, regPartitionTestFreeRTOS
from fett.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests, overallScore, doKeywordsExistInText
import fett.cwesEvaluation.common
from collections import defaultdict
from copy import deepcopy

VULCLASS = "resourceManagement"

@decorate.debugWrap
def scoreAllTests(logs):
    if (isEnabledDict(VULCLASS,"useSelfAssessment")):
        return defaultSelfAssessmentScoreAllTests(VULCLASS, logs)

    # Score the log files
    ret = []
    funcTestsScores = dict()
    for name, log in logs:
        logLines = ftReadLines(log)
        if (name in getSettingDict(VULCLASS,["testsInfo"])): #regular CWE test
            try:
                testScorerFunc = getattr(globals()[name],name)
            except Exception as exc:
                errorAndLog(f"scoreAllTests-{VULCLASS}: Could not locate the scorer function for <{name}>",exc=exc)
                ret.append([f"{name.replace('_','-').upper()}", SCORES.FAIL, "Failed to Score!"])
                continue
            ret.append(testScorerFunc(logLines))
        else: #special grouped tests (non CWEs)
            scoreInfo = defaultScoreTest(name, logLines, "funcTestsInfo")
            printAndLog(f"{VULCLASS}-Score-Details: {scoreInfo}",doPrint=False)
            try:
                funcTestsScores[scoreInfo[0]] = scoreInfo[1]
            except Exception as exc:
                logAndExit(f"scoreAllTests-{VULCLASS}: Failed to read the output of overallScore for {name}.")

    # Append ret with the CWEs scores based on funcTests
    for test, funcTests in getSettingDict(VULCLASS,["mapTestsToCwes"]).items():
        if (not fett.cwesEvaluation.common.isTestEnabled(VULCLASS,test)):
            continue
        listScores = []
        scoreDetails = []
        for funcTest in funcTests:
            if (funcTest in funcTestsScores):
                score = funcTestsScores[funcTest]
            else:
                warnAndLog(f"scoreAllTests-{VULCLASS}: Missing score for <{funcTest}>.")
                score = SCORES.FAIL
            scoreDetails.append(f"{funcTest.split('_')[-1]}:{score}")
            listScores.append(score)
        dispName = f"{test.replace('_','-').upper()}"
        ret.append(overallScore(listScores,dispName,scoreString=', '.join(scoreDetails)))

    return ret

@decorate.debugWrap
def defaultScoreTest(testName, logLines, testsInfoSection):
    osFlavor = "unix" if isEnabled("isUnix") else "FreeRTOS"
    nParts = getSettingDict(VULCLASS,[testsInfoSection,testName,osFlavor])

    scoreOptions = [SCORES.CALL_ERR, SCORES.HIGH, SCORES.MED, SCORES.LOW, SCORES.NONE]

    def scoreToKey(xScore, negate=False):
        if (negate):
            return f"NEG-{str(xScore).lower()}Keywords"
        else:
            return f"{str(xScore).lower()}Keywords"

    # Collect goldenKeywords
    goldenKeywords = defaultdict(list)
    for negate in [False, True]:
        for xScore in scoreOptions:
            key = scoreToKey(xScore,negate=negate)
            if doesSettingExistDict(VULCLASS,[testsInfoSection,testName,key]):
                curDict = deepcopy(getSettingDict(VULCLASS,[testsInfoSection,testName,key]))
                for setting in ["osImage", "target"]:
                    if (getSetting(setting) in curDict):
                        curDict = curDict[getSetting(setting)]
                    elif ("any" in curDict):
                        curDict = curDict["any"]
                    else:
                        logAndExit(f"defaultScoreTest: Failed to parse the <{setting}> keywords for <{testName}>.",exitCode=EXIT.Dev_Bug)
                goldenKeywords[key] = curDict

    goldenKeywords[scoreToKey(SCORES.CALL_ERR)] += ["<INVALID>"] #INVALID is common
    relvKeywords =  [levelKeyword for levelKeywords in goldenKeywords.values() for levelKeyword in levelKeywords]
    
    def scorePart(partLogLines):
        """
        for each score, starting with the worst --> best; do
            if one of the golden keywords exist --> return this score
            if one of the golden NEG-keywors does not exist --> return this score
        done
        """
        scoredKeywords = doKeywordsExistInText('\n'.join(partLogLines),relvKeywords)
        for xScore in scoreOptions:   
            for negate in [False, True]:
                for goldenKeyword in goldenKeywords[scoreToKey(xScore,negate=negate)]:
                    if (negate ^ scoredKeywords[goldenKeyword]):
                        return xScore
        return SCORES.FAIL

    if (nParts == 1):
        partsLines = {1: logLines}
    else:
        if (isEqSetting('osImage','FreeRTOS')):
            partsLines = regPartitionTestFreeRTOS(logLines,nParts,testNum=testName)
        else:
            partsLines = regPartitionTest(logLines,nParts,testNum=testName)
    
    listScores = [adjustToCustomScore(partsLines[iPart],scorePart(partsLines[iPart])) for iPart in range(1,nParts+1)]
    if (testsInfoSection=="funcTestsInfo"): #This is not ready to display yet
        dispName = testName
    else: 
        dispName = f"{testName.replace('_','-').upper()}"
    return overallScore(listScores,dispName)