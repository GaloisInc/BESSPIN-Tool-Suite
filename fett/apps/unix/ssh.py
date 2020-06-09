#! /usr/bin/env python3
"""
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *
import pexpect

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
    return

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest (target):
    printAndLog("Testing ssh and scp...", tee=getSetting('appLog'))
    sshSuccess = target.openSshConn(userName=target.userName)
    if (not sshSuccess):
        target.shutdownAndExit(f"Test[user test ssh]:Failed to open ssh conn.", exitCode=EXIT.Implementation)
    printAndLog("Test ssh passed successfully!", doPrint=False, tee=getSetting('appLog'))
    target.sendFile (pathToFile=getSetting('repoDir'),xFile='README.md',timeout=120)
    printAndLog("Test scp passed successfully!", doPrint=False, tee=getSetting('appLog'))
    printAndLog("Ssh and scp test OK!", tee=getSetting('appLog'))
    if(not target.onlySsh): # only for debian
        target.closeSshConn()
    return
