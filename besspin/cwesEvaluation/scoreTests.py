#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring the CWEs
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import os, glob, sys
from importlib.machinery import SourceFileLoader
import enum, re
from besspin.base.utils.misc import *
import besspin.base.config

VUL_CLASSES = ["bufferErrors", "PPAC", "resourceManagement", "informationLeakage", "numericErrors", "hardwareSoC", "injection"]

class SCORES (enum.Enum):
    """
    An enum representing the possible score values for a CWE test.
    See ${repo}/docs/cwesEvaluation/besspinPhilosophy.md for an explanation of
    each score.
    """
    NINF = -10
    NOT_APPLICABLE = -4
    NOT_IMPLEMENTED = -3
    FAIL = -2
    CALL_ERR = -1
    HIGH = 0
    MED = 1
    LOW = 2
    NONE = 3
    DETECTED = 4 #The value of DETECTED will be overridden to be 3 (= NONE)
    INF = 10

    def __str__ (self): #to replace '_' by '-' when printing
        """
        Convert this SCORE to a String.

        RETURNS:
        --------
            A string representation of this score.
        """
        if (self.name == "NOT_IMPLEMENTED"):
            return "NoImpl"
        elif (self.name == "NOT_APPLICABLE"):
            return "N/A"
        else:
            return "%s" % self.name.replace('_','-')

    @property
    def value(self):
        """
        DETECTED and NONE should have the same value, but setting two ENUM constants to the same value means one of them
        is an alias to the other. Which we don't want for clarity; To distinguish between the NONE and DETECTED
        concepts. This makes NONE and DETECTED have the same value for the sake of averaging or any value related
        operations. Average will thus never yield DETECTED, but rather NONE. So you can see individual test parts be
        scored DETECTED, but the overall CWE score will be NONE.
        """
        if (self.name == "DETECTED"):
            return self.__class__["NONE"]._value_
        else:
            return self._value_

    def __lt__(self, other):
        """
        Less than operator.

        ARGUMENTS:
        ----------
            other : SCORE
                Score to compare against.

        RETURNS:
        --------
            True iff the integer value of <self> is less than the integer value
            of <other>.
        """
        if (str(self.__class__) == str(other.__class__)):
            return self.value < other.value
        logAndExit (f"SCORES: __lt__ not implemented for inputs of type {type(self)} and {type(other)}.",exitCode=EXIT.Dev_Bug)

    def __gt__(self, other):
        """
        Greater than operator.

        ARGUMENTS:
        ----------
            other : SCORE
                Score to compare against.

        RETURNS:
        --------
            True iff the integer value of <self> is greater than the integer
            value of <other>.
        """
        if (str(self.__class__) == str(other.__class__)):
            return self.value > other.value
        logAndExit (f"SCORES: __lt__ not implemented for inputs of type {type(self)} and {type(other)}.",exitCode=EXIT.Dev_Bug)

    def __len__(self):
        """
        Get the length of this SCORE.

        RETURNS:
        --------
            The length of the string representation of this score.
        """
        return len(str(self))

    @staticmethod
    def minScore (scoreList):
        """
        Get the lowest score in a list of scores.

        ARGUMENTS:
        ----------
            scoreList : List of SCORES
                List of scores to find the minimum of.

        RETURNS:
        --------
            The lowest SCORES object in <scoreList>.
        """
        minScore = SCORES.INF
        for xScore in scoreList:
            if (xScore < minScore):
                minScore = xScore
        return minScore

    @classmethod
    def avgScore (cls,scoreList): #Always floors
        """
        Return the floor of the average of a list of scores.

        ARGUMENTS:
        ----------
            scoreList : List of SCORES
                List of scores to compute the average over.

        RETURNS:
        --------
            The average SCORES object in <scoreList>.
        """
        sumScores = 0
        for xScore in scoreList:
            sumScores += xScore.value
        avgValue = sumScores // len(scoreList)
        return cls(avgValue)

    @classmethod
    def weightedAvgScore (cls, scoreList, partsWeights):
        minScore = cls.minScore(scoreList)
        if (minScore < cls.HIGH): #One of the parts has an error --> error
            return minScore
        sumScores = 0
        for xScore, xWeight in zip(scoreList, partsWeights):
            sumScores += xWeight * xScore.value
        avgValue = sumScores // sum(partsWeights)
        return cls(avgValue)

    @classmethod
    def toScore (cls, strScore):
        """
        Convert a string representation of a score to a SCORES object.

        ARGUMENTS:
        ----------
            strScore : String
                String to convert to a SCORES object.

        RETURNS:
        --------
            A SCORES object corresponding to <strScore>.
        """
        return cls[getSettingDict('cwesAssessments',[strScore])]

    @classmethod
    def toTableExactRepr (cls, score):
        """
        Translate the score to the string representation in the table as normalized exact score (2nd score column)
        """
        if ((score > cls.DETECTED) or (score < cls.HIGH)):
            return '-'
        else:
            return str(score.value/cls.DETECTED.value)

