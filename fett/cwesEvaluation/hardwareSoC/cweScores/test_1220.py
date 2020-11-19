from fett.base.utils.misc import *
from fett.cwesEvaluation.hardwareSoC.cweScores.helpers import *

def test_1220(logTest,logsDir):
    testNum = 1220
    if (logTest != f"test_{testNum}.log"):
        return [f"TEST-{testNum}", SCORES.FAIL, "Wrong test called!"]

    return defaultRecommendationText (testNum, logsDir)