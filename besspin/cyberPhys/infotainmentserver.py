#! /usr/bin/env python3
""" 
This is executed after loading the app on the xTarget to execute this app
"""
import requests

from besspin.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def install (xTarget):
    # xTarget is a besspin xTarget object
    appLog = getSetting('appLog',targetId=xTarget.targetId)

    printAndLog(f"{xTarget.targetIdInfo}infotainment server install: starting the service...", doPrint=False, tee=appLog)
    xTarget.runCommand("mkdir -p /usr/local/sbin",tee=appLog)
    xTarget.runCommand("install infotainment_server.elf /usr/local/sbin/infotainment_server", erroneousContents="install:", tee=appLog)
    serviceTimeout = 120
    if isEqSetting('osImage','debian',targetId=xTarget.targetId):
        xTarget.runCommand("cp infotainment-server.service /lib/systemd/system/infotainment-server.service", erroneousContents="install:", tee=appLog)
        xTarget.runCommand("systemctl enable infotainment-server.service", timeout=serviceTimeout, tee=appLog)
        xTarget.runCommand("systemctl start infotainment-server.service", erroneousContents=["Failed to start", "error code"], tee=appLog)
    elif isEqSetting('osImage','FreeBSD', targetId=xTarget.targetId):
        xTarget.runCommand("install -d /usr/local/etc/rc.d", tee=appLog)
        xTarget.runCommand("install infotainment-server.sh /usr/local/etc/rc.d/infotainment-server", erroneousContents="install:", tee=appLog)
        # connectal and vcu118 FreeBSD are slow with these commands. Easier to just bump it up for all
        xTarget.runCommand("service infotainment-server enable", erroneousContents="infotainment-server does not exist", tee=appLog, timeout=serviceTimeout)
        xTarget.runCommand("service infotainment-server start", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
    else:
        xTarget.terminateAndExit(f"{xTarget.targetIdInfo}Can't start infotainment server service on <{getSetting('osImage', targetId=xTarget.targetId)}>",
                                 exitCode=EXIT.Dev_Bug)

    printAndLog(f"{xTarget.targetIdInfo}infotainment server installed successfully.",tee=appLog)

@decorate.debugWrap
@decorate.timeWrap
def isServiceRunning (xTarget):
    # TODO: query whether the service is running
    # Perhaps listen for messages from the server?
    # Running the command below takes several seconds, thus is impractical:
    #xTarget.runCommand("systemctl status infotainment-server.service", erroneousContents=["???"], tee=appLog)
    return True # not sure what to do here yet

@decorate.debugWrap
@decorate.timeWrap
def restart (xTarget):
    appLog = getSetting('appLog',targetId=xTarget.targetId)
    printAndLog(f"{xTarget.targetIdInfo}Restarting infotainment server service!", tee=appLog)
    serviceTimeout = 120
    if isEqSetting('osImage','debian',targetId=xTarget.targetId):
        xTarget.runCommand("pkill infotainment_se",exitOnError=False,tee=appLog)
        xTarget.runCommand("systemctl stop infotainment-server.service", erroneousContents=["Failed to stop", "error code"], tee=appLog)
        xTarget.runCommand("systemctl start infotainment-server.service", erroneousContents=["Failed to start", "error code"], tee=appLog)
    elif isEqSetting('osImage','FreeBSD',targetId=xTarget.targetId):
        xTarget.runCommand("service infotainment-server stop", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
        xTarget.runCommand("service infotainment-server start", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
    else:
        xTarget.terminateAndExit(f"{xTarget.targetIdInfo}Can't restart infotainment server service on <{getSetting('osImage', targetId=xTarget.targetId)}>",
                                 exitCode=EXIT.Dev_Bug)
    printAndLog(f"{xTarget.targetIdInfo}infotainment server restarted.",tee=appLog)