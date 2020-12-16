#! /usr/bin/env python3
""" 
The main file for running cyberPhys
"""

from fett.base.utils.misc import *
import fett.cyberPhys.launch
import fett.target.launch

@decorate.debugWrap
@decorate.timeWrap
def runCyberPhys(xTarget):
    # here anything that needs to be done on the targets before handing the user the prompt
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
        if ((not getSetting('targetObj',targetId=targetId).process.isalive()) 
            and handleError("Target is down")):
            break

        # Ping network
        if ((not getSetting('targetObj',targetId=targetId).pingTarget(
                                    exitOnError=False,pingAttempts=10,printSuccess=False))
             and handleError("Failed to ping target")):
            break

        time.sleep(10)

    # Will send an item to the queue anyway; If we're here because of error:
    #   Yes: So this will exit the main thread
    #   No: So the item in the queue will not be read
    fett.cyberPhys.launch.ftQueueUtils("cyberPhysMain:queue", getSetting('cyberPhysQueue'), 'put')

    return
