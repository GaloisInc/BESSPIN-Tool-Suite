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
        return NotImplemented

    def __gt__(self, other):
        if (str(self.__class__) == str(other.__class__)):
            return self.value > other.value
        return NotImplemented

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

class redirectPrintToFile:
    def __init__(self,reportFile=None):
        self.reportFile = reportFile

    def __enter__(self):
        self._original_stdout = sys.stdout
        if (self.reportFile is None): #just disable
            sys.stdout = open(os.devnull, 'w')
        else:
            sys.stdout = self.reportFile

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (self.reportFile is None):
            sys.stdout.close()
        sys.stdout = self._original_stdout


def tryScoreTest(scorerModule, customScorer, testName, logTest, testsDir):
    try:
        return getattr(getattr(scorerModule,testName),testName)(SCORES, customScorer, logTest, testsDir)
    except AttributeError as e:
        return scorerModule.scoreTest(SCORES, customScorer, testName, logTest, testsDir)
    except AttributeError as e:
        printAndLog(e)
        throw(e)

def scoreLogs(scorerModule, customScorer, logs, testsDir):
    try:
        return scorerModule.scoreAllTests(SCORES, customScorer, logs, testsDir)
    except AttributeError as e:
        ret = []
        for testName, log in logs:
            try:
                ret.append(tryScoreTest(scorerModule, customScorer, testName, log, testsDir))
            except:
                report ("Error in {0}: Failed to parse <{1}>.".format(testName,log))
                testNum = testName.split('_')[1]
                ret.append(["TEST-{0}".format(testNum), SCORES.FAIL, "Failed to Score!"])
    return ret

def main (scorerModule, customScorer, csvPath):
    reportFileName = os.path.join(getSetting("workDir"), "scoreReport.log")
    # TODO: Is there a better way to set this report file?
    global reportFile
    try:
        reportFile = open(os.path.join(getSetting("workDir"),
                                       "scoreReport.log"),
                          'a')
    except Exception as exc:
        # TODO: I don't think filename is defined if we don't go through
        # __main__...  Check this file for globals and fix them
        logAndExit("<scoreTests.main>: Failed to open the report file "
                   f"<{reportFileName}> to append.",
                   exitCode=EXIT.Files_and_paths,
                   exc=exc)

    # Get all the log files
    testsDir = getSetting("cwesEvaluationLogDir")
    contents = sorted(os.listdir(testsDir))
    logs = [(f.split('.')[0], f) for f in contents if f.endswith(".log")]
    rows = scoreLogs(scorerModule, customScorer, logs, testsDir)
    if (len(rows) < 1): #nothing to score
        report (f"Warning in {fileName}: There are no logs to score.")
    else:
        # output a csv file
        try:
            fcsv = open (csvPath, "w")
            for row in rows:
                fcsv.write(f"{row[0].split('-')[1]},{row[1]},{row[1].value},{row[2]}\n")
            fcsv.close()
        except Exception as exc:
            logAndExit(f"<scoreTests.main> Failed to generate the csv output "
                       f"file <{csvPath}>.",
                       exc=exc,
                       exitCode=EXIT.Files_and_paths)
        # Build table for scoring
        for row in tabulate(rows):
            printAndLog(row, tee=reportFile)


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

