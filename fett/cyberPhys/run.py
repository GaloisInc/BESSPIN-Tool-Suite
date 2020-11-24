#! /usr/bin/env python3
""" 
The main file for running cyberPhys
"""

from fett.base.utils.misc import *
import fett.cyberPhys.launch
import fett.target.launch

from fett.apps.unix import otaserver

@decorate.debugWrap
@decorate.timeWrap
def runCyberPhys(xTarget):
    printAndLog (f"{xTarget.targetIdInfo}runCyberPhys: Starting the application stack...")
    # here anything that needs to be done on the targets before handing the user the prompt
    if (isEnabled('sendTarballToTarget',targetId=xTarget.targetId)):
        #send any needed files to target
        xTarget.sendTar(timeout=60)

    # assign modules
    if (xTarget.osImage=='FreeRTOS'):
        xTarget.appModules = []
    elif (xTarget.osImage in ['debian', 'FreeBSD']):
        xTarget.appModules = [otaserver]
    else:
        xTarget.terminateAndExit(f"{xTarget.targetIdInfo}<runApp> is not implemented for <{xTarget.osImage}>.",exitCode=EXIT.Implementation)

    # The appLog will be the file object flying around for logging into app.out
    appLog = ftOpenFile(os.path.join(getSetting('workDir'),'app.out'), 'a')
    appLog.write('-'*20 + "<FETT-APPS-OUT>" + '-'*20 + '\n\n')
    setSetting("appLog",appLog)

    # Install
    for appModule in xTarget.appModules:
        appModule.install(xTarget)
        appLog.flush()
    return

@decorate.debugWrap
@decorate.timeWrap
def watchdog(targetId):
    """
    This function keeps monitoring the target, and if it goes down, it resets it
    " There are 3 things that we need to make sure while developing this:
    " 1. Can watch
    " 2. resets
    " 3. Is able to exit
    """
    listenQueue = getSetting('watchdogQueue',targetId=targetId)
    while (listenQueue.empty()): #Main thread didn't exit yet, and watchdog no error
        def handleError(errorString):
            """
            Either resets the target and returns False so the loop continues, 
            OR returns True and break the loop
            """
            if (isEnabled('interactiveShell')):
                print("\n",flush=True)
            if (isEnabled('resetOnWatchdog')):
                warnAndLog(f"<target{targetId}>: {errorString}! Resetting...")
                # Here we should reset
                fett.target.launch.resetTarget(getSetting('targetObj',targetId=targetId)) 
                printAndLog("Please press Enter to return to the interactive shell...")
                return False
            else:
                errorAndLog(f"<target{targetId}>: {errorString}!")
                return True

        # Check process
        if not isTargetAlive(targetId) and handleError("Target is not alive"):
            break

        time.sleep(10)

    # Will send an item to the queue anyway; If we're here because of error:
    #   Yes: So this will exit the main thread
    #   No: So the item in the queue will not be read
    fett.cyberPhys.launch.ftQueueUtils("cyberPhysMain:queue", getSetting('cyberPhysQueue'), 'put')

    return

@decorate.debugWrap
@decorate.timeWrap
def isTargetAlive(targetId):
    xTarget = getSetting('targetObj',targetId=targetId)
    if not xTarget.process.isalive():
        printAndLog(f"{xTarget.targetIdInfo}process is not alive.")
        return False

    if not xTarget.pingTarget(exitOnError=False,pingAttempts=10,printSuccess=False):
        printAndLog(f"{xTarget.targetIdInfo}does not respond to ping.")
        return False

    osImage = getSetting('osImage',targetId=targetId)
    if osImage == 'FreeRTOS':
        # TODO
        logAndExit (f"{xTarget.targetIdInfo}<isTargetAlive> is not implemented for <{osImage}>.",exitCode=EXIT.Implementation)
    elif osImage in ['debian', 'FreeBSD']:
        if not otaserver.deploymentTest(xTarget):
            printAndLog(f"{xTarget.targetIdInfo}ota server doesn't respond. Attempting to recover.")
            if not otaserver.restart(xTarget):
                printAndLog(f"{xTarget.targetIdInfo}ota recovery failed.")
                return False
    else:
        logAndExit (f"{xTarget.targetIdInfo}<isTargetAlive> is not implemented for <{osImage}>.",exitCode=EXIT.Implementation)

    return True
