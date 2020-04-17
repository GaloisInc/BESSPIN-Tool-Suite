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
import sys

""" This is the FETT entry function """
@decorate.debugWrap
@decorate.timeWrap
def startFett ():
    # ------- Global/Misc sanity checks
    #check we're in nix
    if (sys.executable.split('/')[1] != 'nix'):
        logAndExit(f"Please run within a nix shell. [Run <nix-shell> in target-fett directory].",exitCode=EXIT.Environment)

    #Processor and osImage combinations
    combinationsDict = getSetting('procOsCombinations')
    if (getSetting('processor') not in getSettingDict('procOsCombinations',[getSetting('osImage')])):
        logAndExit(f"{getSetting('osImage')} is not compatible with <{getSetting('processor')}>.",exitCode=EXIT.Configuration)

    #qemu on FreeRTOS?
    if (isEqSetting('osImage','FreeRTOS') and isEqSetting('target','qemu')):
        logAndExit (f"Qemu is not implemented for FreeRTOS.",exitCode=EXIT.Implementation)

    #Console mode on FreeRTOS?
    if (isEqSetting('osImage','FreeRTOS') and isEnabled('openConsole')):
        warnAndLog (f"Unable to <openConsole> on FreeRTOS. This will be switched off.")
        setSetting('openConsole',False)

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
    if (isEqSetting('osImage','FreeRTOS')):
        if (not isEnabled('https') and not isEnabled('ota')):
            warnAndLog (f"All FreeRTOS apps are switched off.")
            exitFett (EXIT.Nothing_to_do)
        if (isEnabled('https') and isEnabled('ota')):
            warnAndLog (f"<https> and <ota> are mutually exclusive. <ota> is going to be ignored.")
            setSetting('ota',False)
    elif (isEqSetting('osImage','FreeBSD') or isEqSetting('osImage','debian')):
        if (not isEnabled('webserver') and not isEnabled('database')):
            if (not isEnabled('openConsole')):
                warnAndLog (f"All {getSetting('osImage')} apps are switched off, and <openConsole> is disabled.")
                exitFett (EXIT.Nothing_to_do)
            else:
                warnAndLog (f"All {getSetting('osImage')} apps are switched off. This is a console only mode.")

        if (isEnabled('webserver') and isEnabled('database')):
            warnAndLog (f"<webserver> and <database> are mutually exclusive. <webserver> is going to be ignored.")
            setSetting('webserver',False) 
    
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
    pass

""" This is the teardown function """
@decorate.debugWrap
def endFett ():
    pass

