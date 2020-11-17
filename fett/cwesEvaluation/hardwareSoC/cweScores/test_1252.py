from fett.base.utils.misc import *
from fett.cwesEvaluation.hardwareSoC.cweScores.helpers import *

def test_1252(logTest,logsDir):
    testNum = 1252
    if (logTest != f"test_{testNum}.log"):
        return [f"TEST-{testNum}", SCORES.FAIL, "Wrong test called!"]
    
    logText = ftReadLines(os.path.join(logsDir,logTest),splitLines=False)

    relvKeywords = [  "<NOGDB>","<INVALID>",
                        "<EXECUTION>","<WRITE>","<READ>",
                        "<Disabled>", "<Non-Protected>", "<Bad-Range>"    ]
    keywordsDict = doKeywordsExistInText(logText,relvKeywords)

    if (keywordsDict["<NOGDB>"]):
        return overallScore ([],testNum,msgIfNotImplemented="Requires GDB Access")

    if (keywordsDict["<INVALID>"]):
        score = SCORES.CALL_ERR
    elif (keywordsDict["<EXECUTION>"]):
        score = SCORES.NONE
    elif (keywordsDict["<WRITE>"]):
        score = SCORES.MED
    elif (keywordsDict["<READ>"]):
        score = SCORES.HIGH
    elif (keywordsDict["<Disabled>"] or keywordsDict["<Non-Protected>"] or keywordsDict["<Bad-Range>"]):
        score = SCORES.V_HIGH
    else:
        score = SCORES.FAIL

    return overallScore([adjustToCustomScore(logText.splitlines(),score)],testNum)

