#! /usr/bin/env python3
"""
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def install(target):
    return

@decorate.debugWrap
@decorate.timeWrap
def deploy (target):
    printAndLog ("Deployment successful. Target is ready.",tee=getSetting('appLog'))

    #Here we should send a message to the portal

    #Here we should wait for a termination signal from the portal

    printAndLog("Termination signal received. Preparing to exit...",tee=getSetting('appLog'))
    return

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest (target):
    extensiveTest (target)
    return

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest (target):
    printAndLog("Testing SSH and SCP...", tee=getSetting('appLog'))

    target.switchUser()
    wasAlreadyInSsh = target.isSshConn
    
    # SSH Test
    if (not wasAlreadyInSsh): #If in an SSH connection already, then there is no need to test
        if (not target.openSshConn(userName=target.userName)):
            target.shutdownAndExit(f"Test[user test ssh]:Failed to open ssh conn.", exitCode=EXIT.Run)
    printAndLog("Test SSH passed successfully!", doPrint=False, tee=getSetting('appLog'))

    # SCP Test
    target.sendFile (pathToFile=getSetting('repoDir'),xFile='README.md',timeout=120)
    printAndLog("Test SCP passed successfully!", doPrint=False, tee=getSetting('appLog'))

    printAndLog("SSH and SCP test OK!", tee=getSetting('appLog'))

    # Return to the previous state
    if (not wasAlreadyInSsh):
        target.closeSshConn()
    target.switchUser()    
    
    return