@decorate.debugWrap
def scoreTests(vulClass, logsDir, title, doPrint=True, reportFileName="scoreReport.log"):
    """
    Score all test logs in a given directory.

    ARGUMENTS:
    ----------
        vulClass : String
            Vulnerability class to score.

        logsDir : String
            Directory of log files to score.

        title : String
            Title to use for score output table.

        doPrint : Boolean
            Whether to print score results to the screen.

        reportFileName : String
            File to append score tables to.

    SIDE-EFFECTS:
    -------------
        - Appends score tables to ${workDir}/<reportFileName>.
        - Writes CSV score file to <logsDir>/scores.csv.
        - Writes INI config file to <logsDir>/<vulClass>.ini.
        - If ${runningMultitaskingTests} is disabled, stores scores in
          ${cweScores}[<vulClass>].  These scores are a dictionary from CWE
          name to SCORES object.
        - If <doPrint> is <True>, prints a score table to the screen.

    RETURNS:
    --------
        A tuple of (Dictionary of String to SCORES, List of String).  In order,
        the elements of this tuple are:
            0. A mapping from CWE names to SCORES the tests for those CWEs
               received.
            1. The cells of the score table.  Each element represents a row,
               and each element of each row represents a cell in that row.
    """
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
    scorerModulePath = os.path.join(getSetting("repoDir"),"besspin","cwesEvaluation",vulClass,"cweScores.py")
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
        xConfig.add_section(besspin.base.config.CWES_SELF_ASSESSMENT_SECTION)
        if (vulClass not in ["bufferErrors", "informationLeakage"]):
            xConfig.add_section(besspin.base.config.CWES_ENABLED_TESTS_SECTION)
        try:
            for row in rows:
                cweName = f"{'-'.join(row[0].split('-')[1:])}"
                cweNameD = cweName.replace('-','_')
                scoresDict[cweNameD] = row[1]
                xConfig.set(besspin.base.config.CWES_SELF_ASSESSMENT_SECTION,f"assessment_{cweNameD}",f"{row[1]}")
                if (vulClass not in ["bufferErrors", "informationLeakage"]):
                    xConfig.set(besspin.base.config.CWES_ENABLED_TESTS_SECTION,f"test_{cweNameD}",'No') #already tested
                fcsv.write(f"{cweName},{row[1]},{row[1].value},{row[2]},\"{row[3]}\"\n")
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
    """
    Render a two dimensional list as an ASCII table.

    ARGUMENTS:
    ----------
        elements : List of List of String
            The rows of the table to render.  Each element represents a row,
            and each element of each row represents a cell in that row.

        vulClass : String
            The vulnerability class the scores in this table belong to.

        title : String
            The title to add to the top of the table.

        hasMultitaskScores : Boolean
            Whether or not the <elements> contains a column at the end
            consisting of multitasking scores.

    RETURNS:
    --------
        A list of strings where each element represents one line in the output.
    """
    table = []

    headers = ["CWE","Score","Score","Notes"]
    if hasMultitaskScores:
        headers.append("Multitasking Pass")

    # prettify elements
    for iRow in range(len(elements)):
        elements[iRow][0] = elements[iRow][0].replace("TEST","CWE") #To ensure consistency
        try:
            val = float(elements[iRow][2])
            elements[iRow][2] = f"{100*val:.2f}%"
        except:
            pass

    # fullElements contains the headers as well so that the width computation
    # takes header width into account
    fullElements= [headers] + elements

    if hasMultitaskScores:
        widths = [ (len(e[0]), len(e[1]), len(e[2]), len(e[3]), len(e[4])) for e in fullElements]
    else:
        widths = [ (len(e[0]), len(e[1]), len(e[2]), len(e[3])) for e in fullElements ]
    widthCols = [ 2 + max([w[i] for w in widths]) for i in range(len(widths[0]))]

    # Draw title header
    table.append(tabulate_row([],widthCols,drawLine=True))
    table.append(tabulate_row([title], [sum(widthCols) + len(widths[0]) - 1]))
    table.append(tabulate_row([],widthCols,drawLine=True))

    # Draw the header (one column less)
    headers.remove("Score")
    headersWidthCols = [widthCols[0], 1 + sum(widthCols[1:3])] + widthCols[3:]
    table.append(tabulate_row(headers, headersWidthCols))
    table.append(tabulate_row([],headersWidthCols,drawSeparation=True))

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
def tabulate_row(elements,widthCols,drawLine=False,drawSeparation=False,
                customSeparations=None,horizSeparator='-'):
    """
    Render a line in an ASCII table.

    ARGUMENTS:
    ----------
        elements : List of String
            A single row of a table.  Each element represents a cell in the
            row.  This argument is ignored if either <drawLine> or
            <drawSeparation> is True.  Otherwise, <elements> must contain the
            same number of elements as <widthCols>.

        widthCols : List of Int
            The width in characters of each cell in the ASCII representation of
            the table.

        drawLine : Boolean
            Whether to render a line consisting solely of "-".

        drawSeparation : Booean
            Whether to draw a separator line, such as between rows.  This has
            no effect if <drawLine> is True.

        customSeparations : Optional List of Boolean
            If <drawSeparation> is True, this parameter controls whether to
            draw <horizSeparator> for each column in the row.  The list should
            be the same length as <widthCols>.  Passing <None> for this
            parameter is equivalent to passing a list consisting of <True> for
            every element.

        horizSeparator : String
            If <drawSeparation> is True, this parameter specifies the character
            to use when drawing the horizontal separator.

    RETURNS:
    --------
        A string rendering of <elements>.
    """
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
    """
    Score a test part as specified in the ${customizedScoring} config section.
    If ${customizedScoring}[${useCustomFunction}] is enabled, the custom
    scoring function will be used and all other custom scoring options will be
    ignored.  Otherwise, the score will be computed using the other settings in
    ${customizedScoring}.

    ARGUMENTS:
    ----------
        lines : List of String
            Output from running the test part.

    RETURNS:
    --------
        A SCORES instance representing the custom score.
    """
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
    """
    If ${useCustomScoring} is enabled, this function custom scores a test and
    returns the better score between the custom and default score.  If
    ${useCustomScoring} is disabled, this function returns the default score.

    ARGUMENTS:
    ----------
        lines : List of String
            Log output from the test.

        defaultScore : SCORES
            Default test score.

    RETURNS:
    --------
        If ${useCustomScoring} is enabled:
            - Returns whichever is better between the custom score and
              <defaultScore>.
        Else:
            - Returns <defaultScore>.
    """
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
    """
    Pretty format a vulnerability class string.

    ARGUMENTS:
    ----------
        vulClass : String
            Vulnerability class to pretty format.

    RETURNS:
    --------
        A pretty formatted representation of <vulClass>.
    """
    caps = list(filter(lambda c: c.isupper(), vulClass))
    iFirstCap = vulClass.find(caps[0]) if(caps) else -1
    if (iFirstCap<=0):
        return vulClass[0].upper() + vulClass[1:]
    else:
        return vulClass[0].upper() + vulClass[1:iFirstCap] + ' ' + vulClass[iFirstCap:]
