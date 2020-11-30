#! /usr/bin/env python3
"""
Building OS images any other needed files
"""

import os, re, glob, ipaddress
from fett.base.utils.misc import *
import fett.apps.build
import fett.cyberPhys.build

@decorate.debugWrap
def prepareOsImage (targetId=None):
    targetSuffix = f'_{targetId}' if (targetId) else ''
    # create the osImages directory
    osImagesDir = os.path.join(getSetting('workDir'),f'osImages{targetSuffix}')
    mkdir(osImagesDir)
    setSetting('osImagesDir',osImagesDir,targetId=targetId)

    # setup os image and extra images
    if isEqSetting('binarySource', 'SRI-Cambridge',targetId=targetId):
        osImageElf = os.path.join(osImagesDir,f"bbl-cheri.elf")
        setSetting('osImageElf',osImageElf,targetId=targetId)
        imageVariantSuffix = '' if (isEqSetting('sourceVariant','default',targetId=targetId)) else f"-{getSetting('sourceVariant',targetId=targetId)}"
        setSetting('SRI-Cambridge-imageVariantSuffix',imageVariantSuffix,targetId=targetId)
        osImageExtraElf = os.path.join(osImagesDir,f"kernel-cheri{imageVariantSuffix}.elf")
        setSetting('osImageExtraElf', osImageExtraElf, targetId=targetId)
    else:
        osImageElf = os.path.join(osImagesDir,f"{getSetting('osImage',targetId=targetId)}.elf")
        setSetting('osImageElf',osImageElf,targetId=targetId)
        setSetting('osImageExtraElf', None,targetId=targetId)


    if(isEqSetting('osImage','FreeRTOS',targetId=targetId)):
        if (getSetting('mode') in ['test', 'production']):
            fett.apps.build.prepareFreeRTOS()
        elif (isEqSetting('mode','cyberPhys')):
            fett.cyberPhys.build.prepareFreeRTOS(targetId=targetId)
    elif(isEqSetting('osImage','debian',targetId=targetId)):
        prepareDebian(targetId=targetId)
    elif(isEqSetting('osImage','FreeBSD',targetId=targetId)):
        prepareFreeBSD(targetId=targetId)
    elif(isEqSetting('osImage','busybox',targetId=targetId)):
        prepareBusybox(targetId=targetId)
    else:
        logAndExit (f"<target.prepareOsImage> is not implemented for <{getSetting('osImage',targetId=targetId)}> "
            f"in <{getSetting('mode')}> mode.",exitCode=EXIT.Dev_Bug)


