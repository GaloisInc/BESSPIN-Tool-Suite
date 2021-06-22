#! /usr/bin/env python3
"""
The main file for running cyberPhys
"""

from besspin.base.utils.misc import *
import besspin.target.launch
from besspin.base.threadControl import ftQueueUtils
from besspin.cyberPhys import otaserver, infotainmentserver

# Import for CAN bus
from besspin.cyberPhys.cyberphyslib.cyberphyslib.canlib import UdpBus, Message, CAN_ID_HEARTBEAT_ACK, CAN_ID_HEARTBEAT_REQ

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
        xTarget.terminateAndExit(f"{xTarget.targetIdInfo}<runCyberPhys> is not implemented for <{xTarget.osImage}>.",exitCode=EXIT.Implementation)

    # Enable SSH on root/riscv
    if (xTarget.osImage=='debian'):
        xTarget.enableSshOnRoot()

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
def resetComponent(component, targetId):
    xTarget = getSetting('targetObj',targetId=targetId)
    if component == "ota":
        otaserver.restart(xTarget)
    elif component == "infotainment":
        infotainmentserver.restart(xTarget)

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
        if not infotainmentserver.isServiceRunning(xTarget):
            printAndLog(f"{xTarget.targetIdInfo}infotainment server didn't respond.")
    return True

@decorate.debugWrap
def heartBeatListener():
    """
    Sends heartbeat requests and listens to responses.
    The responses are then sent to each target's watchdog
    This is a workaround because we can bind to the same port only once.
    """
    listenQueue = getSetting('heartbeatQueue')
    # Hardcoded targetId=1 because there is always at least one target
    xTarget = getSetting('targetObj', targetId=1)
    broadcastIp = xTarget.ipBroadcast
    cyberPhysCanbusPort = getSetting('cyberPhysCanbusPort')

    try:
        printAndLog(f"<heartBeatListener> Starting CAN bus on {broadcastIp}:{cyberPhysCanbusPort}", doPrint=False)
        canbus = UdpBus(ip=broadcastIp,port=cyberPhysCanbusPort)
    except Exception as exc:
        logAndExit(f"<heartBeatListener> Failed to instantiate <UdpBus> with {broadcastIp}:{cyberPhysCanbusPort}.",exc=exc,exitCode=EXIT.Run)
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
                {broadcastIp}:{cyberPhysCanbusPort} with exception {exc}",exc=exc,exitCode=EXIT.Run)
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
