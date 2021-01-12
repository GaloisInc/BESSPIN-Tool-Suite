#! /usr/bin/env python3

import sys, os
import argparse, atexit, logging

def main(xArgs):
    buildDir = os.path.abspath(os.path.dirname(__file__))
    repoDir = os.path.abspath(os.path.join(buildDir,os.pardir))
    workDir = os.path.join(repoDir,'workDir')

    # Let's do this ugly workaround to have this utility use the tool, but not to be part of the tool
    sys.path.insert(0, repoDir)
    from fett.base.utils.misc import trashCanObj, exitPeacefully, setSetting, getSetting
    from fett.base.config import loadConfiguration
    from fett.cwesEvaluation.common import score
    from fett.cwesEvaluation.utils.checkValidScores import checkValidScores

    vulClass = xArgs.vulClass
    logFile = os.path.join(workDir,'vulClassScore.log')
    try:
        fLog = open(logFile,'w')
        fLog.close()
    except Exception as exc:
        print(f"(Error)~  Failed to create the log file <{logFile}>.\n{formatExc(exc)}.")
        exitFett(EXIT.Files_and_paths)
    logLevel = logging.DEBUG if (xArgs.debug) else logging.INFO 
    logging.basicConfig(filename=logFile,filemode='w',format='(%(levelname)s)~  %(message)s',datefmt='%I:%M:%S %p',level=logLevel)

    setSetting('repoDir',repoDir)
    setSetting('workDir',workDir)
    setSetting('logFile', logFile)
    setSetting('trash',trashCanObj())
    setSetting('debugMode', xArgs.debug)
    atexit.register(exitPeacefully,getSetting('trash'))
    setSetting('buildDir',os.path.join(workDir,'build'))
    setSetting('cwesEvaluationLogs',os.path.join(workDir,'cwesEvaluationLogs'))

    # Load all configuration and setup settings
    setupEnvFile = os.path.join(repoDir,'fett','base','utils','setupEnv.json')
    setSetting('setupEnvFile', setupEnvFile)
    configFile = os.path.join(repoDir,'myConfig.ini')
    setSetting('configFile', configFile)

    loadConfiguration(configFile)

    score (os.path.join(getSetting('cwesEvaluationLogs'),vulClass), vulClass)
    checkValidScores()

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Scores the CWEs logs for a failed run (Debug utility).')
    xArgParser.add_argument ('vulClass', help='The vulnerability class to score.')
    xArgParser.add_argument ('-d', '--debug', help='Enable debugging mode.', action='store_true')

    xArgs = xArgParser.parse_args()
    main(xArgs)