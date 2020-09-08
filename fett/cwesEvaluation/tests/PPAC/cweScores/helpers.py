#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
helpers functions for scoring the CWE tests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import re
from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore

def readLogLines (logTest,testsDir):
    fLog = ftOpenFile("{0}/{1}".format(testsDir,logTest),"r")
    lines = fLog.read().splitlines()
    fLog.close()
    return lines

def getOsImage (lines,testNum=None):
    warnText = "" if (testNum is None) else " in test_{0}.log".format(testNum)
    for line in lines:
        lineMatch = re.match(r'^<OSIMAGE=(?P<osImage>\w+)>$',line)
        if (lineMatch is not None):
            return lineMatch.group('osImage')
    errorAndLog("<PPAC scores> Could not determine <osImage>{0}.".format(warnText))
    return "NoOsImageFound"

def regPartitionTest (testLines,nParts,testNum=None):
    partsLines = {}
    for iPart in range(1,nParts+1):
        start = f"---Part{iPart:02d}:"
        end = f"---Part{iPart+1:02d}:" if (iPart<nParts) else "-"*50
        partsLines[iPart] = partitionLines(testLines,start,end,testNum=testNum,doPrintWarnings=False)
    return partsLines

def matchLines(testLines, reString):
    for line in testLines:
        lineMatch = re.match(reString, line)
        if lineMatch is not None:
            yield lineMatch

def partitionLines (lines,start,end,testNum=None,doPrintWarnings=True):
    warnText = "" if (testNum is None) else " in test_{0}.log".format(testNum)
    startFound = False
    iStart = 0
    iEnd = len(lines)-1
    for iLine,line in enumerate(lines):
        if (start in line):
            if (startFound):
                warnAndLog("<PPAC scores>: part start <{0}> found again{1}.".format(start,warnText),doPrint=doPrintWarnings)
            startFound = True
            iStart = iLine
        if (startFound and (end in line)):
            iEnd = iLine
            return lines[iStart:iEnd+1]
    if (startFound):
        warnAndLog("<PPAC scores>: part end <{0}> not found{1}.".format(end,warnText),doPrint=doPrintWarnings)
        return lines[iStart:iEnd+1]   
    else:
        warnAndLog("<PPAC scores>: part start <{0}> not found{1}.".format(start,warnText),doPrint=doPrintWarnings)
        return []

def scoreGrantedDenied (SCORES, lines,lastGranted=False):
    #lastGranted: if it is True, then if granted at last, counts as granted. Otherwise, one denied gives a denied.
    isGranted = True
    isTestLegit = False
    for line in lines:
        if ("<INVALID>" in line):
            return SCORES.CALL_ERR
        if ("<GRANTED>" in line):
            isTestLegit = True
            if (lastGranted):
                isGranted = True
        if ("<DENIED>" in line):
            isTestLegit = True
            isGranted = False
    if (isTestLegit):
        return isGranted
    else:
        return SCORES.FAIL

def overallScore (listScores, testNum,msgIfNotImplemented="Not Implemented"):
    if (len(listScores)==0): #not implemented
        return ["TEST-{0}".format(testNum), SCORES.NOT_IMPLEMENTED, msgIfNotImplemented]
    ovrScore = SCORES.minScore(listScores)
    scoreString = ', '.join([f"p{i+1:02d}:{partScore}" for i,partScore in enumerate(listScores)])

    return ["TEST-{0}".format(testNum), ovrScore, scoreString]

def SendRecvCheck (lines,testNum=None):
    warnText = "" if (testNum is None) else " in test_{0}.log".format(testNum)
    targetRecv = ''
    hostRecv = ''
    for line in lines:
        if ((len(targetRecv)==0)):
            targetMatch = re.match(r'^(?P<targetRecv>[\w\-\.]+):<TARGET-RECV>$',line)
            if (targetMatch is not None):
                targetRecv = targetMatch.group('targetRecv')
        else:
            hostMatch = re.match(r'^<HOST-RECV>:(?P<hostRecv>[\w\-\.]+)$',line)
            if (hostMatch is not None):
                hostRecv = hostMatch.group('hostRecv')
                break
    return ((targetRecv==hostRecv) and (len(targetRecv)>0))

def doesKeywordExist (lines, keyword):
    for line in lines:
        if (keyword in line):
            return True
    return False

