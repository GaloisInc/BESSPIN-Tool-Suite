#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""
import requests

from fett.base.utils.misc import *

OTASERVER_PORT = 5050

@decorate.debugWrap
@decorate.timeWrap
def install (target):
    # target is a fett target object
    appLog = getSetting('appLog')

    target.runCommand("echo \"Starting ota service...\"",tee=appLog)
    target.runCommand("mkdir -p /usr/local/sbin",tee=appLog)
    target.runCommand("install ota.elf /usr/local/sbin/ota", erroneousContents="install:",tee=appLog)
    serviceTimeout = 120
    if isEqSetting('osImage','debian',target.targetId):
        target.runCommand("cp ota.service /lib/systemd/system/ota.service", erroneousContents="install:",tee=appLog)
        target.runCommand("systemctl enable ota.service", timeout=serviceTimeout, tee=appLog)
        target.runCommand("systemctl start ota.service", erroneousContents=["Failed to start", "error code"],tee=appLog)
    elif isEqSetting('osImage','FreeBSD',target.targetId):
        # Install gdb
        target.runCommand("install gdb-freebsd-riscv64-static /usr/local/sbin/gdb", erroneousContents="install:",tee=appLog)
        # Install OTA server
        target.runCommand("install -d /usr/local/etc/rc.d",tee=appLog)
        target.runCommand("install ota.sh /usr/local/etc/rc.d/ota", erroneousContents="install:",tee=appLog)
        # connectal and vcu118 FreeBSD are slow with these commands. Easier to just bump it up for all
        target.runCommand("service ota enable", erroneousContents="ota does not exist",tee=appLog, timeout=serviceTimeout)
        target.runCommand("service ota start", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
    else:
        target.terminateAndExit (f"Can't start ota service on <{getSetting('osImage',target.targetId)}>",
                     exitCode=EXIT.Dev_Bug)

    printAndLog("Ota installed successfully.",tee=appLog)

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest (target) -> bool:
    appLog = getSetting('appLog')
    url = "http://" + target.ipTarget + ':' + str(OTASERVER_PORT)
    resp = requests.get(url)
    if resp.status_code == 200:
        return True
    else:
        printAndLog(f"Target <{target.targetId}: Ota service test failed!",tee=appLog)
        return False

@decorate.debugWrap
@decorate.timeWrap
def restart (target):
    appLog = getSetting('appLog')
    printAndLog(f"Target <{target.targetId}: Restarting ota service!",tee=appLog)
    serviceTimeout = 120
    if isEqSetting('osImage','debian',target.targetId):
        target.runCommand("systemctl stop ota.service", erroneousContents=["Failed to stop", "error code"],tee=appLog)
        target.runCommand("systemctl start ota.service", erroneousContents=["Failed to start", "error code"],tee=appLog)
    elif isEqSetting('osImage','FreeBSD',target.targetId):
        target.runCommand("service ota stop", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
        target.runCommand("service ota start", erroneousContents=["failed"], tee=appLog, timeout=serviceTimeout)
    else:
        target.terminateAndExit (f"Can't restart ota service on <{getSetting('osImage',target.targetId)}>",
                     exitCode=EXIT.Dev_Bug)
    printAndLog(f"Target <{target.targetId}: Ota restared. Testing...",tee=appLog)
    return deploymentTest(target)