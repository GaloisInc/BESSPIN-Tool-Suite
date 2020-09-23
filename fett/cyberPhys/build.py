#! /usr/bin/env python3
"""
Building any binaries or images for cyberPhys
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def buildCyberPhys (targetId=None):
    targetInfo = f" <for target{targetId}>" if (targetId) else ''
    targetSuffix = f'_{targetId}' if (targetId) else ''

    # Create build directory
    buildDir = os.path.join(getSetting('workDir'), f'build{targetSuffix}')
    mkdir(buildDir)
    setSetting('buildDir',buildDir,targetId=targetId)

    # Nothing to send so far
    setSetting('sendTarballToTarget',False,targetId=targetId)

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOS(targetId=None):
    #Netboot on FreeRTOS?
    if (isEqSetting('elfLoader','netboot',targetId=targetId)):
        warnAndLog (f"Netboot cannot load FreeRTOS image. Falling to JTAG.", doPrint=False)
        setSetting('elfLoader','JTAG')

    # define some paths
    osImageAsm = os.path.join(getSetting('osImagesDir',targetId=targetId),f"{getSetting('osImage')}.asm")
    setSetting('osImageAsm',osImageAsm,targetId=targetId)

    logAndExit("<cyberPhys:prepareFreeRTOS> is not yet implemented.",exitCode=EXIT.Implementation)
    return

