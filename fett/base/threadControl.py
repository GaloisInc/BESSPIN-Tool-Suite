#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This has the functions needed for thread control
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

from fett.base.utils.misc import *
import threading

@decorate.debugWrap
def createFettLocks():
    # Create a network lock to protect network operations while multithreading
    setSetting('networkLock',threading.Lock())
    # Create the locks needed for vcu118 board(s)
    """
    For VCU118, we're using a conservative approach for the sake of robustness;
    The following operations are all protected by a single lock (openocdLock):
    - clear flash
    - program bitfile
    - start an openocd process + gdb setup and connect
    """
    setSetting('openocdLock',threading.Lock())
    # We also need a lock for TFTP
    setSetting('tftpLock',threading.Lock())
    # Create a lock for using the FreeRTOS submodule directory or FreeRTOS general settings
    setSetting('FreeRTOSLock',threading.Lock())
    # When programming flash, we need to wait for all targets before power cycling
    if (isEqSetting('mode','cyberPhys')):
        setSetting('vcu118FlashCounter',Counter(getSetting("nVcu118Targets")))

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


class Counter:
    def __init__(self,goldenCount):
        self._count = 0
        self.goldenCount = goldenCount
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._event.clear() #to be explicit

    def incAndCheck(self): #Have to be done in the same lock acquiring to avoid multiple calls
        with self._lock:
            self._count += 1
            return (self._count == self.goldenCount)

    def waitForEverything(self):
        self._event.wait()

    def userIsReady(self):
        self._event.set()

