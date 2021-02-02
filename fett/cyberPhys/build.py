#! /usr/bin/env python3
"""
Building any binaries or images for cyberPhys
"""

from fett.base.utils.misc import *
import fett.target.build
from fett.apps.build import cpFilesToBuildDir, getBinDir, buildDirPathTuple
import functools

@decorate.debugWrap
@decorate.timeWrap
def buildCyberPhys (targetId=None):
    _targetInfo = f" <for target{targetId}>" if (targetId) else ''
    targetSuffix = f'_{targetId}' if (targetId) else ''

    # Create build directory
    buildDir = os.path.join(getSetting('workDir'), f'build{targetSuffix}')
    mkdir(buildDir)
    setSetting('buildDir',buildDir,targetId=targetId)

    # Prepare files for each target
    if (getSetting('osImage',targetId=targetId) in ['debian', 'FreeBSD']):
        # ota server, infotainment
        tarName = os.path.join(getSetting('buildDir',targetId=targetId),getSetting('tarballName'))
        buildOtaUpdateServer(tarName, targetId=targetId)
        buildInfotainmentServer(tarName, targetId=targetId)
        setSetting('sendTarballToTarget',True,targetId=targetId)
    else:
        # Nothing to send
        setSetting('sendTarballToTarget',False,targetId=targetId)

@decorate.debugWrap
@decorate.timeWrap
def copyOtaUpdateserverFiles(tarName, targetId=None):
    """
    Stuff the server binary into a tar file
    """
    # Just grab the pre-built binary
    osImage = getSetting('osImage',targetId=targetId)
    otaAppDir = getCyberphysAppDir('ota-update-server')
    otaBinDir = getBinDir('ota-update-server',targetId=targetId)
    cpFilesToBuildDir (otaBinDir, pattern="ota.elf", targetId=targetId)
    cpFilesToBuildDir (otaAppDir, pattern="key", targetId=targetId)
    tarFiles = ["ota.elf","key"]

    runtimeFilesDir = os.path.join(otaAppDir, osImage)
    if osImage == 'debian':
        cpFilesToBuildDir (runtimeFilesDir, pattern="ota.service", targetId=targetId)
        tarFiles += ["ota.service"]
    elif osImage == 'FreeBSD':
        cpFilesToBuildDir (runtimeFilesDir, pattern="ota.sh", targetId=targetId)
        tarFiles += ["ota.sh"]
    else:
        logAndExit (f"Installing ota-update-server is not supported on <{osImage}>",
                    exitCode=EXIT.Dev_Bug)
    
    buildDirPathTuplePartial = functools.partial(buildDirPathTuple, targetId=targetId)
    filesList=map(buildDirPathTuplePartial, tarFiles)
    return filesList

@decorate.debugWrap
@decorate.timeWrap
def copyInfotainmentServerFiles(tarName, targetId=None):
    """
    Stuff the server binary into a tar file
    """
    # grab the pre-built binary
    osImage = getSetting('osImage', targetId=targetId)
    infotainmentBinDir = getBinDir('infotainment-server', targetId=targetId)
    cpFilesToBuildDir(infotainmentBinDir, pattern="infotainment_server", targetId=targetId)
    tarFiles = ["infotainment_server"]

    infotainmentAppDir = getCyberphysAppDir('infotainment-server')
    runtimeFilesDir = os.path.join(infotainmentAppDir, osImage)
    if osImage == 'debian':
        cpFilesToBuildDir(runtimeFilesDir, pattern="infotainment-server.service", targetId=targetId)
        tarFiles += ["infotainment-server.service"]
    elif osImage == 'FreeBSD':
        cpFilesToBuildDir(runtimeFilesDir, pattern="infotainment-server.sh", targetId=targetId)
        tarFiles += ["infotainment-server.sh"]
    else:
        logAndExit(f"Installing infotainment-server is not supported on <{osImage}>",
                   exitCode=EXIT.Dev_Bug)

    buildDirPathTuplePartial = functools.partial(buildDirPathTuple, targetId=targetId)
    filesList=map(buildDirPathTuplePartial, tarFiles)
    return filesList

@decorate.debugWrap
@decorate.timeWrap
def buildOtaUpdateServer(tarName, targetId=None):
    if (isEnabled('buildApps')):
        # Build server
        logAndExit (f"Building from source is not supported for the OTA update server application",
                   exitCode=EXIT.Configuration)
    else:
        tarFiles = copyOtaUpdateserverFiles(tarName,targetId=targetId)
        #Create the tarball here to be sent to target
        tar (tarName, tarFiles)

@decorate.debugWrap
@decorate.timeWrap
def buildInfotainmentServer(tarName, targetId=None):
    if (isEnabled('buildApps')):
        # Build server
        logAndExit(f"Building from source is not supported for the infotainment server application",
                   exitCode=EXIT.Configuration)
    else:
        tarFiles = copyInfotainmentServerFiles(tarName, targetId=targetId)
        # create the tarball here to be sent to target
        tar(tarName, tarFiles)

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOS(targetId=None):
    #Netboot on FreeRTOS?
    if (isEqSetting('elfLoader','netboot',targetId=targetId)):
        warnAndLog (f"Netboot cannot load FreeRTOS image. Falling to JTAG.", doPrint=False)
        setSetting('elfLoader','JTAG',targetId=targetId)

    # define some paths
    osImageAsm = os.path.join(getSetting('osImagesDir',targetId=targetId),"FreeRTOS.asm")
    setSetting('osImageAsm',osImageAsm,targetId=targetId)

    #build it
    fett.target.build.freeRTOSBuildChecks(targetId=targetId,freertosFork="classic")

    #copy the C files, .mk files, and any directory
    copyDir(os.path.join(getSetting('repoDir'),'fett','cyberPhys','srcFreeRTOS'),getSetting('buildDir',targetId=targetId),copyContents=True)
    copyDir(os.path.join(getSetting('repoDir'),'build','cyberphys','canlib'),getSetting('buildDir',targetId=targetId),copyContents=True)

    fett.target.build.prepareFreeRTOSNetworkParameters(targetId=targetId)
    buildDir = getSetting('buildDir',targetId=targetId)
    fett.target.build.buildFreeRTOS(targetId=targetId, buildDir=buildDir)

    cp(os.path.join(buildDir,'FreeRTOS.elf'), getSetting('osImageElf',targetId=targetId))
    return



@decorate.debugWrap
def getCyberphysAppDir(app):
    return os.path.join(getSetting('repoDir'),'build','cyberphys', app)
