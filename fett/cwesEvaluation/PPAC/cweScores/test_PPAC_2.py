from fett.base.utils.misc import *
from fett.cwesEvaluation.hardwareSoC.cweScores.helpers import *

def test_PPAC_2(logTest,logsDir):
    testNum = "PPAC_2"
    if (logTest != f"test_{testNum}.log"):
        return [f"TEST-{testNum}", SCORES.FAIL, "Wrong test called!"]

    return defaultRecommendationText (testNum, logsDir)