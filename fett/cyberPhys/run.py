#! /usr/bin/env python3
""" 
The main file for running cyberPhys
"""
import time

from fett.base.utils.misc import *
import fett.cyberPhys.launch
import fett.target.launch

from fett.cyberPhys import otaserver, infotainmentserver

# Import for CAN bus
from fett.cyberPhys.canlib import UDPBus, Message
from fett.cyberPhys.canspecs import CAN_ID_HEARTBEAT_ACK, CAN_ID_HEARTBEAT_REQ

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
        xTarget.appModules = [otaserver, infotainmentserver]
    else:
        xTarget.terminateAndExit(f"{xTarget.targetIdInfo}<runApp> is not implemented for <{xTarget.osImage}>.",exitCode=EXIT.Implementation)

    # The appLog will be the file object flying around for logging into app.out
    appLog = ftOpenFile(os.path.join(getSetting('workDir'),f"app{xTarget.targetSuffix}.out"), 'a')
    appLog.write('-'*20 + "<FETT-APPS-OUT>" + '-'*20 + '\n\n')
    setSetting("appLog",appLog,targetId=xTarget.targetId)

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
            appLog = getSetting('appLog',targetId=targetId)
            appLog.close()
            break

        time.sleep(1)

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
    if osImage in ['debian', 'FreeBSD']:
        if not otaserver.isServiceRunning(xTarget):
            printAndLog(f"{xTarget.targetIdInfo}ota server didn't respond.")
            # otaserver.restart(xTarget)
            # return otaserver.isServiceRunning(xTarget)

    return True

@decorate.debugWrap
@decorate.timeWrap
def watchdogHeartbeat(targetId):
    # store the relevant target info
    ip_addr = getSetting('vcu118BroadcastIp')
    port = getSetting('cyberPhysCanbusPort')
    s_fails = 0
    count = 0
    max_s_fails = 4

    # FIXME: correct this for the filtering
    whitelist = None
    blacklist = None

    # watchdog parameters
    ntargets = getSetting('nTargets')
    update_period = 1.0
    listenQueue = getSetting('watchdogHeartbeatQueue',targetId=targetId)
    canbus = UDPBus("", port,
                            whitelist = whitelist,
                            blacklist = blacklist)
    canbus.set_filters([{"can_id": CAN_ID_HEARTBEAT_ACK, "can_mask": 0XFFFFFFFF, "extended": True}])

    printAndLog(f"<targetId: {targetId}> starting heartbeat with whitelist {whitelist} and blacklist {blacklist}")

    while (listenQueue.empty()): #Main thread didn't exit yet, and watchdog no error
        count += 1 # NOTE: why increment first?

        # create a message based on tick
        heartbeat_req = Message(arbitration_id=CAN_ID_HEARTBEAT_REQ,
                                    is_extended_id=True,
                                    data=list(count.to_bytes(4, byteorder = 'big')))
        canbus.send(heartbeat_req, ip_addr, port)
        printAndLog (f"<targetId: {targetId}>: FETT <heartBeatWatchDog mode> sending message")

        #  Assume one second window to receive watchdog responses
        endOfWait = time.time() + 1.0
        responses = []
        while (time.time() < endOfWait) and (len(responses) < ntargets):
            heartbeat_ack = canbus.recv(timeout=0.1)
            if heartbeat_ack:
                print(f"RX: {heartbeat_ack}")
                responses.append(heartbeat_ack)

        # record successive failures
        if len(responses) == ntargets:
            s_fails = 0
        else:
            s_fails += 1

        # check for heartbeat failure
        if s_fails >= max_s_fails:
            # NOTE: fix against the data inside of the packet?
            errorAndLog(f"<targetId: {targetId}> watchdog heartbeat failure criteria met: number of fails {s_fails}")
            return
        time.sleep(update_period)

    # this state should not be entered -- put in cyberphys main queue to exit main thread
    fett.cyberPhys.launch.ftQueueUtils("cyberPhysMain:queue", getSetting('cyberPhysQueue'), 'put')
    return
