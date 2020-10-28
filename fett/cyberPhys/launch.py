#! /usr/bin/env python3
""" 
The main file to start launching cyberPhys
"""

from fett.base.utils.misc import *
import fett.target.launch
import fett.cyberPhys.interactive
import fett.cyberPhys.run
import threading, queue

@decorate.debugWrap
@decorate.timeWrap
def startCyberPhys():
    # Create a network lock to protect network operations while multithreading
    setSetting('networkLock',threading.Lock())
    # Create a vcu118 boards(s) lock 
    setSetting('vcu118Lock',threading.Lock())

    printAndLog (f"Launching FETT <cyberPhys mode>...")
    # start/prepareEnv/Launch
    runThreadPerTarget(fett.target.launch.startFett)
    printAndLog (f"FETT <cyberPhys mode> is launched!")

    # - We need a way for communication between this (main thread) and the watchdog threads [and interacting thread].
    # - We'll use queues. Each queue should be used in one-way communication. So there is a main queue that is watched here.
    # - And we create a queue for each watchdog [and interacting thread] (Creating a threading.Event() is possible, but not
    #   for interactive, so we'll keep it all as queues for consistency and more future compatibility).
    exitQueue = queue.Queue(maxsize=getSetting('nTargets')+int(isEnabled('interactiveShell')))
    setSetting('cyberPhysQueue',exitQueue)
    for targetId in range(1,getSetting('nTargets')+1):
        setSetting('watchdogQueue',queue.Queue(maxsize=1),targetId=targetId)

    # Start the watchdogs
    allThreads = runThreadPerTarget(fett.cyberPhys.run.watchdog,onlyStart=True)

    if (isEnabled('interactiveShell')):
        # Pipe the UART
        runThreadPerTarget(startUartPiping)
        printAndLog("You may access the UART using: <socat - TCP4:localhost:${port}> or <nc localhost ${port}>.")
        # Create an interactor queue
        # Interactor can be terminated because of a watchdog reported error, or by the user
        setSetting('interactorQueue',queue.Queue(maxsize=2))

        # Start the interactive shell
        allThreads += runThreadPerTarget(fett.cyberPhys.interactive.interact,
                        addTargetIdToKwargs=False, onlyStart=True, singleThread=True)

    # Start the watch on the watchdogs [+ interactive shell]
    ftQueueUtils("cyberPhysMain:queue",exitQueue,'get') #block until receiving an error or termination
    
    # Terminating all threads
    for targetId in range(1,getSetting('nTargets')+1):
        ftQueueUtils(f"target{targetId}:watchdog:queue",getSetting('watchdogQueue',targetId=targetId),'put')
    if (isEnabled('interactiveShell')):
        ftQueueUtils("interactiveShell:queue",getSetting('interactorQueue'),'put',itemToPut='main')

    # Waiting for all threads to terminate
    for xThread in allThreads:
        xThread.join()

    return

@decorate.debugWrap
@decorate.timeWrap
def endCyberPhys():
    printAndLog (f"Terminating FETT...")
    if (isEnabled('interactiveShell')):
        # End UART piping
        runThreadPerTarget(endUartPiping)
    # Terminate the targets
    runThreadPerTarget(fett.target.launch.endFett,
                    mapTargetSettingsToKwargs=[('xTarget','targetObj')],
                    addTargetIdToKwargs=False)

@decorate.debugWrap
@decorate.timeWrap
def runThreadPerTarget(func, tArgs=(), tKwargs=None, addTargetIdToKwargs=True, 
        mapTargetSettingsToKwargs=[], onlyStart=False, singleThread=False):
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
    singleThread: If enabled, instead of a thread per target, only a single thread is created
    """
    xThreads = []
    if (tKwargs is None):
        tKwargs = {}
    if (singleThread):
        allTargets = range(1)
    else:
        allTargets = range(1,getSetting('nTargets')+1)
    for iTarget in allTargets:
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
@decorate.timeWrap
def ftQueueUtils(queueName,xQueue,method,timeout=None,itemToPut=True,exitFunc=logAndExit):
    if(method=='put'):
        try:
            return xQueue.put(itemToPut, block=True, timeout=timeout)
        except Exception as exc:
            exitFunc(f"Failed to put <{itemToPut}> to <{queueName}>.",exc=exc,exitCode=EXIT.Dev_Bug)
    elif(method=='get'):
        try:
            return xQueue.get(block=True, timeout=timeout)
        except Exception as exc:
            exitFunc(f"Failed to get from <{queueName}>.",exc=exc,exitCode=EXIT.Dev_Bug)
    else:
        exitFunc(f"<ftQueueUtils> not implemented for method<{method}>.",exitCode=EXIT.Implementation)

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
    