@decorate.debugWrap
@decorate.timeWrap
def freeRTOSBuildChecks(targetId=None):
    """
    Check FreeRTOS build parameters and set settings appropriately
    """
    with getSetting('FreeRTOSLock'):
        # Check if FreeRTOS mirror is checked out properly
        forkDir = os.path.join(getSetting('repoDir'),getSetting('FreeRTOSforkName'))
        setSetting('FreeRTOSforkDir',forkDir)
        if (not os.path.isdir(getSetting('FreeRTOSforkDir'))):
            logAndExit (f"Failed to find the FreeRTOS fork at <{getSetting('FreeRTOSforkDir')}>. Please use <git submodule update --init>.",exitCode=EXIT.Environment)
        if (len(os.listdir(getSetting('FreeRTOSforkDir'))) == 0):
            logAndExit (f"The FreeRTOS fork at <{getSetting('FreeRTOSforkDir')}> is empty. Please use <git submodule update>.",exitCode=EXIT.Environment)

        if isEqSetting('target', 'qemu', targetId=targetId):
            projDir = os.path.join(getSetting('FreeRTOSforkDir'),
                                   getSetting('FreeRTOSprojNameQemu'))
        else:
            projDir = os.path.join(getSetting('FreeRTOSforkDir'),
                                   getSetting('FreeRTOSprojNameNonQemu'))
        setSetting('FreeRTOSprojDir',projDir,targetId=targetId)
        if (not os.path.isdir(getSetting('FreeRTOSprojDir',targetId=targetId))):
            logAndExit (f"Failed to find the FreeRTOS project at <{getSetting('FreeRTOSprojDir',targetId=targetId)}>.",exitCode=EXIT.Environment)

        #cross-compiling sanity checks
        if (isEqSetting('binarySource','Michigan',targetId=targetId) and
            not isEqSetting('cross-compiler', 'Clang')):
            warnAndLog(f"Cross compiling with <{getSetting('cross-compiler')}> "
                       f"while using binary source <{getSetting('binarySource',targetId=targetId)}> "
                       "is not supported.  Cross compiling with <Clang> and "
                       "linking with <LLD> instead.")
            setSetting('cross-compiler', 'Clang')
            setSetting('linker','LLD')
        if (isEqSetting('cross-compiler','GCC') and (not isEqSetting('linker','GCC'))):
            warnAndLog (f"Linking using <{getSetting('linker')}> while cross-compiling with <GCC> is not supported. Linking using <GCC> instead.")
            setSetting('linker','GCC')
        if (isEqSetting('cross-compiler','Clang') and (not isEqSetting('linker','LLD'))):
            warnAndLog (f"Linking using <{getSetting('linker')}> while cross-compiling with <Clang> is not supported. Linking using <LLD> instead.")
            setSetting('linker','LLD')

        # FatFs
        if (isEqSetting('mode','test')): #targeId is None for test mode (the only mode that uses SDCard+buildApps)
            if (isEqSetting('freertosFatFs','default')):
                if (isEqSetting('target','awsf1')):
                    setSetting('freertosFatFs','dosblk')
                elif (isEqSetting('target','vcu118')):
                    setSetting('freertosFatFs','ramdisk')
            elif (isEqSetting('freertosFatFs','dosblk') and (not isEqSetting('target','awsf1'))):
                logAndExit(f"FatFs using <dosblk> is only available on <awsf1> target.",exitCode=EXIT.configuration)
            elif (isEqSetting('freertosFatFs','sdcard') and (not isEqSetting('target','vcu118'))):
                logAndExit(f"FatFs using <sdcard> is only available on <vcu118> target.",exitCode=EXIT.configuration)
            if isEqSetting('freertosFatFs','sdcard'):
                # C++ SD Arduino library causing issues with Clang
                if isEqSetting('cross-compiler','Clang'):
                    logAndExit(f"Compiling the SDcard library using Clang/LLD is not yet implemented.",exitCode=EXIT.Implementation)
                warnAndLog("FatFs is configured to use <sdcard>. This run will only succeed if an SD card is available to the board.")

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOSNetworkParameters(targetId=None, buildDir=None):
    #Include the network configuration parameters
    if (buildDir is None):
        buildDir = getSetting('buildDir',targetId=targetId)

    #This is a list of tuples: (settingName, macroNameBase, int/hex)
    thisTarget = getSetting('target',targetId=targetId)
    listConfigIpParams = [(f"{thisTarget}MacAddrTarget",'configMAC_ADDR', hex), (f"{thisTarget}IpTarget",'configIP_ADDR', int),
                          (f"{thisTarget}IpHost",'configGATEWAY_ADDR', int), (f"{thisTarget}NetMaskTarget",'configNET_MASK', int)]

    def mapVal(val,xType):
        if (xType==int):
            return int(val)
        elif (xType==hex):
            return "0x{:02X}".format(int(val,16))

    configIpHfile = ftOpenFile (os.path.join(buildDir,'fettFreeRTOSIPConfig.h'),'a')
    for xSetting,xMacro,xType in listConfigIpParams:
        if (doesSettingExist(xSetting)):
            settingVal = getSetting(xSetting)
        elif (xMacro=='configIP_ADDR'): #special treatment to accommodate for many-targets
            settingVal = getTargetIp(targetId=targetId)
        else:
            logAndExit(f"prepareFreeRTOSNetworkParameters: Cannot find setting <{xSetting}>",exitCode=EXIT.Dev_Bug)
            
        for iPart,xPart in enumerate(re.split(r'[\.\:]',settingVal)):
            try:
                configIpHfile.write(f"#define {xMacro}{iPart} {mapVal(xPart,xType)}\n")
            except Exception as exc:
                logAndExit(f"Failed to populate <fettFreeRTOSIPConfig.h>.",exc=exc,exitCode=EXIT.Dev_Bug)
    configIpHfile.close()

@decorate.debugWrap
@decorate.timeWrap
def getTargetIp(targetId=None):
    thisTarget = getSetting('target',targetId=targetId)
    if (thisTarget=='vcu118'): #use hostIP + targetId
        ipInc = 1 if (targetId is None) else targetId
        ipTarget = str(ipaddress.ip_address(getSetting(f"{thisTarget}IpHost"))+ipInc)
        if ((ipTarget!="10.88.88.2") and 
                (isEqSetting('osImage','FreeBSD',targetId=targetId) and isEqSetting('target','vcu118',targetId=targetId))):
            logAndExit(f"<FreeBSD> on <vcu118> has to have the IP <10.88.88.2>; not <{ipTarget}> [ticket#853].",exitCode=EXIT.Dev_Bug)
        return ipTarget
    else:
        logAndExit(f"<getTargetIp> is not implemented for <{thisTarget}>.",exitCode=EXIT.Implementation)

