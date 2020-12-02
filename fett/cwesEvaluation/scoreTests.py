#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring the CWEs
- UNKNOWN: One of the following:
    -- FAIL: the test did not run or could not be parsed or any other weird error.
    -- CALL-ERR: call error to the sys call or module needed for that test
    -- DoS: The test is denied though didn't breach yet. Impractical hardware.
- SCALE: NONE (no weakness) -> V-LOW -> LOW -> MED -> HIGH -> V-HIGH

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import os
import glob
import sys
from importlib.machinery import SourceFileLoader
import enum
import re

from fett.base.utils.misc import *

class SCORES (enum.Enum):
    NINF = -10
    RECOMMEND = -7
    NOT_IMPLEMENTED = -6
    UNKNOWN = -5
    INVALID = -4
    FAIL = -3
    DOS = -2
    CALL_ERR = -1
    V_HIGH = 0
    HIGH = 1
    MED = 2
    LOW = 3
    V_LOW = 4
    DETECTED = 5
    NONE = 6
    INF = 10

    def __str__ (self): #to replace '_' by '-' when printing
        if (self.name == "NOT_IMPLEMENTED"):
            return "N/A"
        else:
            return "%s" % self.name.replace('_','-')

    def __lt__(self, other):
        if (str(self.__class__) == str(other.__class__)):
            return self.value < other.value
        logAndExit (f"SCORES: __lt__ not implemented for inputs of type {type(self)} and {type(other)}.",exitCode=EXIT.Dev_Bug)

    def __gt__(self, other):
        if (str(self.__class__) == str(other.__class__)):
            return self.value > other.value
        logAndExit (f"SCORES: __lt__ not implemented for inputs of type {type(self)} and {type(other)}.",exitCode=EXIT.Dev_Bug)

    def __len__(self):
        return len(str(self))

    def minScore (scoreList): #Note that no need for 'self' here; it's used as a function
        minScore = SCORES.INF
        for xScore in scoreList:
            if (xScore < minScore):
                minScore = xScore
        return minScore

    def avgScore (scoreList,ignoreErrors=False): #Always floors
        sumScores = 0
        for xScore in scoreList:
            if not (ignoreErrors and (xScore.value<SCORES.V_HIGH.value)):
                sumScores += xScore.value
        avgValue = sumScores // len(scoreList)
        return SCORES(avgValue)

@decorate.debugWrap
def scoreTests(scorerModule, csvPath, logsDir):
    reportFileName = os.path.join(getSetting("workDir"), "scoreReport.log")
    fScoresReport = ftOpenFile(reportFileName, 'a')
    try:
        setSetting("reportFile", fScoresReport)
    except Exception as exc:
        logAndExit("<scoreTests>: Failed to open the report file "
                   f"<{reportFileName}> to append.",
                   exitCode=EXIT.Files_and_paths,
                   exc=exc)

    # Get all the log files
    logs = [(os.path.basename(f).split('.')[0], f) for f in glob.glob(os.path.join(logsDir, '*.log'))]
    rows = scorerModule.scoreAllTests(logs)
    if (len(rows) < 1): #nothing to score
        warnAndLog("<scoreTests>: There are no logs to score.")
    else:
        # output a csv file
        try:
            fcsv = ftOpenFile(csvPath, "w")
            for row in rows:
                fcsv.write(f"{row[0].split('-')[1]},{row[1]},{row[1].value},{row[2]}\n")
            fcsv.close()
        except Exception as exc:
            logAndExit(f"<scoreTests> Failed to generate the csv output "
                       f"file <{csvPath}>.",
                       exc=exc,
                       exitCode=EXIT.Files_and_paths)
        # Build table for scoring
        for row in tabulate(rows):
            printAndLog(row, tee=fScoresReport)

    fScoresReport.close()

@decorate.debugWrap
def tabulate(elements):
    table = []
    widths = [ (len(e[0]), len(e[1]), len(e[2])) for e in elements ]
    widthCols = [ 2 + max([w[i] for w in widths]) for i in range(0,3) ]

    # Draw Column Headers
    table.append(tabulate_row([],widthCols,drawLine=True))
    table.append(tabulate_row(["TEST","Score","Notes"],widthCols))
    table.append(tabulate_row([],widthCols,drawLine=True))

    # Draw each result
    firstRow = True
    for row in elements:
        if (not firstRow):
            table.append(tabulate_row([],widthCols,drawSeparation=True))
        else:
            firstRow = False
        table.append(tabulate_row(row, widthCols))

    # Draw bottom edge
    table.append(tabulate_row([],widthCols,drawLine=True))
    return table

