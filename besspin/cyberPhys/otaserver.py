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

    xTarget.runCommand("echo \"Starting ota service...\"",tee=appLog)
    xTarget.runCommand("mkdir -p /usr/local/sbin",tee=appLog)
    xTarget.runCommand("install ota.elf /usr/local/sbin/ota", erroneousContents="install:",tee=appLog)
    serviceTimeout = 180
    if isEqSetting('osImage','debian',targetId=xTarget.targetId):
        xTarget.runCommand("cp ota.service /lib/systemd/system/ota.service", erroneousContents="install:",tee=appLog)
        xTarget.runCommand("systemctl enable ota.service", timeout=serviceTimeout, tee=appLog)
        xTarget.runCommand("systemctl start ota.service", erroneousContents=["Failed to start", "error code"],tee=appLog)
    elif isEqSetting('osImage','FreeBSD',targetId=xTarget.targetId):
        # Install OTA server
        xTarget.runCommand("install -d /usr/local/etc/rc.d",tee=appLog)
        xTarget.runCommand("install ota.sh /usr/local/etc/rc.d/ota", erroneousContents="install:",tee=appLog)
        # connectal and vcu118 FreeBSD are slow with these commands. Easier to just bump it up for all
        xTarget.runCommand("service ota enable", erroneousContents="ota does not exist",tee=appLog, timeout=serviceTimeout)
        xTarget.runCommand("service ota start", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
    else:
        xTarget.terminateAndExit (f"{xTarget.targetIdInfo}Can't start ota service on <{getSetting('osImage',targetId=xTarget.targetId)}>",
                     exitCode=EXIT.Dev_Bug)

    printAndLog(f"{xTarget.targetIdInfo}Ota installed successfully.",tee=appLog)

@decorate.debugWrap
@decorate.timeWrap
def isServiceRunning (xTarget):
    otaserver_port = getSetting('cyberPhysOtaServerPort')
    url = f"http://{xTarget.ipTarget}:{otaserver_port}"
    try:
        resp = requests.get(url)
        assert (resp.status_code == 200),f"{xTarget.targetIdInfo}Ota service: resp != 200."
        return True
    except Exception as e:
        warnAndLog(f"{xTarget.targetIdInfo}Ota service test failed.",exc=e)
        return False

@decorate.debugWrap
@decorate.timeWrap
def restart (xTarget):
    appLog = getSetting('appLog',targetId=xTarget.targetId)
    printAndLog(f"{xTarget.targetIdInfo}Restarting ota service!",tee=appLog)
    serviceTimeout = 120
    if isEqSetting('osImage','debian',targetId=xTarget.targetId):
        xTarget.runCommand("systemctl restart ota.service", erroneousContents=["Failed", "error code"],tee=appLog)
    elif isEqSetting('osImage','FreeBSD',targetId=xTarget.targetId):
        xTarget.runCommand("service ota restart", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
    else:
        xTarget.terminateAndExit (f"{xTarget.targetIdInfo}Can't restart ota service on <{getSetting('osImage',targetId=xTarget.targetId)}>",
                     exitCode=EXIT.Dev_Bug)
    printAndLog(f"{xTarget.targetIdInfo}Ota restared.",tee=appLog)