@decorate.debugWrap
@decorate.timeWrap
def buildFreeRTOS(doPrint=True, extraEnvVars=[], targetId=None, buildDir=None):
    targetInfo = f'<target{targetId}>: ' if (targetId) else ''
    with getSetting('FreeRTOSLock'):
        if (buildDir is None):
            defaultBuildDir = True
            buildDir = getSetting('buildDir',targetId=targetId)
        else:
            defaultBuildDir = False
        #Cleaning all ".o" and ".elf" files in site
        cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.o')
        cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.elf')
        if isEqSetting("target", "qemu",targetId=targetId):
            cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.d')

        #Compile
        printAndLog (f"{targetInfo}Cross-compiling...",doPrint=doPrint)
        envVars = extraEnvVars
        envVars.append(f"XLEN={getSetting('xlen',targetId=targetId)}")
        envVars.append(f"USE_CLANG={'yes' if (isEqSetting('cross-compiler','Clang')) else 'no'}")
        if isEqSetting('target','qemu',targetId=targetId):
            envVars.append(f"PROJ_NAME=main_fett")
        else:
            envVars.append(f"PROG=main_fett")
        envVars.append(f"BSP={getSetting('target',targetId=targetId)}")
        if (isEqSetting('mode','test')):
            envVars.append(f"FATFS={getSetting('freertosFatFs',targetId=targetId).upper()}")
            if isEqSetting('freertosFatFs','ramdisk',targetId=targetId):
                envVars.append(f"RAMDISK_NUM_SECTORS={getSetting('freertosRamdiskNumSectors')}")

        if isEqSetting('binarySource', 'Michigan',targetId=targetId):
            dockerToolchainImage = 'michigan-image:1.0'
            envVars.append("USE_MORPHEUS=yes")

            # Build directory must be mounted at INC_FETT_APPS
            dockerBuildMount = "/root/build"
            envVars.append(f"INC_FETT_APPS={dockerBuildMount}")
            dockerExtraMounts = {buildDir : dockerBuildMount}

            # The `make` function will mount
            # FreeRTOS-10.0.1/FreeRTOS/Demo/RISC-V_Galois_P1 as /root/makeDir on
            # the docker image.  However, the FreeRTOS Makefile references
            # ../Common and ../../Source.  Therefore, FETT must also mount
            # FreeRTOS-10.0.1/FreeRTOS/Demo/Common as /root/Common and
            # FreeRTOS-10.0.1/FreeRTOS/Source as /Source to preserve these relative
            # paths.
            hostCommon = os.path.abspath(os.path.join(getSetting("FreeRTOSprojDir",targetId=targetId),
                                                      os.pardir,
                                                      "Common"))
            dockerExtraMounts[hostCommon] = "/root/Common"
            hostSource = os.path.abspath(os.path.join(getSetting("FreeRTOSprojDir",targetId=targetId),
                                                      os.pardir,
                                                      os.pardir,
                                                      "Source"))
            dockerExtraMounts[hostSource] = "/Source"

            # Do not set SYSROOT_DIR in the Michigan case, despite being built
            # with clang, because SYSROOT_DIR is already set in the docker image
        else:
            dockerToolchainImage = None
            dockerExtraMounts = {}
            envVars.append(f"INC_FETT_APPS={buildDir}")
            if (isEqSetting('cross-compiler','Clang')):
                # check that the sysroot env variable exists:
                sysRootEnv = getSettingDict('nixEnv',['FreeRTOS', 'clang-sysroot'])
                if (sysRootEnv not in os.environ):
                    logAndExit (f"{targetInfo}<${sysRootEnv}> not found in the nix path.",exitCode=EXIT.Environment)
                envVars.append(f"SYSROOT_DIR={os.environ[sysRootEnv]}")

        logging.debug(f"going to make using {envVars}")
        if (isEqSetting('mode','evaluateSecurityTests') and
            isEnabled('useCustomCompiling') and 
            isEnabledDict('customizedCompiling','useCustomMakefile')
            ):
            make (envVars,buildDir,
                  dockerToolchainImage=dockerToolchainImage,
                  dockerExtraMounts=dockerExtraMounts,
                  targetId=targetId, buildDir=buildDir)
        else: 
            # default environment
            make (envVars,getSetting('FreeRTOSprojDir',targetId=targetId),
                  dockerToolchainImage=dockerToolchainImage,
                  dockerExtraMounts=dockerExtraMounts,
                  targetId=targetId, buildDir=buildDir)

        #check if the elf file was created
        if isEqSetting('target', 'qemu' ,targetId=targetId):
            builtElf = os.path.join(getSetting('FreeRTOSprojDir',targetId=targetId),
                                    'build',
                                    f'FreeRTOS-{mainName}.elf')
        else:
            builtElf = os.path.join(getSetting('FreeRTOSprojDir',targetId=targetId),'main_fett.elf')
        if (not os.path.isfile(builtElf)):
            logAndExit(f"{targetInfo}<make> executed without errors, but cannot find <{builtElf}>.",exitCode=EXIT.Run)

        if isEqSetting('binarySource', 'Michigan', targetId=targetId):
            # Encrypt elf file
            argsList = ['docker', 'run', '-it', '--privileged=true',
                        '-v', f'{getSetting("FreeRTOSprojDir",targetId=targetId)}:/root/makeDir',
                        dockerToolchainImage,
                        'bash', '-c', f'elf-parser -e /root/makeDir/main_fett.elf']
            sudoShellCommand(argsList)

        if (defaultBuildDir):
            cp(builtElf,getSetting('osImageElf',targetId=targetId))
        else:
            cp(builtElf,os.path.join(buildDir,'FreeRTOS.elf'))

        if not isEqSetting('target', 'qemu' ,targetId=targetId):
            builtAsm = os.path.join(getSetting('FreeRTOSprojDir',targetId=targetId),'main_fett.asm')
            if (not os.path.isfile(builtAsm)):
                logAndExit(f"{targetInfo}<make> executed without errors, but cannot find <{builtAsm}>.",exitCode=EXIT.Run)
            if (defaultBuildDir):
                cp(builtAsm,getSetting('osImageAsm',targetId=targetId))
            else:
                cp(builtAsm,os.path.join(buildDir,'FreeRTOS.asm'))
        printAndLog(f"{targetInfo}Files cross-compiled successfully.",doPrint=doPrint)

        #Cleaning all ".o" files post run
        cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.o')
        cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.elf')
        if isEqSetting('target', 'qemu' ,targetId=targetId):
            cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.d')