@decorate.debugWrap
def tabulate_row(elements,widthCols,drawLine=False,drawSeparation=False):
    def centralize (msg, width):
        if (len(msg)>width):
            return '|' + msg[:width]
        spaces = width - len(msg)
        leadingSpaces = spaces//2
        laggingSpaces = (spaces-1)//2+1
        return '|' + ' '*leadingSpaces + msg + ' '*laggingSpaces

    if (drawLine):
        message = ' ' + '-'*(sum(widthCols)+2) + ' '
    elif (drawSeparation):
        message = '|' + '-'*widthCols[0] + '|' + '-'*widthCols[1] + '|' + '-'*widthCols[2] + '|'
    else:
        message = centralize(elements[0],widthCols[0]) + centralize(str(elements[1]),widthCols[1]) + centralize(elements[2],widthCols[2]) + '|'
    return (message)

@decorate.debugWrap
def customScorePart (lines): #should return: NINF (for PASS), DETECTED, or NONE (for prevented)
    
    #checking custom function -- it overrides the other options.
    if (isEnabledDict('customizedScoring','useCustomFunction')): #use custom function
        customScorerFuncOut = os.path.join(getSetting('workDir'),'customScorerFunction.out')
        pathToCustomFunction = getSettingDict('customizedScoring','pathToCustomFunction')
        try:
            with redirectPrintToFile(customScorerFuncOut): #disable print
                customModule = SourceFileLoader("customScorerModule", pathToCustomFunction).load_module()
        except Exception as exc:
            warnAndLog(f"<customScorer>: Failed to load custom scorer "
                       "module. Ignoring the option.",
                       exc=exc)
            return SCORES.NINF
        try:
            with redirectPrintToFile(customScorerFuncOut): #disable print
                retScore = customModule.main(lines,SCORES)
        except Exception as exc:
            warnAndLog(f"<customScorer>: Failed to score using main in "
                       f"<{pathToCustomFunction}>.",
                       exc=exc)
            return SCORES.NINF
        return retScore

    for line in lines:
        #checking stdoutKeywords and gdbKeywords
        for keyword in getSettingDict('customizedScoring','stdoutKeywords') + getSettingDict('customizedScoring','gdbKeywords'):
            if (keyword in line):
                return SCORES.DETECTED
        #checking funcCheckpoints
        if ('<GDB-CHECKPOINT>' in line):
            return SCORES.DETECTED
        #checking memValues
        memMatch = re.match(r"^\d+\: /x \* \(int \*\) 0x(?P<memAddress>[abcdef\d]{8}) = 0x(?P<memValue>[abcdef\d]{1,8})\s*$",line)
        if (memMatch is not None):
            if (int(memMatch.group('memAddress'),16) != getSettingDict('customizedScoring','memAddress')):
                warnAndLog("<customScorer>: Encountered unexpected "
                           f"memory address in the GDB line <{line}>. Was "
                           "expecting "
                           f"<0x{getSettingDict('customizedScoring','memAddress'):08x}>.")
            else: #This is fine
                memValue = int(memMatch.group('memValue'),16)
                if (memValue == getSettingDict('customizedScoring','memResetValue')):
                    continue
                elif (getSettingDict('customizedScoring','memViolationValues') == ['ALL']):
                    return SCORES.DETECTED
                else:
                    for memViolationValue in getSettingDict('customizedScoring','memViolationValues'):
                        if (memValue == memViolationValue):
                            return SCORES.DETECTED

    return SCORES.NINF

@decorate.debugWrap
def adjustToCustomScore (lines,defaultScore):
    if (not isEnabled('useCustomScoring')):
        return defaultScore
    customScore = customScorePart(lines)
    if ((customScore == SCORES.DETECTED) and (defaultScore == SCORES.CALL_ERR)): #The test was prevented from continuing
        return SCORES.NONE #PREVENTED
    elif (customScore > defaultScore):
        return customScore 
    else:
        return defaultScore
