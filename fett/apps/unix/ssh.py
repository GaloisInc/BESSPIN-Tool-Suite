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
    printAndLog("Testing ssh ", tee=getSetting('appLog'))
    # target.switchUser()
    if (target.isCurrentUserRoot and target.userName != 'root'):
        target.shutdownAndExit(f"Test[openSshConn]: User {target.userName} is not current root user. "
                               f"<{getSetting('osImage')}>.", exitCode=EXIT.Dev_Bug)
    sshSuccess = target.openSshConn(userName=target.userName)
    if (not sshSuccess):
        target.shutdownAndExit(f"Test[user test ssh]:Failed to open ssh conn.", exitCode=EXIT.Implementation)
    # target.sendFile (pathToFile=getSetting('repoDir'),xFile='README.md',timeout=120)
    target.closeSshConn()

    printAndLog("Test[user test ssh]: Ssh test OK!", doPrint=True, tee=getSetting('appLog'))
    return
