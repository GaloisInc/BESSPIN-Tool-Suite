#! /usr/bin/env python3
"""
The main file for running cyberPhys
"""

from fett.base.utils.misc import *
import fett.cyberPhys.launch
import fett.target.launch
from fett.base.threadControl import ftQueueUtils
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

    # queue that heartbeat responses will come from
    wHeartbeatQueue = getSetting('watchdogHeartbeatQueue', targetId=targetId)

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

        # responses
        responses = []
        while not wHeartbeatQueue.empty():
            responses.append(ftQueueUtils(f"watchDogHeartbeatQueue{targetId}",wHeartbeatQueue,'get'))
        #printAndLog(f"<targetId {targetId}> Watchdog {responses}")
        # TODO: check for heartbeat failure here, will be fixed later

        # Check process
        if not isTargetAlive(targetId) and handleError("Target is not alive"):
            appLog = getSetting('appLog',targetId=targetId)
            appLog.close()
            break

        time.sleep(1)

    # Will send an item to the queue anyway; If we're here because of error:
    #   Yes: So this will exit the main thread
    #   No: So the item in the queue will not be read
    ftQueueUtils("cyberPhysMain:queue", getSetting('cyberPhysQueue'), 'put')

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
            # NOTE: this code is commented out now, need to test OTA more before re-enabling or deleting
            # this code for good
            # otaserver.restart(xTarget)
            # return otaserver.isServiceRunning(xTarget)

    return True

@decorate.debugWrap
def heartBeatListener():
    """
    Sends heartbeat requests and listens to responses.
    The responses are then sent to each target's watchdog
    This is a workaround because we can bind to the same port only once.
    """
    listenQueue = getSetting('heartbeatQueue')
    canbusPort = getSetting('cyberPhysCanbusPort')
    try:
        canbus = UDPBus("",canbusPort)
    except Exception as exc:
        logAndExit(f"Failed to instantiate <UDPBus> with port {canbusPort}.",exc=exc,exitCode=EXIT.Run)
    try:
        canbus.set_filters([{"can_id": CAN_ID_HEARTBEAT_ACK, "can_mask": 0XFFFFFFFF, "extended": True}])
    except Exception as exc:
        logAndExit(f"Failed to set canbus filters.",exc=exc,exitCode=EXIT.Run)

    # get queues from settings
    cnt = 0
    watchdog_queues = {}
    for targetId in range(1,getSetting('nTargets')+1):
        watchdog_queues[targetId] = getSetting('watchdogHeartbeatQueue', targetId=targetId)

    # Hearbeat request settings
    vcu118BroadcastIp = getSetting('vcu118BroadcastIp')
    cyberPhysCanbusPort = getSetting('cyberPhysCanbusPort')

    while (listenQueue.empty()): #Main thread didn't exit yet, and watchdog no error
        cnt += 1
        try:
            heartbeat_req = Message(arbitration_id=CAN_ID_HEARTBEAT_REQ,
                                    is_extended_id=True,
                                    data=list(cnt.to_bytes(4, byteorder = 'big')))
            canbus.send(heartbeat_req, vcu118BroadcastIp, cyberPhysCanbusPort)
        except Exception as exc:
            logAndExit(f"Failed to send heartbeat request to {vcu118BroadcastIp}:{cyberPhysCanbusPort}",exc=exc,exitCode=EXIT.Run)
        printAndLog (f"FETT <heartBeatWatchDog mode> sending request", doPrint=False)

        # Assume one second window to receive watchdog responses
        endOfWait = time.time() + 1.0
        responses = []
        while (time.time() < endOfWait) and (len(responses) < getSetting('nTargets')):
            heartbeat_ack = canbus.recv(timeout=0.1)
            if heartbeat_ack:
                responses.append(heartbeat_ack)

        if (len(responses) < getSetting('nTargets')):
            logAndExit(f"Failed to receive on cabus.",exc=exc,exitCode=EXIT.Run)

        # send the messages to the queues
        # NOTE: no filtering is done; the watchdogs
        # must determine if the responses are relevant
        for q in watchdog_queues.values():
            for m in responses[::-1]:
                q.put(m)
        time.sleep(1)

    # Will send an item to the queue anyway; If we're here because of error:
    #   Yes: So this will exit the main thread
    #   No: So the item in the queue will not be read
    ftQueueUtils("cyberPhysMain:queue", getSetting('cyberPhysQueue'), 'put')

    return