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
from fett.base.core import formatExc, objFett, printAndLog

def main (xArgs):
    # Create working Directory
    fettDir = os.path.abspath(os.path.dirname(__file__))
    if (xArgs.workingDirectory):
        workDir = os.path.abspath(xArgs.workingDirectory)
    else:
        workDir = os.path.join(fettDir,'workDir')
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
        configFile = os.path.join(fettDir,'config.ini')
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

    # Getting the main FETT object
    xFett = objFett(workDir, configFile)

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='FETT (Finding Exploits to Thwart Tampering)')
    xArgParser.add_argument ('-c', '--configFile', help='Overwrites the default config file: ./config.ini')
    xArgParser.add_argument ('-w', '--workingDirectory', help='Overwrites the default working directory: ./workDir/')
    xArgParser.add_argument ('-l', '--logFile', help='Overwrites the default logFile: ./${workDir}/fett.log')
    xArgParser.add_argument ('-d', '--debug', help='Enable debugging mode.', action='store_true')
    xArgs = xArgParser.parse_args()

    main(xArgs)
