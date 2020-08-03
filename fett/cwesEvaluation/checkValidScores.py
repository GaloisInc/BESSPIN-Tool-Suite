# This checks the validity of the scores when the binary source is GFE

from fett.base.utils.misc import *

import os
from collections import defaultdict

class cweException:
    def __init__ (self):
        self.osList = ['FreeRTOS', 'FreeBSD', 'debian']
        self.legitValues = defaultdict(list)
        for iOS in self.osList:
            self.legitValues[iOS] = [0]

    def addException (self,xOS,xVal):
        if (xOS == '*'):
            for iOS in self.osList:
                self.addException (iOS,xVal)
        elif (xOS in self.osList):
            try:
                intVal = int(xVal)
            except Exception as exc:
                logAndExit (f"Non-integer value <{xVal}> in cwesException file.",exitCode=EXIT.Dev_Bug)
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
    cweExceptionsFile = os.path.join(getSetting('repoDir'),'fett','cwesEvaluation','validScoresGFE.csv')
    cwesExceptions = defaultdict(cweException)
    for line in ftReadLines(cweExceptionsFile):
        if ((len(line)==0) or (line.strip()[0] == '#')):
            continue
        items = line.split(',')
        if (len(items) != 3):
            logAndExit (f"Unrecognized entry <{line}> in <{cweExceptionsFile}>.",exitCode=EXIT.Dev_Bug)
        cwesExceptions[items[0]].addException(*items[1:])
    
    #error Count:
    errCount = 0
    baseLogDir = os.path.join(getSetting('workDir'), 'cwesEvaluationLogs')
    for vulClass in getSetting("vulClasses"):
        csvScoresFile = os.path.join(baseLogDir, vulClass, 'scores.csv')

        #check for the scores.csv file
        if (not os.path.isfile(csvScoresFile)):
            warnAndLog(f"No scores found for <{vulClass}>.")
            continue

        #Read the scores
        for line in ftReadLines(csvScoresFile):
            if (len(line)==0):
                continue
            items = line.split(',')
            if (len(items) < 4):
                logAndExit (f"Unexpected line <{line}> in <{csvScoresFile}>.",exitCode=EXIT.Dev_Bug)
            try:
                scoreVal = int(items[2])
            except Exception as exc:
                logAndExit (f"Non-integer value <{items[2]}> in <{csvScoresFile}>.",exitCode=EXIT.Dev_Bug)
            if (scoreVal not in cwesExceptions[items[0]].getLegitValues(getSetting('osImage'))):
                errorAndLog (f"checkValidScores: Unaccepted score in <{vulClass}>: (cwe-{items[0]}:{items[1]})")
                errCount += 1
                
    if (errCount > 0):
        pluralS = 's' if (errCount>1) else ''
        logAndExit(f"checkValidScores: {errCount} unaccepted score{pluralS}.",exitCode=EXIT.Run)
    else:
        printAndLog (f"checkValidScores: Scores were successfully validated.")
    
    return
