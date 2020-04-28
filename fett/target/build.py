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
        # Check if FreeRTOS mirror is checked out
        if (len(os.listdir(getSetting('FreeRTOSfork'))) == 0):
            logAndExit (f"The FreeRTOS fork at <{getSetting('FreeRTOSfork')}> seems not checked-out properly. Please use <git submodule update>.",exitCode=EXIT.Environment)

        #cross-compiling sanity checks
        if ((not isEqSetting('cross-compiler','Clang')) and isEqSetting('linker','LLD')):
            warnAndLog (f"Linking using <{getSetting('linker')}> while cross-compiling with <{getSetting('cross-compiler')} is not supported. Linking using <GCC> instead.>.")
            setSetting('linker','GCC')

        if (isEqSetting('cross-compiler','Clang')):
            logAndExit(f"<Clang> is not yet supported for FreeRTOS.",exitCode=EXIT.Implementation)



        logAndExit (f"Building FreeRTOS kernel is not yet fully implemented.",exitCode=EXIT.Implementation)

@decorate.debugWrap
@decorate.timeWrap
def prepareDebian():
    # copy the crngOnDebian.riscv
    cp (getSetting('addEntropyDebianPath'),getSetting('buildDir'))
    importImage('debian')

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

