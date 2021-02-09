#! /usr/bin/env python3
from collections import defaultdict

from fett.base.utils.misc import *
from fett.cwesEvaluation.utils import featureModelUtil
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore
from fett.cwesEvaluation.informationLeakage.iexutils import dirnames
from fett.cwesEvaluation.utils.scoringAux import defaultSelfAssessmentScoreAllTests
import glob,os

"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
scoring functions for each CWE test
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""
VULCLASS = "informationLeakage"

def parseTestName(testName):
    return testName.split("_")[1]

@decorate.debugWrap
@decorate.timeWrap
def generateCweMap():
    CWES = [ "CWE_200",
             "CWE_201",
             "CWE_202",
             "CWE_203",
             "CWE_205",
             "CWE_206",
             "CWE_212",
             "CWE_226",
             "CWE_244",
             "CWE_524" ]
    vulClassDir = os.path.join(getSetting('repoDir'),
                           'fett',
                           'cwesEvaluation',
                           'informationLeakage')
    fmfile  = os.path.join(vulClassDir, 'InformationLeakage.cfr')
    src = os.path.join(vulClassDir, 'sources')

    # Compare the mapping[tests] and .cfr hash versus the saved values
    savedMapFile = getSettingDict(VULCLASS,"cwesMapFile")
    mapping = safeLoadJsonFile (savedMapFile)
    tests        = dirnames(f"{src}/tests/*.c") + [t.split("test_")[-1] for t in dirnames(f"{src}/nonstandard/*.c")]
    doComputeMap = False

    if (set(mapping.keys()) != set(tests)): #Re-generate the map
        warnAndLog (f"IEX:generateCweMap: The available tests do not match the info saved in"
            f" {savedMapFile}. The file is now updated, please consider committing any changes"
            f" accordingly.")
        doComputeMap = True

    computedModelHash = computeMd5ForFile(fmfile)
    if (computedModelHash != getSettingDict(VULCLASS,"modelHash")):
        warnAndLog (f"IEX:generateCweMap: The saved hash in {os.path.join(vulClassDir,'setupEnv.json')}"
            f" does not match the computed value <{computedModelHash}>. Please consider committing any"
            f" model changes accordingly.")
        doComputeMap = True

    if (doComputeMap):
        fm = featureModelUtil.loadFM(fmfile)
        mapping = {}
        for t in tests:
            cfg    = [f"Test_{t}"]
            fm2    = featureModelUtil.addConstraints(fm, cfg)
            result = featureModelUtil.checkMust(fm2, CWES)
            mapping[t] = [ cwe for (cwe, on) in zip(CWES, result) if on ]
        safeDumpJsonFile(mapping, savedMapFile)
    return mapping

def scoreAllTests(logs):
    if (isEnabledDict(VULCLASS,"useSelfAssessment")):
        return defaultSelfAssessmentScoreAllTests(VULCLASS, logs)

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
    if log.find('TEST ERROR') >= 0:
        score = SCORES.CALL_ERR
    elif log.find('TEST NOT IMPLEMENTED') >= 0:
        score = SCORES.NOT_IMPLEMENTED
    elif log.find('TEST FAILED') >= 0:
        score = SCORES.HIGH
    elif ((log.find('TEST PASSED') >= 0) or (log.find('Illegal instruction') >= 0)):
        score = SCORES.NONE
    else:
        score = SCORES.FAIL
    return adjustToCustomScore(log.splitlines(),score)