@decorate.debugWrap
@decorate.timeWrap
def prepareDebian(targetId=None):
    # copy the crngOnDebian.riscv
    cp (getSetting('addEntropyDebianPath'),getSetting('buildDir',targetId=targetId))
    importImage(targetId=targetId)

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeBSD(targetId=None):
    importImage(targetId=targetId)

@decorate.debugWrap
@decorate.timeWrap
def prepareBusybox(targetId=None):
    importImage(targetId=targetId)

@decorate.debugWrap
def selectImagePaths(targetId=None):
    if isEnabled('useCustomOsImage',targetId=targetId):
        return [getSetting('pathToCustomOsImage',targetId=targetId)]
    else:
        imageType = getSetting('target',targetId=targetId) if (getSetting('target',targetId=targetId)!='awsf1') else getSetting('pvAWS',targetId=targetId)
        if isEqSetting('binarySource','GFE',targetId=targetId):
            nixImage = getSettingDict('nixEnv',[getSetting('osImage',targetId=targetId),imageType])
            if (nixImage in os.environ):
                tempPath = os.path.join(getSetting('workDir'),f'tmp{targetId}')
                mkdir (tempPath)
                tempImagePath = os.path.join(tempPath,os.path.basename(getSetting('osImageElf',targetId=targetId)))
                cp (os.environ[nixImage], tempImagePath) #to ensure it has the standard tool name
                return [tempImagePath]
            else:
                printAndLog(f"Could not find image for <{getSetting('osImage',targetId=targetId)}> in nix environment. Falling back to binary repo.", doPrint=False)
        baseDir = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource',targetId=targetId), 'osImages', imageType)
        if isEqSetting('binarySource', 'SRI-Cambridge',targetId=targetId):
            imagePaths = [os.path.join(baseDir, f"bbl-cheri.elf"), 
                os.path.join(baseDir, f"kernel-cheri{getSetting('SRI-Cambridge-imageVariantSuffix',targetId=targetId)}.elf")]
        else:
            imagePaths = [os.path.join(baseDir, f"{getSetting('osImage',targetId=targetId)}.elf")]
        return imagePaths

