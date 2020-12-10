#! /usr/bin/env python3
from collections import defaultdict

from fett.base.utils.misc import *
from fett.cwesEvaluation.utils import featureModelUtil
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
from fett.cwesEvaluation.informationLeakage.iexutils import dirnames
import glob,os

"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring functions for each CWE test
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""

def parseTestName(testName):
    return testName.split("_")[1]

def generateCweMap():
    CWES = [ "CWE_201",
             "CWE_202",
             "CWE_203",
             "CWE_209",
             "CWE_212",
             "CWE_214",
             "CWE_226",
             "CWE_321",
             "CWE_524",
             "CWE_526",
             "CWE_612",
             "CWE_707" ]
    fmfile  = os.path.join(getSetting('repoDir'),
                           'fett',
                           'cwesEvaluation',
                           'informationLeakage',
                           'InformationLeakage.cfr')
    src = os.path.join(getSetting('buildDir'), 'informationLeakage')
    fm = featureModelUtil.loadFM(fmfile)

    tests        = dirnames(f"{src}/tests/*.c")
    mapping = {}
    for t in tests:
        cfg    = [f"Test_{t}"]
        fm2    = featureModelUtil.addConstraints(fm, cfg)
        result = featureModelUtil.checkMust(fm2, CWES)
        mapping[t] = [ cwe for (cwe, on) in zip(CWES, result) if on ]
    return mapping

def scoreAllTests(logs):
    cwemap = generateCweMap()
    scoresDict = defaultdict(list)
    for name, log in logs:
        driver = parseTestName(name)
        testNums = cwemap[driver]
        for testNum in testNums:
            testNum = testNum.split("_")[1]
            scoresDict[testNum].append(scoreTest(log))

    ret = []
    for testNum, listScores in scoresDict.items():
        notesList = []
        for possibleScore in SCORES: #loop this way to use them sorted
            if (listScores.count(possibleScore) > 0):
                notesList.append(f"{possibleScore}({listScores.count(possibleScore)})")

        notes = "Results: " + ', '.join(notesList)
        implemented = [ s for s in listScores if s != SCORES.NOT_IMPLEMENTED ]
        if len(implemented) > 0:
            score = SCORES.avgScore(implemented)
        else:
            score = SCORES.NOT_IMPLEMENTED
        ret.append([f"CWE-{testNum}", score, notes])
    return ret


def scoreTest(logTest):
    log = ftReadLines(logTest,splitLines=False)

    if log.find('TEST NOT IMPLEMENTED') >= 0:
        score = SCORES.NOT_IMPLEMENTED
    elif log.find('TEST FAILED') >= 0:
        score = SCORES.HIGH
    elif log.find('TEST ERROR') >= 0:
        score = SCORES.CALL_ERR
    elif ((log.find('TEST PASSED') >= 0) or (log.find('Illegal instruction') >= 0)):
        score = SCORES.NONE
    else:
        score = SCORES.FAIL
    return adjustToCustomScore(log.splitlines(),score)