class customScorerObj:
    def __init__(self, useCustomScoring, customScoringConfigFile):
        self.isCustomized = useCustomScoring
        if (self.isCustomized):
            self.parseConfigFile(customScoringConfigFile)

    def parseConfigFile (self,customScoringConfigFile):
        try:
            fConfig = open(customScoringConfigFile,"r")
            configLines = fConfig.read().splitlines()
            fConfig.close()
        except Exception as exc:
            logAndExit(f"<customScoreObj>: Failed to read the custom scoring "
                       f"configuration file <{customScoringConfigFile}>.",
                       exc=exc,
                       exitCode=EXIT.Files_and_paths)
        self.configDict = {}
        for line in configLines:
            items = line.split('=')
            self.configDict[items[0]] = items[1].strip('\"')

        for keywords in ['stdoutKeywords', 'gdbKeywords', 'funcCheckpoints', 'memViolationValues']:
            if ((keywords in self.configDict) and (len(self.configDict[keywords])>0)):
                self.configDict[keywords] = self.configDict[keywords].split(" ")
            else:
                self.configDict[keywords] = []

    def scorePart (self,lines): #should return: NINF (for PASS), DETECTED, or NONE (for prevented)
        if (not self.isCustomized):
            return SCORES.NINF

        #checking custom function -- it overrides the other options.
        if (self.configDict['useCustomFunction'] == '1'): #use custom function
            try:
                with redirectPrintToFile(reportFile): #disable print
                    customModule = SourceFileLoader("customScorerModule", self.configDict['pathToCustomFunction']).load_module()
            except Exception as exc:
                warnAndLog(f"<customScoreObj>: Failed to load custom scorer "
                           "module. Ignoring the option.",
                           exc=exc)
                return SCORES.NINF
            try:
                with redirectPrintToFile(reportFile): #disable print
                    retScore = customModule.main(lines,SCORES)
            except Exception as exc:
                warnAndLog(f"<customScoreObj>: Failed to score using main in "
                           f"<{self.configDict['pathToCustomFunction']}>.",
                           exc=exc)
                return SCORES.NINF
            return retScore

        for line in lines:
            #checking stdoutKeywords and gdbKeywords
            for keywords in ['stdoutKeywords', 'gdbKeywords']:
                for keyword in self.configDict[keywords]:
                    if (keyword in line):
                        return SCORES.DETECTED
            #checking funcCheckpoints
            if ('<GDB-CHECKPOINT>' in line):
                return SCORES.DETECTED
            #checking memValues
            memMatch = re.match(r"^\d+\: /x \* \(int \*\) 0x(?P<memAddress>[abcdef\d]{8}) = 0x(?P<memValue>[abcdef\d]{1,8})\s*$",line)
            if (memMatch is not None):
                if (int(memMatch.group('memAddress'),16) != int(self.configDict['memAddress'])):
                    warnAndLog("<customScorerObj>: Encountered unexpected "
                               f"memory address in the GDB line <{line}>. Was "
                               "expecting "
                               f"<0x{int(self.configDict['memAddress']):08x}>.")
                else: #This is fine
                    memValue = int(memMatch.group('memValue'),16)
                    if (memValue == int(self.configDict['memResetValue'])):
                        continue
                    elif (self.configDict['memViolationValues'] == ['ALL']):
                        return SCORES.DETECTED
                    else:
                        for memViolationValue in self.configDict['memViolationValues']:
                            if (memValue == int(memViolationValue)):
                                return SCORES.DETECTED

        return SCORES.NINF

    def adjustToCustomScore (self,lines,defaultScore):
        customScore = self.scorePart(lines)
        if ((customScore == SCORES.DETECTED) and (defaultScore == SCORES.CALL_ERR)): #The test was prevented from continuing
            return SCORES.NONE #PREVENTED
        elif (customScore > defaultScore):
            return customScore 
        else:
            return defaultScore
        

# TODO: Remove this main function
# scoreTests.py module_name module_path class_name tests_dir
if __name__ == '__main__':
    fileName = os.path.basename(__file__)
    nArgs = 6 #0:thisFile 1:ScorerModulePath 2:testsDir 3:reportFile 4:useCustomScoring 5:customScoringConfigFile
    if (len(sys.argv) != nArgs):
        print(f"Error in {fileName}: Wrong number of arguments [!= {nArgs}] passed to the scorer.")
        exit (1)
    modulePath = sys.argv[1]
    testsDir   = sys.argv[2]

    try:
        reportFile = open(sys.argv[3], "a")
    except:
        print(f"Error in {fileName}: Failed to open the report file <{sys.argv[3]}> to append.")
        exit (1)

    try:
        scorerModule = SourceFileLoader("scorer", modulePath).load_module()
    except:
        report(f"Error in {fileName}: Failed to load the scorer module <{modulePath}>.")
        exit (1)

    customScorer = customScorerObj(sys.argv[4]=='1',sys.argv[5])

    csvPath = os.path.dirname(sys.argv[3]) + "/scores.csv"

    main (scorerModule, customScorer, csvPath)
    reportFile.close()