@decorate.debugWrap
def importImage(targetId=None):
    imagePaths = selectImagePaths(targetId=targetId)
    for ip in imagePaths:
        cp (ip, getSetting('osImagesDir',targetId=targetId))
    if (isEqSetting('target', 'vcu118', targetId=targetId)):
        if (isEqSetting('elfLoader','netboot',targetId=targetId) and (getSetting('osImage',targetId=targetId) in ['debian', 'FreeBSD', 'busybox'])):
            if (isEqSetting('procLevel','p3',targetId=targetId)):
                warnAndLog(f"<importImage>: Netboot is currently not supported on P3. Falling back to JTAG.")
                setSetting('elfLoader','JTAG',targetId=targetId)
            else:
                netbootBuildDir = os.path.join(getSetting('osImagesDir',targetId=targetId),'buildNetbootElf')
                netbootElf = os.path.join(netbootBuildDir,f"FreeRTOS.elf")
                setSetting("netbootElf",netbootElf,targetId=targetId)
                mkdir(netbootBuildDir)
                copyDir(os.path.join(getSetting('repoDir'),'fett','target','utils','srcNetboot'),netbootBuildDir,copyContents=True)
                freeRTOSBuildChecks(targetId=targetId)
                prepareFreeRTOSNetworkParameters(targetId=targetId, buildDir=netbootBuildDir)
                #Write the bianry source for team specific codes
                configHfile = ftOpenFile (os.path.join(netbootBuildDir,'fettUserConfig.h'),'a')
                configHfile.write(f"#define BIN_SOURCE_{getSetting('binarySource',targetId=targetId).replace('-','_')}\n")
                configHfile.close()
                buildFreeRTOS(doPrint=False, targetId=targetId, buildDir=netbootBuildDir)
    else:
        warnAndLog(f"<importImage>: the netboot elfLoader was selected but is ignored as target is <{getSetting('target',targetId=targetId)}>", doPrint=False)
    logging.info(f"{getSetting('osImage',targetId=targetId)} image imported successfully.")

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
                    logAndExit(f"cleanDirectory: Failed to delete <{xDirName}/{xFile}>.",exc=exc,exitCode=EXIT.Files_and_paths)

@decorate.debugWrap
@decorate.timeWrap
def crossCompileUnix(directory,extraString=''):
    if (len(glob.glob(os.path.join(directory,"*.c"))) == 0):
        return #there is nothing to compile
    if (isEqSetting('binarySource','SRI-Cambridge')):
        if (not isEqSetting('cross-compiler','Clang')):
            warnAndLog (f"Compiling using <{getSetting('cross-compiler')}> for <{getSetting('binarySource')}> is not supported."
                " Compiling using <Clang> instead.")
            setSetting('cross-compiler','Clang')
        if (not isEqSetting('linker','LLD')):
            warnAndLog (f"Linking using <{getSetting('linker')}> for <{getSetting('binarySource')}> is not supported."
                " Linking using <LLD> instead.")
            setSetting('linker','LLD')

    #cross-compiling sanity checks
    if ((not isEqSetting('cross-compiler','Clang')) and isEqSetting('linker','LLD')):
        warnAndLog (f"Linking using <{getSetting('linker')}> while cross-compiling with <{getSetting('cross-compiler')} is not supported. Linking using <GCC> instead.")
        setSetting('linker','GCC')

    printAndLog (f"Cross-compiling {extraString}...")
    envLinux = []
    osImageCap1 = getSetting('osImage')[0].upper() + getSetting('osImage')[1:]
    envLinux.append(f"OS_IMAGE={osImageCap1}")
    envLinux.append(f"TARGET={getSetting('target').upper()}")
    envLinux.append(f"COMPILER={getSetting('cross-compiler').upper()}")
    envLinux.append(f"LINKER={getSetting('linker').upper()}")
    envLinux.append(f"BIN_SOURCE={getSetting('binarySource').replace('-','_')}")
    envLinux.append(f"SOURCE_VARIANT={getSetting('sourceVariant')}")
    logging.debug(f"going to make using {envLinux}")
    if (isEqSetting('binarySource','SRI-Cambridge')):
        dockerToolchainImage = 'cambridge-toolchain'
    elif (isEqSetting('binarySource','LMCO')):
        dockerToolchainImage = 'galoisinc/besspin:gfe-gcc83'
    else:
        dockerToolchainImage = None
    make (envLinux, directory,dockerToolchainImage=dockerToolchainImage)
    printAndLog(f"Files cross-compiled successfully.")
