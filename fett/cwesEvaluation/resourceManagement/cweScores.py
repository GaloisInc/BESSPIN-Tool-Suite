"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring function for resourceManagement
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
from fett.cwesEvaluation.resourceManagement.customCweScores import *
from fett.cwesEvaluation.resourceManagement.customCweScores.helpers import regPartitionTest
from fett.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests, overallScore, doKeywordsExistInText
from collections import defaultdict
from copy import deepcopy

VULCLASS = "resourceManagement"

@decorate.debugWrap
def scoreAllTests(logs):
    if (isEnabledDict(VULCLASS,"useSelfAssessment")):
        return defaultSelfAssessmentScoreAllTests(VULCLASS, logs)

    ret = []
    for name, log in logs:
        logLines = ftReadLines(log)
        if (name in getSettingDict(VULCLASS,["testsInfo"])): #regular CWE test
            try:
                testScorerFunc = getattr(globals()[name],name)
            except Exception as exc:
                errorAndLog(f"scoreAllTests-resourceManagement: Could not locate the scorer function for <{name}>",exc=exc)
                ret.append([f"{name.replace('_','-').upper()}", SCORES.FAIL, "Failed to Score!"])
                continue
            ret.append(testScorerFunc(logLines))
        else: #special grouped tests (non CWEs)
            ret.append(defaultScoreTest(name, logLines, "funcTestsInfo"))
    return ret

@decorate.debugWrap
def defaultScoreTest(testName, logLines, testsInfoSection):
    osFlavor = "unix" if isEnabled("isUnix") else "FreeRTOS"
    nParts = getSettingDict(VULCLASS,[testsInfoSection,testName,osFlavor])

    scoreOptions = [SCORES.HIGH, SCORES.MED, SCORES.LOW, SCORES.NONE]

    # Collect goldenKeywords
    goldenKeywords = defaultdict(list)
    for xScore in scoreOptions:
        key = f"{str(xScore).lower()}Keywords"
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

    relvKeywords = ["<INVALID>"] + [levelKeyword for levelKeywords in goldenKeywords.values() for levelKeyword in levelKeywords]
    scoredKeywords = doKeywordsExistInText('\n'.join(logLines),relvKeywords)

    def scorePart(partLogLines):
        if (scoredKeywords["<INVALID>"]):
            return SCORES.CALL_ERR
        else:
            for xScore in scoreOptions:
                key = f"{str(xScore).lower()}Keywords"
                for goldenKeyword in goldenKeywords[key]:
                    if (scoredKeywords[goldenKeyword]):
                        return xScore
            return SCORES.FAIL

    if (nParts == 1):
        partsLines = {1: logLines}
    else:
        for iPart in range(1,nParts+1):
            partsLines = regPartitionTest (logLines,nParts,testNum=testName)
    
    listScores = [adjustToCustomScore(partsLines[iPart],scorePart(partsLines[iPart])) for iPart in range(1,nParts+1)]
    return overallScore(listScores,f"{testName.replace('_','-').upper()}")