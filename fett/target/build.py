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

    if(isEqSetting('target','aws')):
        logAndExit (f"<target.build.prepareOsImage> is not yet implemented for <aws>.",exitCode=EXIT.Implementation)

    if(isEqSetting('osImage','FreeRTOS')):
        prepareFreeRTOS ()
    elif(isEqSetting('osImage','debian')):
        prepareDebian ()
    elif(isEqSetting('osImage','FreeBSD')):
        prepareFreeBSD ()

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOS():
    # should build FreeRTOS image here (if needed)
    # Check if FreeRTOS mirror is checked out
    logAndExit (f"<target.build.prepareFreeRTOS> is not yet implemented.",exitCode=EXIT.Implementation)

@decorate.debugWrap
@decorate.timeWrap
def prepareDebian():
    # copy the crngOnDebian.riscv
    cp (getSetting('addEntropyDebianPath'),getSetting('buildDir'))
    setupUnixImages('debian')

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeBSD():
    setupUnixImages('FreeBSD')

@decorate.debugWrap
def setupUnixImages(osImage):
    osImageElf = os.path.join(getSetting('osImagesDir'),f"{osImage}.elf")
    setSetting('osImageElf',osImageElf)
    if (isEnabled('useCustomOsImage')):
        cp (getSetting('pathToCustomOsImage'),osImageElf)
    else: #use nix images
        nixImage = getSettingDict('nixEnv',[osImage,getSetting('target')])
        if (nixImage in os.environ):
            cp(os.environ[nixImage],osImageElf)
        else:
            logAndExit (f"<${nixImage}> not found in the nix path.",exitCode=EXIT.Environment)
    if (isEqSetting('elfLoader','netboot')):
        netbootElf = os.path.join(getSetting('osImagesDir'),f"netboot.elf")
        setSetting('netbootElf',netbootElf)
        netbootImage = getSettingDict('nixEnv','netboot')
        if (netbootImage in os.environ):
            cp(os.environ[netbootImage],netbootElf)
        else:
            logAndExit (f"<${netbootImage}> not found in the nix path.",exitCode=EXIT.Environment)
    logging.info("Unix images imported successfully.")

