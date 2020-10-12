#! /usr/bin/env python3
""" 
The main file for running cyberPhys
"""

from fett.base.utils.misc import *
import fett.cyberPhys.launch

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
    targetObj = getSetting('targetObj',targetId=targetId)
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
                errorAndLog(f"<target{targetId}>: Reset target on watchdog is not yet implemented.")
                return True #Should be False after reset is implemented
            else:
                errorAndLog(f"<target{targetId}>: {errorString}!")
                return True

        time.sleep(10)

        # Check process
        if ((not targetObj.process.isalive()) and handleError("Target is down")):
            break

        # Ping network
        if ((not targetObj.pingTarget(exitOnError=False,pingAttempts=3,printSuccess=False))
             and handleError("Failed to ping target")):
            break

    # Will send an item to the queue anyway; If we're here because of error:
    #   Yes: So this will exit the main thread
    #   No: So the item in the queue will not be read
    fett.cyberPhys.launch.ftQueueUtils("cyberPhysMain:queue", getSetting('cyberPhysQueue'), 'put')

    return
