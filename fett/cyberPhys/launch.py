#! /usr/bin/env python3
""" 
The main file to start launching cyberPhys
"""

from fett.base.utils.misc import *
from fett.target import launch
import threading

@decorate.debugWrap
@decorate.timeWrap
def startCyberPhys():
    # Create an exit lock so that the tool "actually" exits only once!
    setSetting('exitLock',threading.Lock())
    # Create a network lock to protect all network operations while multithreading
    setSetting('networkLock',threading.Lock())

    # start/prepareEnv/Launch
    launchThreads = startThreadPerTarget(launch.startFett)
    for launchThread in launchThreads:
        launchThread.join()

@decorate.debugWrap
@decorate.timeWrap
def endCyberPhys():
    endThreads = startThreadPerTarget(launch.endFett,mapTargetSettingsToKwargs=[('xTarget','targetObj')])
    for endThread in endThreads:
        endThread.join()

@decorate.debugWrap
@decorate.timeWrap
def startThreadPerTarget(func, tArgs=(), tKwargs={}, addTargetIdToKwargs=True, mapTargetSettingsToKwargs=[]):
    xThreads = []
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
    