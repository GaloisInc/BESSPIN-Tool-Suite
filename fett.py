#! /usr/bin/env python3
"""

--- fett.py is the main FETT-Target program. All documentation and features are based on 
    solely executing this file. Please do not execute any other file.
--- Usage: fett.py [-h] [-c CONFIGFILE] [-w WORKINGDIRECTORY] [-l LOGFILE] [-d]
               [-ep ENTRYPOINT]

FETT (Finding Exploits to Thwart Tampering)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGFILE, --configFile CONFIGFILE
                        Overwrites the default config file: ./config.ini
  -w WORKINGDIRECTORY, --workingDirectory WORKINGDIRECTORY
                        Overwrites the default working directory: ./workDir/
  -l LOGFILE, --logFile LOGFILE
                        Overwrites the default logFile: ./${workDir}/fett.log
  -d, --debug           Enable debugging mode.
  -ep ENTRYPOINT, --entrypoint ENTRYPOINT
                        Entrypoint: devHost | ciOnPrem
--- Defaults: 
        workingDirectory = ./workDir
        configFile = ./config.ini
        logFile = ./${workDir}/fett.log
        logging level = INFO 
        entrypoint = devHost
"""

try:
    from fett.base.utils.misc import *
    from fett.base.config import loadConfiguration
    from fett.target.launch import startFett, endFett
    import logging, argparse, os, shutil, atexit, signal
except Exception as exc:
    try:
        #check we're in nix
        import sys
        if (sys.executable.split('/')[1] != 'nix'):
            print (f"(Error)~  Please run within a nix shell. [Run <nix-shell> in target-fett directory].")
        else:
            raise
    except:
        print(f"(Error)~  <{exc.__class__.__name__}>: {exc}")
    print(f"(Info)~  End of FETT! [Exit code -1:Fatal]")
    exit(-1)

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
            exitFett(EXIT.Configuration)
    try:
        os.mkdir(workDir)
    except Exception as exc:
        print(f"(Error)~  Failed to create the working directory <{workDir}>.\n{formatExc(exc)}.")
        exitFett(EXIT.Files_and_paths)

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
        exitFett(EXIT.Configuration)

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
        exitFett(EXIT.Files_and_paths)

    # Entrypoint
    listEntrypoints = ['devHost','ciOnPrem']
    if ((xArgs.entrypoint) and (xArgs.entrypoint not in listEntrypoints)):
        print(f"(Error)~  ENTRYPOINT has to be in [{','.join(listEntrypoints)}].")
        exitFett(EXIT.Configuration)
    elif(xArgs.entrypoint is None):
        xArgs.entrypoint = 'devHost'

    # setup the logging
    logLevel = logging.DEBUG if (xArgs.debug) else logging.INFO 
    logging.basicConfig(filename=logFile,filemode='w',format='%(asctime)s: (%(levelname)s)~  %(message)s',datefmt='%I:%M:%S %p',level=logLevel)
    printAndLog(f"Welcome to FETT!")

    # Store critical settings
    setSetting('repoDir', repoDir)
    setSetting ('workDir', workDir)
    setSetting('configFile', configFile)
    setSetting('logFile', logFile)
    setSetting('debugMode', xArgs.debug)
    setSetting('fettEntrypoint',xArgs.entrypoint)
    # Load all configuration and setup settings
    setupEnvFile = os.path.join(repoDir,'fett','base','utils','setupEnv.json')
    setSetting('setupEnvFile', setupEnvFile)
    loadConfiguration(configFile)

    #Prepare the peaceful exit
    setSetting('trash',trashCanObj())
    atexit.register(exitPeacefully,getSetting('trash'))
    
    #launch the tool
    xTarget = startFett()
    endFett(xTarget)
    exitFett(EXIT.Success)

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='FETT (Finding Exploits to Thwart Tampering)')
    xArgParser.add_argument ('-c', '--configFile', help='Overwrites the default config file: ./config.ini')
    xArgParser.add_argument ('-w', '--workingDirectory', help='Overwrites the default working directory: ./workDir/')
    xArgParser.add_argument ('-l', '--logFile', help='Overwrites the default logFile: ./${workDir}/fett.log')
    xArgParser.add_argument ('-d', '--debug', help='Enable debugging mode.', action='store_true')
    xArgParser.add_argument ('-ep', '--entrypoint', help='Entrypoint: devHost | ciOnPrem | ciAWS')
    xArgs = xArgParser.parse_args()

    #Trapping the signals
    signalsToCatch = [signal.SIGINT, signal.SIGTERM]
    for xSignal in signalsToCatch:
        signal.signal(xSignal,exitOnInterrupt)

    main(xArgs)
