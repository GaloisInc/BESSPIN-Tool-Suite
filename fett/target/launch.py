#! /usr/bin/env python3
""" 
The main file to start launching fett
"""

from fett.base.utils.misc import *
from fett.target.build import prepareOsImage
from fett.apps.build import buildApps
import sys

""" This is the FETT entry function """
@decorate.debugWrap
@decorate.timeWrap
def startFett ():
    # ------- Global/Misc sanity checks
    #check we're in nix
    if (sys.executable.split('/')[1] != 'nix'):
        logAndExit(f"Please run within a nix shell. [Run <nix-shell> in target-fett directory].")

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

        if (isEnabled('webserver') and isEnabled('database')):
            warnAndLog (f"<webserver> and <database> are mutually exclusive. <webserver> is going to be ignored.")
            setSetting('webserver',False) 
    
    buildApps ()

    # config sanity checks for fetching osImage


""" This is the loading/booting function """
@decorate.debugWrap
@decorate.timeWrap
def launchFett ():
    pass

""" This is the teardown function """
@decorate.debugWrap
def endFett ():
    pass

