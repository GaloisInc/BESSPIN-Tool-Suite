#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
helpers functions for scoring the CWE tests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
import re

def overallScore (listScores, testNum,msgIfNotImplemented="Not Implemented"):
    if (len(listScores)==0): #not implemented
        return ["TEST-{0}".format(testNum), SCORES.NOT_IMPLEMENTED, msgIfNotImplemented]
    ovrScore = SCORES.minScore(listScores)
    scoreString = ', '.join([f"p{i+1:02d}:{partScore}" for i,partScore in enumerate(listScores)])

    return ["TEST-{0}".format(testNum), ovrScore, scoreString]

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
