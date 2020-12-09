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