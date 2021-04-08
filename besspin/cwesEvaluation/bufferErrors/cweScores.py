#! /usr/bin/env python3
import os
from importlib.machinery import SourceFileLoader
import math

from besspin.base.utils.misc import *
import besspin.cwesEvaluation.bufferErrors.count as count
from besspin.cwesEvaluation.scoreTests import SCORES
from besspin.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring functions for each CWE test
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""
VULCLASS = "bufferErrors"

def score(testScores):
    """
    Given a list of scores from individual test runs stressing the same CWE,
    compute an overall score for the CWE.

    ARGUMENTS:
    ----------
        testScores : List of SCORES
            A list of scores from individual test runs.

    RETURNS:
    --------
        A tuple of (SCORES, String), where each element is:
            0.  The overall score for the CWE.
            1.  Notes about the individual scores from <testScores>.
    """
    # Additional technical documentation for developers modifying this
    # function:
    """
    This could use some thought. We want to compute a score for a set of BOF tests.

    - A 'trap' is a 'good' result, meaning that the overflow was 'caught' in some way.

    - Both 'timeout' and 'completed' are not so good, as they indicate the overrun was NOT caught, but
    might have altered control flow (in the timeout case).

    - 'call-error' means, due to platform issues, a test was generated that can
    not accurately witness a buffer overrun weakness (e.g., the test requires
    more memory than the platform has available).
    """
    s = 0 # Number 's'uccessful (uncaught)
    i = 0 # call-error (invalid)
    e = 0 # err: FAIL/CALL-ERR (something went wrong with parsing -- no overall score reported)
    validScores = []
    for testScore in testScores:
        if (testScore == SCORES.CALL_ERR):
            i += 1
        elif (testScore == SCORES.FAIL): #FAIL/CALL-ERR 
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
        ovrScore = SCORES.CALL_ERR if e == 0 else SCORES.FAIL
    elif (s == 0): #all are DETECTED/NONE
        ovrScore = SCORES.avgScore(validScores)
    else: #partial score
        """ 
        - Currently, every 's' is considered as HIGH.
        - Even the baseline (non-secure) processor can block some of the buffer overflows from happening.
          This is due to the OS memory management, boundaries, etc. 
        - s=0 should be DETECTED, and s=t should be HIGH.
        - The value (t-s)/t represents the proportion of tests in which errors
          were detected.  Unix OS images have a larger range of values that
          score HIGH because those OSes detect more overflows as a baseline.
          The proportion of detected errors maps to scores as follows:
          - Unix: [0, 0.4), FreeRTOS: [0, 1/3) - HIGH
          - Unix: [0.4, 2/3), FreeRTOS [1/3, 2/3) - MED
          - All: [2/3, 1) - LOW
          - All: 1 - DETECTED
        """
        detectedRatio = (t-s) / float(t)
        unadjustedScore = detectedRatio*(SCORES.DETECTED.value-SCORES.HIGH.value)
        if (unadjustedScore < SCORES.HIGH.value or
            (getSetting('osImage') in ['debian', 'FreeBSD'] and
             detectedRatio < 0.4)):
            ovrScore = SCORES.HIGH
        else:
            ovrScore = SCORES(math.floor(unadjustedScore))

    return (ovrScore, notes)


def scoreByCWE(rows):
    """
    Given a score table containing scores for individual test runs (such as the
    output from <count.tabulate>), this function aggregates scores into scores
    for each CWE.

    ARGUMENTS:
    ----------
        rows : List of Dictionary of String to Any.
            Scores for individual test runs.

    RETURNS:
    --------
        A List of List of [String, SCORES, String], where each element
        represents a score for a CWE.  The elements of each sublist are:
            0.  CWE name.
            1.  Score for the CWE.
            2.  Notes about the score.
    """
    results = {}
    for row in rows:
        if 'CWE' in row:
            for cwe in row['CWE']:
                _, cweNum = cwe.split("_")
                cweNum    = f"CWE-{cweNum}"
                try:
                    results[cweNum].append(row['Adjusted Result'])
                except:
                    results[cweNum] = [row['Adjusted Result']]
        else:
            results[row['TestNumber']] = [row['Adjusted Result']]
    tab = []
    for test in sorted(results.keys()):
        v = score(results[test])
        tab.append([f"{test}", v[0], v[1]])
    return tab

def scoreAllTests(logs):
    """
    Compute buffer errors CWE scores from individual test logs.

    ARGUMENTS:
    ----------
        logs : List of Tuple of (String, String).
            The logs to score.  Each element of the list is a tuple with
            elements:
                0.  The name of the test.
                1.  The path to the log file to score.

    SIDE-EFFECTS:
    -------------
        - If ${bufferErrors}[${csvFile}] is enabled, writes the CSV file
          containing the scores to
          <${cwesEvaluationLogs}/bufferErrors/bufferErrors.csv>.

    RETURNS:
    --------
        A List of List of [String, SCORES, String], where each element
        represents a score for a CWE.  The elements of each sublist are:
            0.  CWE name.
            1.  Score for the CWE.
            2.  Notes about the score.
    """
    if (isEnabledDict(VULCLASS,"useSelfAssessment")):
        return defaultSelfAssessmentScoreAllTests(VULCLASS, logs)

    tab = count.tabulate(logs, count.QEMU_FPGA_LOOKFOR)
    return scoreByCWE(tab)
