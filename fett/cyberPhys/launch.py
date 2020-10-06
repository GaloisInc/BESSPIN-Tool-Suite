#! /usr/bin/env python3
""" 
The main file to start launching cyberPhys
"""

from fett.base.utils.misc import *
from fett.target import launch
from fett.cyberPhys.interactive import interact
import threading

@decorate.debugWrap
@decorate.timeWrap
def startCyberPhys():
    # Create a network lock to protect network operations while multithreading
    setSetting('networkLock',threading.Lock())

    printAndLog (f"Launching FETT <cyberPhys mode>...")
    # start/prepareEnv/Launch
    runThreadPerTarget(launch.startFett)
    printAndLog (f"FETT <cyberPhys mode> is launched!")

    if (isEnabled('interactiveShell')):
        # Pipe the UART
        runThreadPerTarget(startUartPiping)
        printAndLog("You may access the UART using: <socat - TCP4:localhost:${port}> or <nc localhost ${port}>.")
        # start the interactive shell
        interact()

@decorate.debugWrap
@decorate.timeWrap
def endCyberPhys():
    #End UART piping
    runThreadPerTarget(endUartPiping)
    #terminate the targets
    runThreadPerTarget(launch.endFett,
                    mapTargetSettingsToKwargs=[('xTarget','targetObj')],
                    addTargetIdToKwargs=False)

@decorate.debugWrap
@decorate.timeWrap
def runThreadPerTarget(func, tArgs=(), tKwargs=None, addTargetIdToKwargs=True, mapTargetSettingsToKwargs=[], onlyStart=False):
    """
    This function starts a thread for each target in cyberPhys mode
    func: A handle to the function of the thread.
    tArgs: The tuples of args with which the thread function is to be called
    tKwargs: The dictionary of kwargs with which the thread function is to be called.
            (Note that it has to be initialized to None because of how functions in 
            python are defined as first class objects)
    addTargetIdToKwargs: If enabled, kwargs will have "targetId=${iTarget}" for iTarget in [1,..,nTargets]
    mapTargetSettingsToKwargs: A list of tuples (xKwargName, xSettingName), for each tuple, kwarfs will be
                                augmented with "xKwargName=_settings[${iTarget}][xSettingName]"
    onlyStart: If enabled, it will just launch the threads without waiting for them to finish.
    """
    xThreads = []
    if (tKwargs is None):
        tKwargs = {}
    for iTarget in range(1,getSetting('nTargets')+1):
        if (addTargetIdToKwargs):
            tKwargs['targetId'] = iTarget
        for kwargName,xSetting in mapTargetSettingsToKwargs:
            tKwargs[kwargName] = getSetting(xSetting,targetId=iTarget)
        xThread = threading.Thread(target=func, args=tArgs, kwargs=tKwargs)
        xThread.daemon = True
        getSetting('trash').throwThread(xThread,f"<{func.__name__}> for target{iTarget}")
        xThread.start()
        xThreads.append(xThread)

    if (not onlyStart):
        for xThread in xThreads:
            xThread.join()

    return xThreads

@decorate.debugWrap
def startUartPiping(targetId):
    xTarget = getSetting('targetObj',targetId=targetId)
    uartPipePort = xTarget.findPort(portUse='uartFwdPort')
    setSetting('uartPipePort',uartPipePort,targetId=targetId)
    try:
        xTarget.uartSocatProc = subprocess.Popen(
            ['socat', 'STDIO,ignoreeof', f"TCP-LISTEN:{uartPipePort},reuseaddr,fork,max-children=1"],
            stdout=xTarget.process.child_fd,stdin=xTarget.process.child_fd,stderr=xTarget.process.child_fd)
    except Exception as exc:
        xTarget.shutdownAndExit(f"{xTarget.targetIdInfo}startUartPiping: Failed to start the piping.",
            exc=exc,exitCode=EXIT.Run)

    printAndLog (f"{xTarget.targetIdInfo}UART is piped to port <{uartPipePort}>.")

@decorate.debugWrap
def endUartPiping(targetId):
    xTarget = getSetting('targetObj',targetId=targetId)
    try:
        xTarget.uartSocatProc.kill() # No need for fancier ways as we use Popen with shell=False
    except Exception as exc:
        warnAndLog(f"{xTarget.targetIdInfo}endUartPiping: Failed to kill the process.",exc=exc)
    