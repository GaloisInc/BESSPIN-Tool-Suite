#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring functions for each CWE test
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """


## The expected format of a test score in the log file is
## SCORE:XXX:Y:Result
##
## where "XXX" is the test CWE number - a 3 or 4 digit integer
##       "Y" is the part number within that particular test, expected to be a small
##           integer starting at 1
##       "Result" is one of
##           "TEST PASSED"
##           "TEST FAILED"
##           and so on... see scoreTestPart() below for all the strings that
##           are recognized.
##
## Example
##
## SCORE:234:2:TEST FAILED
##
## indicates that part 2 of the test for CWE 234 is a "TEST FAILED" result

import re

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
from fett.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests

VULCLASS = "numericErrors"

@decorate.debugWrap
def partitionLines (lines,testPart,testNum):
    startFound = False
    iStart = 0
    iEnd = len(lines)-1
    start = f"TEST {testNum} PART P{testPart:02d}"
    end = f"TEST {testNum} PART P{(testPart+1):02d}"
    for iLine,line in enumerate(lines):
        if (start in line):
            startFound = True
            iStart = iLine
        if (startFound and (end in line)):
            iEnd = iLine
            return lines[iStart:iEnd+1]
    if (startFound):
        return lines[iStart:iEnd+1]
    else:
        return []

## NAME FORMAT IS: test_DDD((__D*_D*)|[_D*])
## Test Variant and SEED parts are not currently used in the Numeric_Errors tests
@decorate.debugWrap
def scoreAllTests(logs):
    if (isEnabledDict(VULCLASS,"useSelfAssessment")):
        return defaultSelfAssessmentScoreAllTests(VULCLASS, logs)

    scores = {}
    for name, log in logs:
        testNum = name.split('_')[1]
        scores[testNum] = {}
        logLines = ftReadLines(log)
        nPartsMatch = matchExprInLines(r'^<NUMPARTS=(?P<numParts>\d+)>$',logLines)
        if (nPartsMatch is None):
            errorAndLog(f"Failed to score {name}.",doPrint=False)
            scores[testNum][1] = SCORES.FAIL
            continue

        numParts = int(nPartsMatch.group('numParts'))

        for thisPart in range(1, numParts + 1):
            partLines = partitionLines (logLines,thisPart,testNum) #partitioning first make sure the scoring is done for this part only
            thisScore = scoreTestPart(partLines, testNum, thisPart)
            scores[testNum][thisPart] = adjustToCustomScore(partLines,thisScore)


    ret = []
    for testNum in scores:
        xScores = scores[testNum].values()
        ret.append([f"TEST-{testNum}", SCORES.minScore(xScores),', '.join([str(x) for x in xScores])])
    return ret

@decorate.debugWrap
def scoreTestPart(logLines, testNum, testPart):
    if (len(logLines) == 0):
        return SCORES.FAIL
    minScore = SCORES.INF
    for line in logLines:
        scoreMatch = re.match(rf"^SCORE:{testNum}:{testPart}:(?P<relevantString>[\w\s<>]+)$",line)
        if (scoreMatch is not None):
            keyword = scoreMatch.group('relevantString')
            if (keyword in ['TEST FAILED', 'TOP SECRET STUFF', 'SEGFAULT']):
                newScore = SCORES.HIGH
            elif (keyword in ['TEST PASSED', '<ABORT>']): ## SSITH CPU exception prevented a vulnerability
                newScore = SCORES.NONE
            elif (keyword == 'TEST ERROR'):
                newScore = SCORES.CALL_ERR
            else: #unrecognized string
                newScore = SCORES.CALL_ERR
        elif ( ('Segmentation fault' in line) or ('SEGFAULT' in line) or ('<GDB-SIGTRAP>' in line) ):
            newScore = SCORES.HIGH
        elif ('<ABORT>' in line):
            newScore = SCORES.NONE
        else:
            continue

        # if more than one SCORE line found for a particular test part,
        # then report the one with the max value
        if (newScore < minScore):
            minScore = newScore

    if (minScore == SCORES.INF):
        return SCORES.CALL_ERR
    else:
        return minScore
