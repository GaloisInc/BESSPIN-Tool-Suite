#! /usr/bin/env python3
"""
The main file for running cyberPhys
"""

from besspin.base.utils.misc import *
import besspin.cyberPhys.launch
import besspin.target.launch
from besspin.base.threadControl import ftQueueUtils
from besspin.cyberPhys import otaserver, infotainmentserver

# Import for CAN bus
from besspin.cyberPhys.canlib import UDPBus, Message
from besspin.cyberPhys.canspecs import CAN_ID_HEARTBEAT_ACK, CAN_ID_HEARTBEAT_REQ

import struct
import ipaddress

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
    appLog.write('-'*20 + "<BESSPIN-TOOL-SUITE-OUT>" + '-'*20 + '\n\n')
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
                besspin.target.launch.resetTarget(getSetting('targetObj',targetId=targetId))
                printAndLog("Please press Enter to return to the interactive shell...")
                return False
            else:
                errorAndLog(f"<target{targetId}>: {errorString}!")
                return True

        responses = []
        while not wHeartbeatQueue.empty():
            responses.append(ftQueueUtils(f"watchDogHeartbeatQueue{targetId}",wHeartbeatQueue,'get'))

        xTarget = getSetting('targetObj',targetId=targetId)
        targetIp = xTarget.ipTarget

        try:
            msgs = [msg for msg in responses if str(ipaddress.IPv4Address(struct.unpack('<I', msg.data[0:4])[0])) == targetIp]
            if msgs:
                msg = msgs[0]
                printAndLog(f"<target{targetId}>: Heartbeat received, {msg.timestamp}s, \
                    reqID: {int.from_bytes(msg.data[4:8],'big')}",doPrint=False)
            else:
                warnAndLog(f"<target{targetId}>: Heartbeat missed",doPrint=False)
                # TODO: do something more here
        except Exception as exc:
            warnAndLog(f"<target{targetId}> Exception occured processing hearbeat response: {exc}") 

        # Check process
        if not isTargetAlive(targetId) and handleError("Target is not alive"):
            appLog = getSetting('appLog',targetId=targetId)
            appLog.close()
            break

        time.sleep(0.5) # TODO: make the timeout configurable

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
    vcu118BroadcastIp = getSetting('vcu118BroadcastIp')
    cyberPhysCanbusPort = getSetting('cyberPhysCanbusPort')

    try:
        canbus = UdpBus(ip=vcu118BroadcastIp,port=cyberPhysCanbusPort)
    except Exception as exc:
        logAndExit(f"<heartBeatListener> Failed to instantiate <UdpBus> with port {canbusPort}.",exc=exc,exitCode=EXIT.Run)
    try:
        canbus.set_filters([{"can_id": CAN_ID_HEARTBEAT_ACK, "can_mask": 0XFFFFFFFF, "extended": True}])
    except Exception as exc:
        logAndExit(f"<heartBeatListener> Failed to set canbus filters.",exc=exc,exitCode=EXIT.Run)

    # get queues from settings
    cnt = 0
    watchdog_queues = {}
    for targetId in range(1,getSetting('nTargets')+1):
        watchdog_queues[targetId] = getSetting('watchdogHeartbeatQueue', targetId=targetId)

    while (listenQueue.empty()): #Main thread didn't exit yet, and watchdog no error
        cnt += 1
        try:
            heartbeat_req = Message(arbitration_id=CAN_ID_HEARTBEAT_REQ,
                                    is_extended_id=True,
                                    data=list(cnt.to_bytes(4, byteorder = 'big')))
            canbus.send(heartbeat_req)
        except Exception as exc:
            logAndExit(f"<heartBeatListener> Failed to send heartbeat request to \
                {vcu118BroadcastIp}:{cyberPhysCanbusPort}",exc=exc,exitCode=EXIT.Run)
        printAndLog (f"<heartBeatListener> Sending request", doPrint=False)

        # Assume one second window to receive watchdog responses
        endOfWait = time.time() + 1.0 # TODO: make the timeout a variable
        responses = []
        while (time.time() < endOfWait): #and (len(responses) < getSetting('nTargets')):
            heartbeat_ack = canbus.recv(timeout=1.0) # TODO: make the timeout a variable
            if heartbeat_ack:
                responses.append(heartbeat_ack)

        if (len(responses) < getSetting('nTargets')):
            warnAndLog(f"<heartBeatListener> Failed to receive on canbus.", doPrint=False)

        for q in watchdog_queues.values():
            for msg in responses[::-1]:
                try:
                    # Push only responses to the current request
                    if msg.dlc == 8 and int.from_bytes(msg.data[4:8], "big") == cnt:
                        q.put(msg)
                except Exception as exc:
                    warnAndLog(f"<heartBeatListener> Exception occured processing hearbeat response: {exc}")

        time.sleep(1.0) # TODO: make the timeout a variable

    # Will send an item to the queue anyway; If we're here because of error:
    #   Yes: So this will exit the main thread
    #   No: So the item in the queue will not be read
    ftQueueUtils("cyberPhysMain:queue", getSetting('cyberPhysQueue'), 'put')

    return