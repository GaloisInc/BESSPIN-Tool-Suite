from fett.base.utils.misc import *
from fett.cwesEvaluation.utils.scoringHelpers import *

def test_1252(dispName, logText):
    dispName = "TEST-1252"

    relvKeywords = [  "<NOGDB>","<INVALID>",
                        "<EXECUTION>","<WRITE>","<READ>",
                        "<Disabled>", "<Non-Protected>", "<Bad-Range>"    ]
    keywordsDict = doKeywordsExistInText(logText,relvKeywords)

    if (keywordsDict["<NOGDB>"]):
        return overallScore ([],dispName,msgIfNotImplemented="Requires GDB Access")

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

    return overallScore([adjustToCustomScore(logText.splitlines(),score)],dispName)

