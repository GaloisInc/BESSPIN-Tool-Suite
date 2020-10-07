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
def deploymentTest (target):
    printAndLog("Testing SSH and SCP...", tee=getSetting('appLog'))

    target.switchUser()
    wasAlreadyInSsh = target.isSshConn

    # SSH Test
    if (not wasAlreadyInSsh): #If in an SSH connection already, then there is no need to test
        if (not target.openSshConn(userName=target.userName,timeout=30)):
            target.terminateAndExit(f"Test[user test ssh]:Failed to open ssh conn.", exitCode=EXIT.Run)
    printAndLog("Test SSH passed successfully!", doPrint=False, tee=getSetting('appLog'))

    # SCP Test
    target.sendFile (pathToFile=getSetting('repoDir'),xFile='README.md',timeout=120)
    target.runCommand("rm README.md") # researchers don't need to see that
    printAndLog("Test SCP passed successfully!", doPrint=False, tee=getSetting('appLog'))

    printAndLog("SSH and SCP test OK!", tee=getSetting('appLog'))

    # Return to the previous state
    if (not wasAlreadyInSsh):
        target.closeSshConn()
    target.switchUser()    
    
    return