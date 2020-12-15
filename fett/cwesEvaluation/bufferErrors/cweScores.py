#! /usr/bin/env python3
import os
from importlib.machinery import SourceFileLoader
import math

from fett.base.utils.misc import *
import fett.cwesEvaluation.bufferErrors.count as count
from fett.cwesEvaluation.scoreTests import SCORES
from fett.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring functions for each CWE test
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""
VULCLASS = "bufferErrors"

def score(testScores):
    """
    This could use some thought. We want to compute a score for a set of BOF tests.

    - A 'trap' is a 'good' result, meaning that the overflow was 'caught' in some way.

    - Both 'timeout' and 'completed' are not so good, as they indicate the overrun was NOT caught, but
    might have altered control flow (in the timeout case).

    - 'Invalid' means, due to platform issues, a test was generated that can
    not accurately witness a buffer overrun weakness (e.g., the test requires
    more memory than the platform has available).
    """
    s = 0 # Number 's'uccessful (uncaught)
    i = 0 # Invalid
    e = 0 # err: FAIL/CALL-ERR (something went wrong with parsing -- no overall score reported)
    validScores = []
    for testScore in testScores:
        if (testScore == SCORES.INVALID):
            i += 1
        elif (testScore in [SCORES.FAIL, SCORES.CALL_ERR]): #FAIL/CALL-ERR 
            e += 1
        else:
            validScores.append(testScore)
            if (testScore < SCORES.DETECTED): #LOW --> HIGH
                s += 1
    t = len(validScores) # Total valid

    uncaughtPart = f"{s}/{t} uncaught overruns" if (t >0) else ''
    invPart = f'{i} invalid tests' if (i > 0) else ''
    failPart = f'{e} failed tests' if (e > 0) else ''
    notes = ', '.join([part for part in [uncaughtPart, invPart, failPart] if part])
    if (t == 0): #all failed or invalid
        ovrScore = SCORES.INVALID if e == 0 else SCORES.FAIL
    elif (s == 0): #all are DETECTED/NONE
        ovrScore = SCORES.avgScore(validScores)
    else: #partial score
        """ 
        - Currently, every 's' is considered as HIGH.
        - Even the baseline (non-secure) processor can block some of the buffer overflows from happening.
          This is due to the OS memory management, boundaries, etc. 
        - s=0 should be DETECTED, and s=t should be HIGH.
        """
        unadjustedScore = ((t-s)/float(t))*(SCORES.DETECTED.value-SCORES.HIGH.value) 
        if (unadjustedScore < SCORES.HIGH.value):
            ovrScore = SCORES.HIGH
        else:
            ovrScore = SCORES(math.floor(unadjustedScore))

    return (ovrScore, notes)


def scoreByCWE(rows):
    results = {}
    for row in rows:
        if 'CWE' in row:
            for cwe in row['CWE']:
                _, cweNum = cwe.split("_")
                cweNum    = f"CWE-{cweNum}"
                try:
                    results[cweNum].append(row['Result'])
                except:
                    results[cweNum] = [row['Result']]
        else:
            results[row['TestNumber']] = [row['Result']]
    tab = []
    for test in sorted(results.keys()):
        v = score(results[test])
        tab.append([f"{test}", v[0], v[1]])
    return tab

def scoreAllTests(logs):
    if (isEnabledDict(VULCLASS,"useSelfAssessment")):
        return defaultSelfAssessmentScoreAllTests(VULCLASS, logs)

    tab = count.tabulate(logs, count.QEMU_FPGA_LOOKFOR)
    return scoreByCWE(tab)
