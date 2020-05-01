#! /usr/bin/env python3
""" 
The main file to start launching fett
"""

from fett.base.utils.misc import *
from fett.target.build import prepareOsImage
from fett.target import common
from fett.target import fpga
from fett.target import qemu
#from fett.target import aws
from fett.apps.build import buildApps
import sys, os
from importlib.machinery import SourceFileLoader

""" This is the FETT entry function """
@decorate.debugWrap
@decorate.timeWrap
def startFett ():
    # ------- Global/Misc sanity checks

    #Processor and osImage combinations
    combinationsDict = getSetting('procOsCombinations')
    if (getSetting('processor') not in getSettingDict('procOsCombinations',[getSetting('osImage')])):
        logAndExit(f"{getSetting('osImage')} is not compatible with <{getSetting('processor')}>.",exitCode=EXIT.Configuration)

    #qemu on FreeRTOS and Busybox
    if ((getSetting('osImage') in ['FreeRTOS','busybox']) and isEqSetting('target','qemu')):
        logAndExit (f"Qemu is not implemented for {getSetting('osImage')}.",exitCode=EXIT.Implementation)

    # prepare the environment
    prepareEnv()

    # launch fett
    launchFett()

    # tear down
    endFett () 


""" This is the prepare function before launch (binaries, network,) """ 
@decorate.debugWrap
def prepareEnv ():
    printAndLog (f"Preparing the environment...")
    # cannot buildApps on aws
    if (isEnabled('buildApps') and isEqSetting('target','aws')):
        warnAndLog (f"Unable to <buildApps> on <aws>. This will be switched off.")
        setSetting('buildApps',False)

    # config sanity checks for building apps
    setSetting('runApp',True)
    if (isEqSetting('osImage','FreeRTOS')):
        setSetting('webserver',False) 
        setSetting('database',False) 
    elif (isEqSetting('osImage','FreeBSD') or isEqSetting('osImage','debian')):
        if (not isEnabled('webserver') and not isEnabled('database')):
            if (not isEnabled('openConsole')):
                warnAndLog (f"All {getSetting('osImage')} apps are switched off, and <openConsole> is disabled.")
                exitFett (EXIT.Nothing_to_do)
            else:
                warnAndLog (f"All {getSetting('osImage')} apps are switched off. This is a console only mode.")
                setSetting('runApp',False)

        if (isEnabled('webserver') and isEnabled('database')):
            warnAndLog (f"<webserver> and <database> are mutually exclusive. <webserver> is going to be ignored.")
            setSetting('webserver',False) 
    elif (isEqSetting('osImage','busybox')):
        printAndLog(f"<busybox> is only used for smoke testing the target/network. No applications are supported.")
        setSetting('runApp',False)
        setSetting('webserver',False) 
        setSetting('database',False) 
    else:
        logAndExit (f"<launch.prepareEnv> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)
    
    buildApps ()

    prepareOsImage ()

    if (isEqSetting('target','fpga')):
        fpga.programBifile()
        fpga.resetEthAdaptor()
    printAndLog (f"Environment is ready.")

""" This is the loading/booting function """
@decorate.debugWrap
@decorate.timeWrap
def launchFett ():
    printAndLog (f"Launching FETT...")
    xTarget = getClassType()()
    xTarget.start()
    if (isEnabled('isUnix')):
        xTarget.changeRootPassword()
        xTarget.createUser()
    if (isEnabled('runApp')):
        xTarget.runApp(sendFiles=isEnabled('sendTarballToTarget'))
    xTarget.shutdown()


""" This is the teardown function """
@decorate.debugWrap
def endFett ():
    pass

""" This decides the classes hierarchy """
@decorate.debugWrap
def getClassType():
    if (isEqSetting('target','aws')):
        logAndExit (f"<launch.getClassType> is not yet implemented for <aws>.",exitCode=EXIT.Implementation)
    elif (isEqSetting('target','qemu')):
        return qemu.qemuTarget
    elif (isEqSetting('target','fpga')):
        gfeTestingScripts = getSettingDict('nixEnv',['gfeTestingScripts'])
        if (gfeTestingScripts not in os.environ):
            logAndExit (f"<${gfeTestingScripts}> not found in the nix path.",exitCode=EXIT.Environment)
        try:
            sys.path.append(os.environ[gfeTestingScripts])
            from test_gfe_unittest import TestLinux, TestFreeRTOS
        except Exception as exc:
            logAndExit (f"Failed to load <test_gfe_unittest> from <${gfeTestingScripts}>.",exc=exc,exitCode=EXIT.Environment)
        if (isEqSetting('xlen',32)):
            return type('classFpgaTarget',(fpga.fpgaTarget,TestFreeRTOS),dict())
        elif(isEqSetting('xlen',64)):
            return type('classFpgaTarget',(fpga.fpgaTarget,TestLinux),dict())
        else:
            logAndExit (f"Invalid <xlen={getSetting('xlen')}> value.",exitCode=EXIT.Dev_Bug)

    else:
        logAndExit (f"<launch.getClassType> is not implemented for <{getSetting('target')}>.",exitCode=EXIT.Dev_Bug)


