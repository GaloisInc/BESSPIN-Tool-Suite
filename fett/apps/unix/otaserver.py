#! /usr/bin/env python3
""" 
This is executed after loading the app on the xTarget to execute this app
"""
import requests

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def install (xTarget):
    # xTarget is a fett xTarget object
    appLog = getSetting('appLog',targetId=xTarget.targetId)

    xTarget.runCommand("echo \"Starting ota service...\"",tee=appLog)
    xTarget.runCommand("mkdir -p /usr/local/sbin",tee=appLog)
    xTarget.runCommand("install ota.elf /usr/local/sbin/ota", erroneousContents="install:",tee=appLog)
    serviceTimeout = 120
    if isEqSetting('osImage','debian',targetId=xTarget.targetId):
        xTarget.runCommand("cp ota.service /lib/systemd/system/ota.service", erroneousContents="install:",tee=appLog)
        xTarget.runCommand("systemctl enable ota.service", timeout=serviceTimeout, tee=appLog)
        xTarget.runCommand("systemctl start ota.service", erroneousContents=["Failed to start", "error code"],tee=appLog)
    elif isEqSetting('osImage','FreeBSD',targetId=xTarget.targetId):
        # Install gdb
        xTarget.runCommand("install gdb-freebsd-riscv64-static /usr/local/sbin/gdb", erroneousContents="install:",tee=appLog)
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
def deploymentTest (xTarget) -> bool:
    appLog = getSetting('appLog',targetId=xTarget.targetId)
    otaserver_port = getSetting('OtaServerPortTarget')
    url = f"http://{xTarget.ipTarget}:{otaserver_port}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            return True
        else:
            printAndLog(f"{xTarget.targetIdInfo}Ota service test failed!",tee=appLog)
            return False
    except Exception as e:
        printAndLog(f"{xTarget.targetIdInfo}Ota service test failed with exception <{e}>",tee=appLog)
        return False

@decorate.debugWrap
@decorate.timeWrap
def restart (xTarget):
    appLog = getSetting('appLog',targetId=xTarget.targetId)
    printAndLog(f"{xTarget.targetIdInfo}Restarting ota service!",tee=appLog)
    serviceTimeout = 120
    if isEqSetting('osImage','debian',targetId=xTarget.targetId):
        xTarget.runCommand("systemctl stop ota.service", erroneousContents=["Failed to stop", "error code"],tee=appLog)
        xTarget.runCommand("systemctl start ota.service", erroneousContents=["Failed to start", "error code"],tee=appLog)
    elif isEqSetting('osImage','FreeBSD',targetId=xTarget.targetId):
        xTarget.runCommand("service ota stop", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
        xTarget.runCommand("service ota start", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
    else:
        xTarget.terminateAndExit (f"{xTarget.targetIdInfo}Can't restart ota service on <{getSetting('osImage',targetId=xTarget.targetId)}>",
                     exitCode=EXIT.Dev_Bug)
    printAndLog(f"{xTarget.targetIdInfo}Ota restared. Testing...",tee=appLog)
    return deploymentTest(xTarget)