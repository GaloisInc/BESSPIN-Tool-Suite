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
    # Create a network lock to protect all network operations while multithreading
    setSetting('networkLock',threading.Lock())

    printAndLog (f"Launching FETT <cyberPhys mode>...")

    # start/prepareEnv/Launch
    launchThreads = startThreadPerTarget(launch.startFett)
    for launchThread in launchThreads:
        launchThread.join()

    printAndLog (f"FETT <cyberPhys mode> is launched!")

    # start the interactive shell
    interact()

@decorate.debugWrap
@decorate.timeWrap
def endCyberPhys():
    endThreads = startThreadPerTarget(launch.endFett,
                    mapTargetSettingsToKwargs=[('xTarget','targetObj')],
                    addTargetIdToKwargs=False)
    for endThread in endThreads:
        endThread.join()

@decorate.debugWrap
@decorate.timeWrap
def startThreadPerTarget(func, tArgs=(), tKwargs=None, addTargetIdToKwargs=True, mapTargetSettingsToKwargs=[]):
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
    return xThreads
    