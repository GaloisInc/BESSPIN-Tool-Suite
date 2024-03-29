"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
helpers functions for scoring the CWE tests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
import re

def overallScore (listScores, dispName, msgIfNotImplemented="Not Implemented", 
        isSelfAssessment=False, msgIfSelfAssessment="Error - CWE text is not available", scoreString=None,
        partsWeights=None):
    if (len(listScores)==0): #not implemented
        return [dispName, SCORES.NOT_IMPLEMENTED, SCORES.NOT_IMPLEMENTED.value, msgIfNotImplemented]
    
    if (partsWeights is None):
        ovrScore = SCORES.minScore(listScores)
        exactScore = ovrScore.value
    else:
        ovrScore, exactScore = SCORES.weightedAvgScore(listScores,partsWeights)

    if (scoreString is None):
        if (isSelfAssessment):
            scoreString = msgIfSelfAssessment
        else:
            scoreString = ', '.join([f"p{i+1:02d}:{partScore}" for i,partScore in enumerate(listScores)])

    return [dispName, ovrScore, exactScore, scoreString]

def doesKeywordExistInLines (lines, keyword):
    for line in lines:
        if (keyword in line):
            return True
    return False

def doKeywordsExistInText (logText, keywords):
    keywordsDict = dict()
    for keyword in keywords:
        keywordsDict[keyword] = (re.search(keyword,logText) is not None)
    return keywordsDict

def defaultSelfAssessmentScoreAllTests (vulClass, logs):
    ret = []
    for testName, log in logs:
        dispName = testName.replace('_','-').upper()
        ret.append(overallScore([getSelfAssessmentScore(vulClass,testName)],dispName,isSelfAssessment=True,
            msgIfSelfAssessment=getSettingDict(vulClass,["testsInfo",testName,"cweText"])))
    return ret

def getSelfAssessmentScore (vulClass, testName):
    return SCORES.toScore(getSettingDict(vulClass,["selfAssessment",testName.replace("test_","assessment_")]))