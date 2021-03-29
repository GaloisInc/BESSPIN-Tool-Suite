#! /usr/bin/env python3
"""

--- besspin.py is the main BESSPIN-Tool-Suite program. All documentation and features are based on 
    solely executing this file. Please do not execute any other file.
--- usage: besspin.py [-h] [-c CONFIGFILE | -cjson CONFIGFILESERIALIZED]
               [-w WORKINGDIRECTORY] [-l LOGFILE] [-d]
               [-ep {devHost,ciOnPrem,ciAWS,awsProd,awsDev}] [-job JOBID]

BESSPIN (Balancing Evaluation of System Security Properties with Industrial Needs)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGFILE, --configFile CONFIGFILE
                        Overwrites the default config file: ./config.ini
  -cjson CONFIGFILESERIALIZED, --configFileSerialized CONFIGFILESERIALIZED
                        Overwrites and augments the default production
                        settings
  -w WORKINGDIRECTORY, --workingDirectory WORKINGDIRECTORY
                        Overwrites the default working directory: ./workDir/
  -l LOGFILE, --logFile LOGFILE
                        Overwrites the default logFile: ./${workDir}/besspin.log
  -d, --debug           Enable debugging mode.
  -ep {devHost,ciOnPrem,ciAWS,awsProd,awsDev}, --entrypoint {devHost,ciOnPrem,ciAWS,awsProd,awsDev}
                        The entrypoint
  -job JOBID, --jobId JOBID
                        The job ID in production mode.

--- Defaults: 
        workingDirectory = ./workDir
        configFile = ./config.ini
        logFile = ./${workDir}/besspin.log
        logging level = INFO 
        entrypoint = devHost
"""

try:
    from besspin.base.utils.misc import *
    from besspin.base.config import loadConfiguration, genProdConfig
    from besspin.target.launch import startBesspin, endBesspin, resetTarget
    from besspin.cyberPhys.launch import startCyberPhys, endCyberPhys
    from besspin.base.utils import aws
    from besspin.base.threadControl import createBesspinLocks
    import logging, argparse, os, shutil, atexit, signal
