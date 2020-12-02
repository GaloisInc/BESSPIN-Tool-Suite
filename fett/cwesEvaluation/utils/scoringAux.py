"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
helpers functions for scoring the CWE tests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
import re

def overallScore (listScores, dispName, msgIfNotImplemented="Not Implemented", 
        msgIfRecommended="Error - Recommendation text is not available"):
    if (len(listScores)==0): #not implemented
        return [dispName, SCORES.NOT_IMPLEMENTED, msgIfNotImplemented]
    elif ((len(listScores)==1) and (listScores[0]==SCORES.RECOMMEND)):
        return [dispName, SCORES.RECOMMEND, msgIfRecommended]
    ovrScore = SCORES.minScore(listScores)
    scoreString = ', '.join([f"p{i+1:02d}:{partScore}" for i,partScore in enumerate(listScores)])

    return [dispName, ovrScore, scoreString]

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

def defaultRecommendationText (dispName, testLog):
    logLines = ftReadLines(testLog)
    if doesKeywordExistInLines (logLines,"<INVALID>"):
        return overallScore([SCORES.CALL_ERR],dispName)
    textMatch = matchExprInLines (r"^<TEXT=(?P<cweText>.+)>",logLines)
    if (textMatch is None):
        return overallScore([SCORES.RECOMMEND],dispName)
    else:
        return overallScore([SCORES.RECOMMEND],dispName,msgIfRecommended=textMatch.group("cweText"))