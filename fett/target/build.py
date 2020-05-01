#! /usr/bin/env python3
""" 
Building OS images any other needed files
"""

import os
from fett.base.utils.misc import *

@decorate.debugWrap
def prepareOsImage ():
    # create the osImages directory
    osImagesDir = os.path.join(getSetting('workDir'),'osImages')
    mkdir(osImagesDir,addToSettings='osImagesDir')

    osImageElf = os.path.join(getSetting('osImagesDir'),f"{getSetting('osImage')}.elf")
    setSetting('osImageElf',osImageElf)

    if(isEqSetting('target','aws')):
        logAndExit (f"<target.build.prepareOsImage> is not yet implemented for <aws>.",exitCode=EXIT.Implementation)

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
def prepareFreeRTOS():
    """
    We have three different sources of FreeRTOS here:
    1. If 'buildApps' is enabled --> Compile it.
    2. If 'buildApps' is disabled && useCustomImage is disabled --> Nix
    3. If 'buildApps' is disabled && useCustomImage is enabled --> customImage
    """

    #Console mode on FreeRTOS?
    if (isEqSetting('osImage','FreeRTOS') and isEnabled('openConsole')):
        warnAndLog (f"Unable to <openConsole> on FreeRTOS. This will be switched off.", doPrint=False)
        setSetting('openConsole',False)
    #Netboot on FreeRTOS?
    if (isEqSetting('osImage','FreeRTOS') and isEqSetting('elfLoader','netboot')):
        warnAndLog (f"Netboot cannot load FreeRTOS image. Falling to JTAG.", doPrint=False)
        setSetting('elfLoader','JTAG')

    if (not isEnabled('buildApps')): #just fetch the image
        importImage()
    else: #build it
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
        if ((not isEqSetting('cross-compiler','Clang')) and isEqSetting('linker','LLD')):
            warnAndLog (f"Linking using <{getSetting('linker')}> while cross-compiling with <{getSetting('cross-compiler')} is not supported. Linking using <GCC> instead.>.")
            setSetting('linker','GCC')

        if (isEqSetting('cross-compiler','Clang')):
            logAndExit(f"<Clang> is not yet supported for FreeRTOS.",exitCode=EXIT.Implementation)

        #copy the C files, .mk files, and any directory
        copyDir(os.path.join(getSetting('repoDir'),'fett','target','srcFreeRTOS'),getSetting('buildDir'),copyContents=True)

        #Include the relevant user configuration parameters
        #This is a list of tuples: (settingName,macroName)
        listConfigParams = [('appTimeout','APP_TIMEOUT')]
        configHfile = ftOpenFile (os.path.join(getSetting('buildDir'),'fettUserConfig.h'),'a')
        for xSetting,xMacro in listConfigParams:
            configHfile.write(f"#define {xMacro} {getSetting(xSetting)}\n")
        configHfile.close()

        #Cleaning all ".o" and ".elf" files in site
        cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.o')
        cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.elf')

        #Compile
        printAndLog (f"Cross-compiling...")
        envVars = []
        envVars.append(f"XLEN={getSetting('xlen')}")
        envVars.append(f"USE_CLANG={int(isEqSetting('cross-compiler','Clang'))}")
        envVars.append(f"PROG=main_fett")
        envVars.append(f"INC_FETT_APPS={getSetting('buildDir')}")
        logging.debug(f"going to make using {envVars}")
        make (envVars,getSetting('FreeRTOSprojDir'))

        #check if the elf file was created
        builtElf = os.path.join(getSetting('FreeRTOSprojDir'),'main_fett.elf')
        if (not os.path.isfile(builtElf)):
            logAndExit(f"<make> executed without errors, but cannot fine <{builtElf}>.",exitCode=EXIT.Run)
        cp(builtElf,getSetting('osImageElf'))
        printAndLog(f"Files cross-compiled successfully.")

        #Cleaning all ".o" files post run
        cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.o')
        cleanDirectory (getSetting('FreeRTOSforkDir'),endsWith='.elf')
    return

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
def importImage():
    if (isEnabled('useCustomOsImage')):
        cp (getSetting('pathToCustomOsImage'),getSetting('osImageElf'))
    else: #use nix images
        nixImage = getSettingDict('nixEnv',[getSetting('osImage'),getSetting('target')])
        if (nixImage in os.environ):
            cp(os.environ[nixImage],getSetting('osImageElf'))
        else:
            logAndExit (f"<${nixImage}> not found in the nix path.",exitCode=EXIT.Environment)
    if (isEqSetting('elfLoader','netboot') and (getSetting('osImage') in ['debian', 'FreeBSD', 'busybox'])):
        netbootElf = os.path.join(getSetting('osImagesDir'),f"netboot.elf")
        setSetting('netbootElf',netbootElf)
        netbootImage = getSettingDict('nixEnv','netboot')
        if (netbootImage in os.environ):
            cp(os.environ[netbootImage],netbootElf)
        else:
            logAndExit (f"<${netbootImage}> not found in the nix path.",exitCode=EXIT.Environment)
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


