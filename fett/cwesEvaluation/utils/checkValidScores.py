# This checks the validity of the scores when the binary source is GFE

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES

import os
from collections import defaultdict

class cweException:
    def __init__ (self):
        self.osList = ['FreeRTOS', 'FreeBSD', 'debian']
        self.legitValues = defaultdict(list)
        for iOS in self.osList:
            self.legitValues[iOS] = [SCORES.HIGH.value]

    def addException (self,xOS,xVal):
        if (xOS == '*'):
            for iOS in self.osList:
                self.addException (iOS,xVal)
        elif (xOS in self.osList):
            try:
                intVal = int(xVal)
            except Exception as exc:
                logAndExit (f"Non-integer value <{xVal}> in cwesException file.",exitCode=EXIT.Dev_Bug,exc=exc)
            self.legitValues[xOS].append(intVal)
        else:
            logAndExit (f"Unrecognized OS <{xOS}> in cwesException file.",exitCode=EXIT.Dev_Bug)

    def getLegitValues (self, xOS):
        return self.legitValues[xOS]

@decorate.debugWrap
def checkValidScores ():
    # This is only to check the scores are as expected -- only valid for GFE
    if (not isEqSetting('binarySource','GFE')):
        warnAndLog("Scores validity is not checked for non-GFE targets.")
        return

    #Load CWEs exceptions
    cweExceptionsFile = os.path.join(getSetting('repoDir'),'fett','cwesEvaluation','utils','validScoresGFE.csv')
    cwesExceptions = defaultdict(cweException)
    for line in ftReadLines(cweExceptionsFile):
        if ((len(line)==0) or (line.strip()[0] == '#')):
            continue
        items = line.split(',')
        if (len(items) != 3):
            logAndExit (f"Unrecognized entry <{line}> in <{cweExceptionsFile}>.",exitCode=EXIT.Dev_Bug)
        cwesExceptions[items[0].replace('-','_')].addException(*items[1:])
    
    #error Count:
    errCount = 0
    osImage = getSetting('osImage')
    for vulClass in getSetting("vulClasses"):
        vScoresDict = getSettingDict("cweScores",vulClass)
        for cwe,score in vScoresDict.items():
            scoreVal = score.value
            if (score.value not in cwesExceptions[cwe].getLegitValues(osImage)):
                errorAndLog (f"checkValidScores: Unaccepted score in <{vulClass}>: (CWE-{cwe}:{score})")
                errCount += 1
                
    if (errCount > 0):
        pluralS = 's' if (errCount>1) else ''
        logAndExit(f"checkValidScores: {errCount} unaccepted score{pluralS}.",exitCode=EXIT.Run)
    else:
        printAndLog (f"checkValidScores: Scores were successfully validated.")
    
    return