except Exception as exc:
    try:
        #check we're in nix
        import sys
        if (sys.executable.split('/')[1] != 'nix'):
            print (f"(Error)~  Please run within a nix shell. [Run <nix-shell> in besspin directory].")
        else:
            raise
    except:
        print(f"(Error)~  <{exc.__class__.__name__}>: {exc}")
    print(f"(Info)~  End of BESSPIN! [Exit code -1:Fatal]")
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
            exitBesspin(EXIT.Configuration, preSetup=True)
    try:
        os.mkdir(workDir)
    except Exception as exc:
        print(f"(Error)~  Failed to create the working directory <{workDir}>.\n{formatExc(exc)}.")
        exitBesspin(EXIT.Files_and_paths, preSetup=True)

    # Check log file
    if (xArgs.logFile):
        logFile = os.path.abspath(xArgs.logFile)
    else:
        logFile = os.path.join(workDir,'besspin.log')
    try:
        fLog = open(logFile,'w')
        fLog.close()
    except Exception as exc:
        print(f"(Error)~  Failed to create the log file <{logFile}>.\n{formatExc(exc)}.")
        exitBesspin(EXIT.Files_and_paths, preSetup=True)

    # Entrypoint
    if(xArgs.entrypoint is None):
        xArgs.entrypoint = 'devHost'

    # Check jobId is valid, if provided
    if(xArgs.jobId):
        if(not(re.match("^[A-Za-z0-9-_+.]+$", xArgs.jobId))):
            print("(Error)~  Provided jobId contained invalid character(s). It must match regex '[A-Za-z0-9-_+.]'")
            exitBesspin(EXIT.Files_and_paths, preSetup=True)

    # setup the logging
    logLevel = logging.DEBUG if (xArgs.debug) else logging.INFO 
    logging.basicConfig(filename=logFile,filemode='w',format='%(asctime)s: (%(levelname)s)~  %(message)s',datefmt='%I:%M:%S %p',level=logLevel)
    printAndLog(f"Welcome to BESSPIN!")

    #Prepare the peaceful exit
    setSetting('trash',trashCanObj())
    atexit.register(exitPeacefully,getSetting('trash'))

    # Store critical settings
    setSetting('repoDir', repoDir)
    setSetting ('workDir', workDir)
    setSetting('logFile', logFile)
    setSetting('debugMode', xArgs.debug)
    setSetting('besspinEntrypoint',xArgs.entrypoint)
    setSetting('prodJobId', xArgs.jobId)
    
    # Load all configuration and setup settings
    setupEnvFile = os.path.join(repoDir,'besspin','base','utils','setupEnv.json')
    setSetting('setupEnvFile', setupEnvFile)
    if (xArgs.configFile):
        configFile = os.path.abspath(xArgs.configFile)
    elif (xArgs.configFileSerialized):
        configFile = os.path.join(workDir,'production.ini')
        genProdConfig (xArgs.configFileSerialized, configFile)
        printAndLog(f"Configuration deserialized successfully to <{configFile}>.")
    else:
        configFile = os.path.join(repoDir,'config.ini')
        printAndLog(f"Using the default configuration in <{configFile}>.")
    setSetting('configFile', configFile)

    #Load the config file(s)
    loadConfiguration(configFile)

    #Create the global semaphores/Locks
    createBesspinLocks()

    #launch the tool
    if (isEqSetting('mode','cyberPhys')):
        startCyberPhys()
        endCyberPhys()
    else:
        xTarget = startBesspin()

        instruction = None
        if (isEqSetting('mode','production')):
            def sendSuccessMsgToPortal (nodeSuffix, reasonSuffix):
                aws.sendSQS(getSetting(f'{getSetting("besspinEntrypoint")}SqsQueueTX'), logAndExit, 'success', 
                        getSetting('prodJobId'), f"{getSetting('prodJobId')}-{nodeSuffix}",
                        reason=f'besspin-production-{reasonSuffix}',
                        hostIp=aws.getInstanceIp(logAndExit),
                        fpgaIp=getSetting('productionTargetIp')
                        )
                printAndLog(f"Sent {reasonSuffix} message to the SQS queue.")

            # Notify portal that we have deployed successfully
            sendSuccessMsgToPortal('DEPLOY','deployment')

            # Wait for portal to instruct us to do something
            while (instruction != 'termination'):
                instruction = aws.pollPortalIndefinitely (getSetting(f'{getSetting("besspinEntrypoint")}S3Bucket'), xTarget.process, logAndExit)
                if (instruction == 'deadProcess'):
                    warnAndLog ("The main process is dead. Will exit without a notice from Portal.")
                    break
                printAndLog(f"Received {instruction} notice from Portal.")            

                if (instruction == 'reset'):
                    # execute reset flow 
                    xTarget = resetTarget(xTarget)
                    # Notify portal that we have reset successfully
                    sendSuccessMsgToPortal('RESET','reset')

        endBesspin(xTarget,(instruction=='deadProcess'))

    exitBesspin(EXIT.Success)

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='BESSPIN (Balancing Evaluation of System Security Properties with Industrial Needs)')
    xGroupConfig = xArgParser.add_mutually_exclusive_group(required=False)
    xGroupConfig.add_argument ('-c', '--configFile', help='Overwrites the default config file: ./config.ini')
    xGroupConfig.add_argument ('-cjson', '--configFileSerialized', help='Overwrites and augments the default production settings')
    xArgParser.add_argument ('-w', '--workingDirectory', help='Overwrites the default working directory: ./workDir/')
    xArgParser.add_argument ('-l', '--logFile', help='Overwrites the default logFile: ./${workDir}/besspin.log')
    xArgParser.add_argument ('-d', '--debug', help='Enable debugging mode.', action='store_true')
    xArgParser.add_argument ('-ep', '--entrypoint', choices=['devHost','ciOnPrem','ciAWS','awsProd','awsDev'], help='The entrypoint')
    xArgParser.add_argument ('-job', '--jobId', help='The job ID in production mode.')
    xArgs = xArgParser.parse_args()

    #Trapping the signals
    signalsToCatch = [signal.SIGINT, signal.SIGTERM]
    for xSignal in signalsToCatch:
        signal.signal(xSignal,exitOnInterrupt)

    main(xArgs)
