#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring the CWEs
- UNKNOWN: One of the following:
    -- FAIL: the test did not run or could not be parsed or any other weird error.
    -- CALL-ERR: call error to the sys call or module needed for that test
    -- DoS: The test is denied though didn't breach yet. Impractical hardware.
- SCALE: NONE (no weakness) -> LOW ->MED -> HIGH

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import os, glob, sys
from importlib.machinery import SourceFileLoader
import enum, re
from fett.base.utils.misc import *
import fett.base.config

class SCORES (enum.Enum):
    NINF = -10
    NOT_APPLICABLE = -7
    NOT_IMPLEMENTED = -6
    UNKNOWN = -5
    INVALID = -4
    FAIL = -3
    CALL_ERR = -1
    HIGH = 0
    MED = 1
    LOW = 2
    DETECTED = 3
    NONE = 4
    INF = 10

    def __str__ (self): #to replace '_' by '-' when printing
        if (self.name == "NOT_IMPLEMENTED"):
            return "NoImpl"
        elif (self.name == "NOT_APPLICABLE"):
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

    def avgScore (scoreList): #Always floors
        sumScores = 0
        for xScore in scoreList:
            sumScores += xScore.value
        avgValue = sumScores // len(scoreList)
        return SCORES(avgValue)

    def toScore (strScore):
        # Let's be explicit and use a hardcoded 1:1 mapping
        mapToScores = {
            'HIGH' : SCORES.HIGH,
            'MED' : SCORES.MED,
            'LOW' : SCORES.LOW,
            'NONE' : SCORES.NONE,
            'DETECTED' : SCORES.DETECTED,
            'NA' : SCORES.NOT_APPLICABLE,
            'NoImpl' : SCORES.NOT_IMPLEMENTED,
            'UNKNOWN' : SCORES.UNKNOWN
        }
        if (strScore not in mapToScores):
            logAndExit(f"toScore: The string <{strScore}> is not mapped to any score.",exitCode=EXIT.Dev_Bug)
        cwesAssessmentsSet = set(getSetting('cwesAssessments'))
        cwesAssessmentsSet.add('NoImpl') #Add the exception (known divergence)
        if (set(mapToScores.keys()) != cwesAssessmentsSet):
            logAndExit(f"toScore: The mapping in this function has to match the <cwesAssessments> allowed strings",
                exitCode=EXIT.Dev_Bug) #This should prevent both structures from diverging
        return mapToScores[strScore]

@decorate.debugWrap
def scoreTests(vulClass, logsDir, title, doPrint=True, reportFileName="scoreReport.log"):
    reportFilePath = os.path.join(getSetting("workDir"), reportFileName)
    csvPath = os.path.join(logsDir, "scores.csv")
    iniPath = os.path.join(logsDir, f"{vulClass}.ini")
    if isEnabled("runningMultitaskingTests"):
        # Don't clobber previous score results
        scoresDict = {}
    else:
        scoresDict = getSettingDict("cweScores",vulClass)
    fScoresReport = ftOpenFile(reportFilePath, 'a')

    # Get all the log files
    logs = [(os.path.basename(f).split('.')[0], f) for f in sorted(glob.glob(os.path.join(logsDir, '*.log')))]
    scorerModulePath = os.path.join(getSetting("repoDir"),"fett","cwesEvaluation",vulClass,"cweScores.py")
    try:
        scorerModule = SourceFileLoader("cweScores",scorerModulePath).load_module()
    except Exception as exc:
        logAndExit(f"Failed to load the <cweScores> module for <{vulClass}>.",exc=exc,exitCode=EXIT.Dev_Bug)
    rows = sorted(scorerModule.scoreAllTests(logs))
    if (len(rows) < 1): #nothing to score
        warnAndLog("<scoreTests>: There are no logs to score.")
    else:
        # output a csv file + ini file + store the scores in the dict
        fcsv = ftOpenFile(csvPath, "w")
        xConfig = configparser.ConfigParser()
        xConfig.optionxform = str # Hack it to be case sensitive
        xConfig.add_section(fett.base.config.CWES_SELF_ASSESSMENT_SECTION)
        if (vulClass not in ["bufferErrors", "informationLeakage"]):
            xConfig.add_section(fett.base.config.CWES_ENABLED_TESTS_SECTION)
        try:
            for row in rows:
                cweName = f"{'-'.join(row[0].split('-')[1:])}"
                cweNameD = cweName.replace('-','_')
                scoresDict[cweNameD] = row[1]
                xConfig.set(fett.base.config.CWES_SELF_ASSESSMENT_SECTION,f"assessment_{cweNameD}",f"{row[1]}")
                if (vulClass not in ["bufferErrors", "informationLeakage"]):
                    xConfig.set(fett.base.config.CWES_ENABLED_TESTS_SECTION,f"test_{cweNameD}",'No') #already tested
                fcsv.write(f"{cweName},{row[1]},{row[1].value},\"{row[2]}\"\n")
            fcsv.close()
        except Exception as exc:
            logAndExit(f"<scoreTests> Failed to generate the needed files and outputs for <{vulClass}> scores.",
                       exc=exc,
                       exitCode=EXIT.Files_and_paths)
        safeDumpIniFile(xConfig,iniPath)
        # Build table for scoring
        for row in tabulate(rows, vulClass, title, False):
            printAndLog(row, tee=fScoresReport, doPrint=doPrint)

    fScoresReport.close()

    # Return dictionary mapping from CWE -> score, as well as rows of table
    return (scoresDict, rows)

