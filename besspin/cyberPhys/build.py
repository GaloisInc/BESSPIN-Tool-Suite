#! /usr/bin/env python3
"""
Building any binaries or images for cyberPhys
"""

from besspin.base.utils.misc import *
import besspin.target.build
from besspin.fett.build import cpFilesToBuildDir, getBinDir, buildDirPathTuple
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
    cpFilesToBuildDir(infotainmentBinDir, pattern="infotainment_server.elf", targetId=targetId)
    tarFiles = ["infotainment_server.elf"]

    infotainmentAppDir = getCyberphysAppDir('infotainment-server')
    runtimeFilesDir = os.path.join(infotainmentAppDir, osImage)
    if osImage == 'debian':
        cpFilesToBuildDir(runtimeFilesDir, pattern="infotainment-server.service", targetId=targetId)
        tarFiles += ["infotainment-server.service"]
        # Add the script to kill any service listening on port 5002
        cpFilesToBuildDir(runtimeFilesDir, pattern="kill_listeners.sh", targetId=targetId)
        tarFiles += ["kill_listeners.sh"]
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
    tarFiles = copyOtaUpdateserverFiles(tarName,targetId=targetId)
    #Create the tarball here to be sent to target
    tar (tarName, tarFiles)

@decorate.debugWrap
@decorate.timeWrap
def buildInfotainmentServer(tarName, targetId=None):
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

    # Custom image?
    if isEnabled('useCustomOsImage',targetId=targetId):
        targetInfo = f"<target{targetId}>: " if (targetId) else ''
        warnAndLog (f"{targetInfo} Warning, using a custom image")
        imgPath = getSetting('pathToCustomOsImage',targetId=targetId)
        logging.debug(f"{targetInfo} custom image path: {imgPath}")
        cp(imgPath, getSetting('osImageElf',targetId=targetId))
    else:
        # define some paths
        osImageAsm = os.path.join(getSetting('osImagesDir',targetId=targetId),"FreeRTOS.asm")
        setSetting('osImageAsm',osImageAsm,targetId=targetId)

        #build it
        besspin.target.build.freeRTOSBuildChecks(targetId=targetId,freertosFork="classic")
        buildDir = getSetting('buildDir',targetId=targetId)

        #copy the C files, .mk files, and any directory
        copyDir(os.path.join(getSetting('repoDir'),'besspin','cyberPhys','srcFreeRTOS'),buildDir,copyContents=True)
        copyDir(os.path.join(getSetting('repoDir'),'besspin','cyberPhys','canlib'),buildDir,copyContents=True)

        canPort = getSetting('cyberPhysCanbusPort')
        configHfile = ftOpenFile (os.path.join(buildDir,'besspinFreeRTOSConfig.h'),'a')
        try:
            configHfile.write(f"#define CAN_PORT ({canPort}UL)\n")
        except Exception as exc:
            logAndExit(f"Failed to populate <besspinFreeRTOSConfig.h>.",exc=exc,exitCode=EXIT.Dev_Bug)
        configHfile.close()

        configHfile = ftOpenFile (os.path.join(buildDir,'besspinFreeRTOSIPConfig.h'),'a')
        try:
            configHfile.write(f"#define ipconfigUSE_DHCP 0\n")
            configHfile.write(f"#define ipconfigHAS_PRINTF 1\n")
            configHfile.write(f"#define ipconfigHAS_DEBUG_PRINTF 0\n")
        except Exception as exc:
            logAndExit(f"Failed to populate <besspinFreeRTOSIPConfig.h>.",exc=exc,exitCode=EXIT.Dev_Bug)
        configHfile.close()

        besspin.target.build.prepareFreeRTOSNetworkParameters(targetId=targetId)
        besspin.target.build.buildFreeRTOS(targetId=targetId, buildDir=buildDir)

        cp(os.path.join(buildDir,'FreeRTOS.elf'), getSetting('osImageElf',targetId=targetId))
    return

@decorate.debugWrap
def getCyberphysAppDir(app):
    return os.path.join(getSetting('repoDir'),'besspin','cyberPhys', app)
