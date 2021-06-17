#! /usr/bin/env python3

import sys, os
import argparse, atexit, logging

"""
This utility is intended to be used for debug. It runs the CWEs scoring; this is not a full run of Besspin.
There is no guarantee that you did not change the configuration and the utility does not verify that the 
work directory has the files that match the loaded configuration.
"""

def main(xArgs):
    buildDir = os.path.abspath(os.path.dirname(__file__))
    repoDir = os.path.abspath(os.path.join(buildDir,os.pardir))
    workDir = os.path.join(repoDir,'workDir')

    # Let's do this ugly workaround to have this utility use the tool, but not to be part of the tool
    sys.path.insert(0, repoDir)
    from besspin.base.utils.misc import trashCanObj, exitPeacefully, setSetting, getSetting, isEnabled, exitBesspin, EXIT
    from besspin.base.config import loadConfiguration
    from besspin.cwesEvaluation.scoreTests import scoreTests, prettyVulClass
    from besspin.cwesEvaluation.utils.checkValidScores import checkValidScores
    from besspin.cwesEvaluation.utils.computeBesspinScale import computeBesspinScale
    from besspin.cwesEvaluation.utils.computeNaiveCWEsTally import computeNaiveCWEsTally

    logFile = os.path.join(workDir,'vulClassScore.log')
    try:
        fLog = open(logFile,'w')
        fLog.close()
    except Exception as exc:
        print(f"(Error)~  Failed to create the log file <{logFile}>.\n{formatExc(exc)}.")
        exitBesspin(EXIT.Files_and_paths)
    logLevel = logging.DEBUG if (xArgs.debug) else logging.INFO 
    logging.basicConfig(filename=logFile,filemode='w',format='%(asctime)s: (%(levelname)s)~  %(message)s',datefmt='%I:%M:%S %p',level=logLevel)

    setSetting('repoDir',repoDir)
    setSetting('workDir',workDir)
    setSetting('logFile', logFile)
    setSetting('trash',trashCanObj())
    setSetting('debugMode', xArgs.debug)
    atexit.register(exitPeacefully,getSetting('trash'))
    setSetting('buildDir',os.path.join(workDir,'build'))
    setSetting('cwesEvaluationLogs',os.path.join(workDir,'cwesEvaluationLogs'))

    # Load all configuration and setup settings
    setupEnvFile = os.path.join(repoDir,'besspin','base','utils','setupEnv.json')
    setSetting('setupEnvFile', setupEnvFile)
    if (xArgs.configFile):
        configFile = os.path.abspath(xArgs.configFile)
    else:
        configFile = os.path.join(repoDir,'config.ini')
        print(f"Using the default configuration in <{configFile}>.")
    setSetting('configFile', configFile)

    loadConfiguration(configFile)

    # dict key name used to distinguish between the two
    osDiv = "unix" if isEnabled("isUnix") else "FreeRTOS"
    setSetting("osDiv",osDiv)

    if (getSetting('mode') != 'evaluateSecurityTests'):
        print(f"(Error)~  This utility is only for <evaluateSecurityTests> mode.")
        exitBesspin(EXIT.Configuration)

    if (xArgs.vulClass == "all"):
        for vulClass in getSetting("vulClasses"): 
            scoreTests (vulClass, os.path.join(getSetting('cwesEvaluationLogs'),vulClass),prettyVulClass(vulClass))
    else:
        setSetting("vulClasses",[xArgs.vulClass])
        scoreTests (xArgs.vulClass, os.path.join(getSetting('cwesEvaluationLogs'),xArgs.vulClass),prettyVulClass(xArgs.vulClass))
    checkValidScores()

    if (isEnabled('computeNaiveCWEsTally')):
        computeNaiveCWEsTally()
    if (isEnabled('computeBesspinScale')):
        computeBesspinScale()

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Scores the CWEs logs for a failed run (Debug utility).')
    xArgParser.add_argument ('-c', '--configFile', help='Overwrites the default config file: ./config.ini')
    xArgParser.add_argument ('-v', '--vulClass', help='Single vulnerability class to score. Default is <all>',default="all")
    xArgParser.add_argument ('-d', '--debug', help='Enable debugging mode.', action='store_true')

    xArgs = xArgParser.parse_args()
    main(xArgs)