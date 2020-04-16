#! /usr/bin/env python3
"""

--- fett.py is the main FETT-Target program. All documentation and features are based on 
    solely executing this file. Please do not execute any other file.
--- Usage: `./fett.py (--help | -h)`
--- Defaults: 
        workingDirectory = ./workDir
        configFile = ./config.ini
        logFile = ./${workDir}/fett.log
        logging level = INFO 
"""

import logging, argparse, os, shutil
from fett.base.utils.misc import formatExc, printAndLog, setSetting
from fett.base.config import loadConfiguration
from fett.target.launch import launchFett

def main (xArgs):
    # Create working Directory
    repoDir = os.path.abspath(os.path.dirname(__file__))
    if (xArgs.workingDirectory):
        workDir = os.path.abspath(xArgs.workingDirectory)
    else:
        workDir = os.path.join(repoDir,'workDir')
    if (os.path.isdir(workDir)): # already exists, delete
        try:
            shutil.rmtree(workDir)
        except Exception as exc:
            print(f"(Error)~  Failed to delete <{workDir}>.\n{formatExc(exc)}.")
            exit (1)
    try:
        os.mkdir(workDir)
    except Exception as exc:
        print(f"(Error)~  Failed to create the working directory <{workDir}>.\n{formatExc(exc)}.")
        exit (1)

    # Check config file
    if (xArgs.configFile):
        configFile = os.path.abspath(xArgs.configFile)
    else:
        configFile = os.path.join(repoDir,'config.ini')
    try:
        fConfig = open(configFile,'r')
        fConfig.close()
    except Exception as exc:
        print(f"(Error)~  Failed to read the configuration file <{configFile}>.\n{formatExc(exc)}.")
        exit (1)

    # Check log file
    if (xArgs.logFile):
        logFile = os.path.abspath(xArgs.logFile)
    else:
        logFile = os.path.join(workDir,'fett.log')
    try:
        fLog = open(logFile,'w')
        fLog.close()
    except Exception as exc:
        print(f"(Error)~  Failed to create the log file <{logFile}>.\n{formatExc(exc)}.")
        exit (1)

    # setup the logging
    logLevel = logging.DEBUG if (xArgs.debug) else logging.INFO 
    logging.basicConfig(filename=logFile,filemode='w',format='%(asctime)s: (%(levelname)s)~  %(message)s',datefmt='%I:%M:%S %p',level=logLevel)
    printAndLog(f"Welcome to FETT!")

    # Store critical settings
    setSetting('repoDir', repoDir)
    setSetting ('workDir', workDir)
    setSetting('configFile', configFile)
    setSetting('logFile', logFile)
    # Load all configuration and setup settings
    setupEnvFile = os.path.join(repoDir,'fett','base','utils','setupEnv.json')
    setSetting('setupEnvFile', setupEnvFile)
    loadConfiguration(configFile)

    #launch the tool
    launchFett()
    printAndLog(f"End of FETT! [Exit code 0:Success]")
    exit(0)

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='FETT (Finding Exploits to Thwart Tampering)')
    xArgParser.add_argument ('-c', '--configFile', help='Overwrites the default config file: ./config.ini')
    xArgParser.add_argument ('-w', '--workingDirectory', help='Overwrites the default working directory: ./workDir/')
    xArgParser.add_argument ('-l', '--logFile', help='Overwrites the default logFile: ./${workDir}/fett.log')
    xArgParser.add_argument ('-d', '--debug', help='Enable debugging mode.', action='store_true')
    xArgs = xArgParser.parse_args()

    main(xArgs)
