#! /usr/bin/env python3
"""
Building OS images any other needed files
"""

import os, re
from fett.base.utils.misc import *

@decorate.debugWrap
def prepareOsImage ():
    # create the osImages directory
    osImagesDir = os.path.join(getSetting('workDir'),'osImages')
    mkdir(osImagesDir,addToSettings='osImagesDir')

    # setup os image and extra images
    if isEqSetting('binarySource', 'SRI-Cambridge'):
        osImageElf = os.path.join(getSetting('osImagesDir'),f"bbl-cheri.elf")
        setSetting('osImageElf',osImageElf)
        imageVariant = '-purecap' if (isEqSetting('sourceVariant','purecap')) else ''
        osImageExtraElf = os.path.join(getSetting('osImagesDir'),f"kernel-cheri{imageVariant}.elf")
        setSetting('osImageExtraElf', osImageExtraElf)
    else:
        osImageElf = os.path.join(getSetting('osImagesDir'),f"{getSetting('osImage')}.elf")
        setSetting('osImageElf',osImageElf)
        setSetting('osImageExtraElf', None)


    if(isEqSetting('osImage','FreeRTOS')):
        prepareFreeRTOS ()
    elif(isEqSetting('osImage','debian')):
        prepareDebian ()
    elif(isEqSetting('osImage','FreeBSD')):
        prepareFreeBSD ()
    elif(isEqSetting('osImage','busybox')):
        prepareBusybox ()
    else:
        logAndExit (f"<target.prepareOsImage> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)


@decorate.debugWrap
@decorate.timeWrap
def freeRTOSBuildChecks():
    """
    Check FreeRTOS build parameters and set settings appropriately
    """
    # Check if FreeRTOS mirror is checked out properly
    forkDir = os.path.join(getSetting('repoDir'),getSetting('FreeRTOSforkName'))
    setSetting('FreeRTOSforkDir',forkDir)
    if (not os.path.isdir(getSetting('FreeRTOSforkDir'))):
        logAndExit (f"Failed to find the FreeRTOS fork at <{getSetting('FreeRTOSforkDir')}>. Please use <git submodule update --init>.",exitCode=EXIT.Environment)
    if (len(os.listdir(getSetting('FreeRTOSforkDir'))) == 0):
        logAndExit (f"The FreeRTOS fork at <{getSetting('FreeRTOSforkDir')}> is empty. Please use <git submodule update>.",exitCode=EXIT.Environment)

    projDir = os.path.join(getSetting('FreeRTOSforkDir'),getSetting('FreeRTOSprojName'))
    setSetting('FreeRTOSprojDir',projDir)
    if (not os.path.isdir(getSetting('FreeRTOSprojDir'))):
        logAndExit (f"Failed to fine the FreeRTOS project at <{getSetting('FreeRTOSprojDir')}>.",exitCode=EXIT.Environment)

    #cross-compiling sanity checks
    if (isEqSetting('cross-compiler','GCC') and (not isEqSetting('linker','GCC'))):
        warnAndLog (f"Linking using <{getSetting('linker')}> while cross-compiling with <GCC> is not supported. Linking using <GCC> instead.")
        setSetting('linker','GCC')
    if (isEqSetting('cross-compiler','Clang') and (not isEqSetting('linker','LLD'))):
        warnAndLog (f"Linking using <{getSetting('linker')}> while cross-compiling with <Clang> is not supported. Linking using <LLD> instead.")
        setSetting('linker','LLD')

    # C++ SD Arduino library causing issues with Clang
    if (isEqSetting('cross-compiler','Clang') and (isEqSetting('target','fpga'))):
        logAndExit(f"Building FreeRTOS using Clang/LLD is not yet implemented for target <fpga>.",exitCode=EXIT.Implementation)

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOSNetworkParameters():
    #Include the network configuration parameters
    #This is a list of tuples: (settingName, macroNameBase, int/hex)
    thisTarget = getSetting('target')
    listConfigIpParams = [(f"{thisTarget}MacAddrTarget",'configMAC_ADDR', hex), (f"{thisTarget}IpTarget",'configIP_ADDR', int),
                          (f"{thisTarget}IpHost",'configGATEWAY_ADDR', int), (f"{thisTarget}NetMaskTarget",'configNET_MASK', int)]

    def mapVal(val,xType):
        if (xType==int):
            return int(val)
        elif (xType==hex):
            return "0x{:02X}".format(int(val,16))

    configIpHfile = ftOpenFile (os.path.join(getSetting('buildDir'),'fettFreeRTOSIPConfig.h'),'a')
    for xSetting,xMacro,xType in listConfigIpParams:
        for iPart,xPart in enumerate(re.split(r'[\.\:]',getSetting(xSetting))):
            try:
                configIpHfile.write(f"#define {xMacro}{iPart} {mapVal(xPart,xType)}\n")
            except Exception as exc:
                logAndExit(f"Failed to populate <fettFreeRTOSIPConfig.h>.",exc=exc,exitCode=EXIT.Dev_Bug)
    configIpHfile.close()

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOS():
    """
    We have three different sources of FreeRTOS here:
    1. If 'buildApps' is enabled --> Compile it.
    2. If 'buildApps' is disabled && useCustomImage is disabled --> Nix
    3. If 'buildApps' is disabled && useCustomImage is enabled --> customImage
    """

    #Netboot on FreeRTOS?
    if (isEqSetting('osImage','FreeRTOS') and isEqSetting('elfLoader','netboot')):
        warnAndLog (f"Netboot cannot load FreeRTOS image. Falling to JTAG.", doPrint=False)
        setSetting('elfLoader','JTAG')

    # define some paths
    osImageAsm = os.path.join(getSetting('osImagesDir'),f"{getSetting('osImage')}.asm")
    setSetting('osImageAsm',osImageAsm)

    if (not isEnabled('buildApps')): #just fetch the image
        importImage()
    else: #build it
        freeRTOSBuildChecks()

        #copy the C files, .mk files, and any directory
        copyDir(os.path.join(getSetting('repoDir'),'fett','target','srcFreeRTOS'),getSetting('buildDir'),copyContents=True)

        #Include the relevant user configuration parameters
        #This is a list of tuples: (settingName,macroName)
        listConfigParams = [('HTTPPortTarget','HTTP_PORT'),
                            ('TFTPPortTarget','TFTP_PORT'),
                            ('debugMode','FETT_DEBUG'),
                            ('OTAMaxSignedPayloadSize','OTA_MAX_SIGNED_PAYLOAD_SIZE')]

        configHfile = ftOpenFile (os.path.join(getSetting('buildDir'),'fettUserConfig.h'),'a')
        for xSetting,xMacro in listConfigParams:
            try:
                intVal = int(getSetting(xSetting))
            except Exception as exc:
                logAndExit(f"Invalid type in populating <fettUserConfig.h>.",exc=exc,exitCode=EXIT.Dev_Bug)
            configHfile.write(f"#define {xMacro} {intVal}\n")
        #Write the ota filename too (not list as it is unique)
        configHfile.write(f"#define OTA_FILENAME \"{getSettingDict('freertosAssets',['otaHtml'])}\"\n")
        #Write the bianry source for team specific codes
        configHfile.write(f"#define BIN_SOURCE_{getSetting('binarySource').replace('-','_')}\n")
        #Translate the mode to one char: T or D
        configHfile.write(f"#define FETT_MODE \'{getSetting('mode')[0].upper()}\'\n")
        configHfile.close()

        prepareFreeRTOSNetworkParameters()
        buildFreeRTOS()
    return


def buildFreeRTOS(doPrint=True):
    #Cleaning all ".o" and ".elf" files in site
    cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.o')
    cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.elf')

    #Compile
    printAndLog (f"Cross-compiling...",doPrint=doPrint)
    envVars = []
    envVars.append(f"XLEN={getSetting('xlen')}")
    envVars.append(f"USE_CLANG={'yes' if (isEqSetting('cross-compiler','Clang')) else 'no'}")
    if (isEqSetting('cross-compiler','Clang')):
        # check that the sysroot env variable exists:
        sysRootEnv = getSettingDict('nixEnv',['FreeRTOS', 'clang-sysroot'])
        if (sysRootEnv not in os.environ):
            logAndExit (f"<${sysRootEnv}> not found in the nix path.",exitCode=EXIT.Environment)
        envVars.append(f"SYSROOT_DIR={os.environ[sysRootEnv]}")
    envVars.append(f"PROG=main_fett")
    envVars.append(f"INC_FETT_APPS={getSetting('buildDir')}")
    envVars.append(f"BSP={getSetting('target')}")
    if getSetting('FreeRTOSUseRAMDisk'):
        envVars.append(f"FREERTOS_USE_RAMDISK=1")
    envVars.append(f"RAMDISK_NUM_SECTORS={getSetting('freertosRamdiskNumSectors')}")
    logging.debug(f"going to make using {envVars}")
    make (envVars,getSetting('FreeRTOSprojDir'))

    #check if the elf file was created
    builtElf = os.path.join(getSetting('FreeRTOSprojDir'),'main_fett.elf')
    builtAsm = os.path.join(getSetting('FreeRTOSprojDir'),'main_fett.asm')
    if (not os.path.isfile(builtElf)):
        logAndExit(f"<make> executed without errors, but cannot find <{builtElf}>.",exitCode=EXIT.Run)
    cp(builtElf,getSetting('osImageElf'))
    if (not os.path.isfile(builtAsm)):
        logAndExit(f"<make> executed without errors, but cannot find <{builtAsm}>.",exitCode=EXIT.Run)
    cp(builtAsm,getSetting('osImageAsm'))
    printAndLog(f"Files cross-compiled successfully.",doPrint=doPrint)

    #Cleaning all ".o" files post run
    cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.o')
    cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.elf')

@decorate.debugWrap
@decorate.timeWrap
def prepareDebian():
    # copy the crngOnDebian.riscv
    cp (getSetting('addEntropyDebianPath'),getSetting('buildDir'))
    importImage()

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeBSD():
    importImage()

@decorate.debugWrap
@decorate.timeWrap
def prepareBusybox():
    importImage()

@decorate.debugWrap
def selectImagePaths():
    if isEnabled('useCustomOsImage'):
        return [getSetting('pathToCustomOsImage')]
    else:
        # inconsistency
        if isEqSetting('binarySource', 'SRI-Cambridge'):
            imageType = getSetting('target') if getSetting('target') != 'aws' else 'aws'
        else:
            imageType = getSetting('target') if getSetting('target') != 'aws' else getSetting('pvAWS')
        if getSetting('binarySource') == 'GFE':
            nixImage = getSettingDict('nixEnv',[getSetting('osImage'),imageType])
            if (nixImage in os.environ):
                tempPath = os.path.join(getSetting('workDir'),'tmp')
                mkdir (tempPath)
                tempImagePath = os.path.join(tempPath,os.path.basename(getSetting('osImageElf')))
                cp (os.environ[nixImage], tempImagePath) #to ensure it has the standard tool name
                return [tempImagePath]
            else:
                printAndLog(f"Could not find image for <{getSetting('osImage')}> in nix environment. Falling back to binary repo.", doPrint=False)
        baseDir = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'), 'osImages', imageType)
        if isEqSetting('binarySource', 'SRI-Cambridge'):
            imageVariant = '-purecap' if (isEqSetting('sourceVariant','purecap')) else ''
            imagePaths = [os.path.join(baseDir, f"bbl-cheri.elf"), os.path.join(baseDir, f"kernel-cheri{imageVariant}.elf")]
        else:
            imagePaths = [os.path.join(baseDir, f"{getSetting('osImage')}.elf")]
        return imagePaths

@decorate.debugWrap
def importImage():
    imagePaths = selectImagePaths()
    for ip in imagePaths:
        cp (ip, getSetting('osImagesDir'))
    if not (isEqSetting('target', 'aws')):
        if (isEqSetting('elfLoader','netboot') and (getSetting('osImage') in ['debian', 'FreeBSD', 'busybox'])):
            netbootElf = os.path.join(getSetting('osImagesDir'),f"netboot.elf")
            setSetting('netbootElf',netbootElf)
            netbootImage = getSettingDict('nixEnv','netboot')
            if (netbootImage in os.environ):
                cp(os.environ[netbootImage],netbootElf)
            else:
                logAndExit (f"<${netbootImage}> not found in the nix path.",exitCode=EXIT.Environment)
    else:
        warnAndLog(f"<importImage>: the netboot elfLoader was selected but is ignored as target is aws", doPrint=False)
    logging.info(f"{getSetting('osImage')} image imported successfully.")

@decorate.debugWrap
def cleanDirectory (xDir,endsWith='.o'):
    if ((not xDir) or (not os.path.isdir(xDir))):
        logAndExit(f"cleanDirectory: <{xDir}> is not a valid directory.", exitCode=EXIT.Dev_Bug)

    if (not isinstance(endsWith,str)):
        logAndExit(f"cleanDirectory: <{endsWith}> has to be a string.", exitCode=EXIT.Dev_Bug)

    for xDirName, xDirList, xFilesList in os.walk(xDir):
        for xFile in xFilesList:
            if (xFile.endswith(endsWith)):
                try:
                    os.remove(os.path.join(xDirName,xFile))
                except Exception as exc:
                    logAndExit(f"cleanDirectory: Failed to delete <{xDirName}/{xFile}>.", exitCode=EXIT.Files_and_paths)