@decorate.debugWrap
def tabulate(elements, vulClass, title, hasMultitaskScores):
    table = []

    headers = ["TEST","Score","Notes"]
    if hasMultitaskScores:
        headers.append("Multitasking Pass")

    # fullElements contains the headers as well so that the width computation
    # takes header width into account
    fullElements= [headers] + elements

    if hasMultitaskScores:
        widths = [ (len(e[0]), len(e[1]), len(e[2]), len(e[3])) for e in fullElements]
    else:
        widths = [ (len(e[0]), len(e[1]), len(e[2])) for e in fullElements ]
    widthCols = [ 2 + max([w[i] for w in widths]) for i in range(len(widths[0]))]

    # Draw title header
    table.append(tabulate_row([],widthCols,drawLine=True))
    table.append(tabulate_row([title], [sum(widthCols) + len(widths[0]) - 1]))
    table.append(tabulate_row([],widthCols,drawLine=True))

    # Draw each result
    firstRow = True
    for row in fullElements:
        if (not firstRow):
            table.append(tabulate_row([],widthCols,drawSeparation=True))
        else:
            firstRow = False
        table.append(tabulate_row(row, widthCols))

    # Draw bottom edge
    table.append(tabulate_row([],widthCols,drawLine=True))
    return table

@decorate.debugWrap
def tabulate_row(elements,widthCols,drawLine=False,drawSeparation=False,
                customSeparations=None,horizSeparator='-'):
    def centralize (msg, width):
        if (len(msg)>width):
            return '|' + msg[:width]
        spaces = width - len(msg)
        leadingSpaces = spaces//2
        laggingSpaces = (spaces-1)//2+1
        return '|' + ' '*leadingSpaces + msg + ' '*laggingSpaces

    if (drawLine):
        message = ' ' + '-'*(sum(widthCols)+len(widthCols)-1) + ' '
    elif (drawSeparation):
        if (customSeparations is None):
            customSeparations = [True for col in widthCols]
        elif (len(customSeparations) != len(widthCols)):
            logAndExit("tabulate_row: Invalid <customSeparations>.",exitCode=EXIT.Dev_Bug)
        message = '|' + '|'.join([(horizSeparator if sep else ' ')*width for width,sep in zip(widthCols,customSeparations)]) + '|'
    elif (len(elements) == len(widthCols)):
        message = ''.join([centralize(str(element),widthCol) for element,widthCol in zip(elements,widthCols)]) + '|'
    else:
        printAndLog(f"tabulate_row: The faulty row is <{elements}>.",doPrint=False)
        logAndExit("tabulate_row: Length mismatch between <elements> and <widhCols>.",exitCode=EXIT.Dev_Bug)
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

def prettyVulClass(vulClass):
    caps = list(filter(lambda c: c.isupper(), vulClass))
    iFirstCap = vulClass.find(caps[0]) if(caps) else -1
    if (iFirstCap<=0):
        return vulClass[0].upper() + vulClass[1:]
    else:
        return vulClass[0].upper() + vulClass[1:iFirstCap] + ' ' + vulClass[iFirstCap:]
