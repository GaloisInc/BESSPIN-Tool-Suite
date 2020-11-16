from fett.base.utils.misc import *
from fett.cwesEvaluation.hardwareSoC.cweScores.helpers import *

def test_1252(logTest,logsDir):
    testNum = 1252
    if (logTest != f"test_{testNum}.log"):
        return [f"TEST-{testNum}", SCORES.FAIL, "Wrong test called!"]
    
    testLines = ftReadLines(os.path.join(logsDir,logTest))

    if (doesKeywordExist(testLines,"<NOGDB>")):
        return overallScore ([],testNum,msgIfNotImplemented="Requires GDB Access")

    if (doesKeywordExist(testLines,"<INVALID>")):
        score = SCORES.CALL_ERR
    else:
        warnAndLog("<test_1252>: Scoring is not yet implemented.")
        score = SCORES.NOT_IMPLEMENTED

    return overallScore([score],testNum)

