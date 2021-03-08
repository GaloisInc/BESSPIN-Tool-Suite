# This checks the validity of the scores when the binary source is GFE

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES

@decorate.debugWrap
def checkValidScores ():
    # This is only to check the scores are as expected -- only valid for GFE
    if (not isEqSetting('binarySource','GFE')):
        warnAndLog("Scores validity is not checked for non-GFE targets.")
        return
    
    #error Count:
    errCount = 0
    osImage = getSetting('osImage')
    for vulClass in getSetting("vulClasses"):
        vScoresDict = getSettingDict("cweScores",vulClass)
        for cwe,score in vScoresDict.items():
            if (score == SCORES.HIGH): #looks fine
                continue
            if ("gfeScoringExceptions" in getSettingDict(vulClass,["testsInfo",f"test_{cwe}"])):
                exceptions = getSettingDict(vulClass,["testsInfo",f"test_{cwe}","gfeScoringExceptions"])
                isItAnOkException = False
                for exception in exceptions:
                    if (("osImage" not in exception) or ("score" not in exception)):
                        logAndExit(f"checkValidScores: Invalid exception format for <test_{cwe}> in <{vulClass}>.",
                            exitCode=EXIT.Dev_Bug)
                    if ((exception["osImage"]==osImage) and (SCORES.toScore(exception["score"])==score)):
                        isItAnOkException = True
                        break
                if (isItAnOkException): #This score is fine
                    continue

            errorAndLog (f"checkValidScores: Unaccepted score in <{vulClass}>: (CWE-{cwe}:{score})")
            errCount += 1
                
    if (errCount > 0):
        pluralS = 's' if (errCount>1) else ''
        logAndExit(f"checkValidScores: {errCount} unaccepted score{pluralS}.",exitCode=EXIT.Run)
    else:
        printAndLog (f"checkValidScores: Scores were successfully validated.")
    
    return
