#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
helpers functions for scoring the CWE tests
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import re

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore

def getOsImage (lines,testNum=None):
    warnText = "" if (testNum is None) else " in test_{0}.log".format(testNum)
    for line in lines:
        lineMatch = re.match(r'^<OSIMAGE=(?P<osImage>\w+)>$',line)
        if (lineMatch is not None):
            return lineMatch.group('osImage')
    print ("Error: Could not determine <osImage>{0}.".format(warnText))
    return "NoOsImageFound"

def regPartitionTest (logLines,nParts,testNum=None):
    partsLines = {}
    for iPart in range(1,nParts+1):
        start = f"---Part{iPart:02d}:"
        end = f"---Part{iPart+1:02d}:" if (iPart<nParts) else "NO-NEED-TO-DETECT-AN-ENDING"
        partsLines[iPart] = partitionLines(logLines,start,end,testNum=testNum,doPrintWarnings=False)
    return partsLines

def regPartitionTestFreeRTOS (logLines,nParts,testNum=None):
    partsLines = {}
    for iPart in range(1,nParts+1):
        start = f"---Part{iPart:02d}:"
        end = "---Part{:02d}:".format(iPart+1) if (iPart<nParts) else "NO-NEED-TO-DETECT-AN-ENDING"
        partsLines[iPart] = partitionLines(logLines,start,end,testNum=testNum,doPrintWarnings=False)
        #print(partsLines[iPart])
    return partsLines

def partitionLines (lines,start,end,testNum=None,doPrintWarnings=True):
    warnText = "" if (testNum is None) else " in test_{0}.log".format(testNum)
    startFound = False
    iStart = 0
    isError = False
    iEnd = len(lines)-1
    for iLine,line in enumerate(lines):
        if (start in line):
            if (startFound):
                print ("Warning: part start <{0}> found again{1}.".format(start,warnText))
            startFound = True
            iStart = iLine

        # if (startFound and (end in line)):
        #     iEnd = iLine
        #     return lines[iStart:iEnd+1]
        # if("Error" in line):
        #     lines += ">>>End of Testgen<<<"
        #     return lines[iStart:iEnd+1]
        if (startFound):
            if (isinstance(end,str)): #only one string
                if (end in line):
                    iEnd = iLine
                    return lines[iStart:iEnd+1]
            else:
                for xEnd in end:
                    if (xEnd in line):
                        iEnd = iLine
                        return lines[iStart:iEnd+1]

    if (startFound):
        warnAndLog ("partitionLines: part end <{0}> not found{1}.".format(end,warnText),doPrint=doPrintWarnings)
        return lines[iStart:iEnd+1]   
    else:
        warnAndLog ("partitionLines: part start <{0}> not found{1}.".format(start,warnText))
        return []

def overallScore (listScores, testNum):
    if (len(listScores)==0): #not implemented
        return ["TEST-{0}".format(testNum), SCORES.NOT_IMPLEMENTED, "Not Implemented"]
    ovrScore = SCORES.minScore(listScores)
    scoreString = ', '.join([f"p{i+1:02d}:{partScore}" for i,partScore in enumerate(listScores)])

    return ["TEST-{0}".format(testNum), ovrScore, scoreString]

def doesKeywordExist (lines, keyword):
    for line in lines:
        if (keyword in line):
            return True
    return False

