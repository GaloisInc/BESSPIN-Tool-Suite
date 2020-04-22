#! /usr/bin/env python3
""" 
Main fpga class + misc fpga functions
"""

from fett.base.utils.misc import *
from fett.target.common import *

import subprocess, getpass, psutil
import sys, signal, os, socket

class fpgaTarget (commonTarget):
    def __init__ (self):

        # For FreeBSD
        self.uartAttempts = 0
        self.limitUartAttempts = 8 if(isEqSetting('procFlavor','bluespec')) else 4

        super().__init__()
        return

@decorate.debugWrap
@decorate.timeWrap
def programBifile ():
    printAndLog("Preparing the FPGA environment...")
    clearProcesses()
    gfeOut = ftOpenFile(os.path.join(getSetting('workDir'),'gfe.out'),'a')
    printAndLog("Clearing the flash...",doPrint=False)
    gfeOut.write("\n\ngfe-clear-flash\n")
    try:
        subprocess.check_call(['gfe-clear-flash'],stdout=gfeOut,stderr=gfeOut,timeout=90)
    except Exception as exc:
        errorAndLog(f"<gfe-clear-flash> has failed. Will continue anyway.",doPrint=False,exc=exc)

    printAndLog("Programming the bitfile...")
    nAttempts = 2
    for iAttempt in range(nAttempts):
        gfeOut.write("\n\ngfe-program-fpga\n")
        clearProcesses()
        try:
            outProgram = subprocess.check_output(['gfe-program-fpga', getSetting('processor')],stderr=gfeOut,timeout=90)
            printAndLog(str(outProgram,'utf-8').strip())
            break
        except Exception as exc:
            if (iAttempt < nAttempts-1):
                errorAndLog(f"Failed to program the FPGA. Trying again...",doPrint=True,exc=exc)
            else:
                logAndExit(f"Failed to program the FPGA.",exc=exc,exitCode=EXIT.Run)

    gfeOut.close()
    printAndLog("FPGA was programmed successfully!")

    
@decorate.debugWrap
def setEthAdaptorName ():
    def tryToGetEthAdaptorName(ipOrMac,ipAddress=None,macAddress=None):
        if (ipOrMac not in ['MAC','IP']):
            logAndExit (f"<fpga.tryToGetEthAdaptorName> called with unrecognized argument <{ipOrMac}>.",exitCode=EXIT.Dev_Bug)
        if ((ipOrMac == 'MAC') and not macAddress):
            logAndExit (f"<fpga.tryToGetEthAdaptorName> called with 'MAC' and <macAddress=None>.",exitCode=EXIT.Dev_Bug)
        if ((ipOrMac == 'IP') and not ipAddress):
            logAndExit (f"<fpga.tryToGetEthAdaptorName> called with 'IP' and <ipAddress=None>.",exitCode=EXIT.Dev_Bug)

        for nic, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if (ipOrMac == 'MAC'):
                    if(addr.family == psutil.AF_LINK):
                        if (addr.address == macAddress):
                            setSetting('ethAdaptor',nic)
                            return True
                elif (ipOrMac == 'IP'):
                    if(addr.family == socket.AF_INET):
                        if (addr.address == ipAddress):
                            setSetting('ethAdaptor',nic)
                            return True
        return False

    printAndLog("getEthAdaptorName: Obtaining the ethernet adaptor name using the mac address...",doPrint=False)
    interfacesFile = '/etc/network/interfaces'
    macAddressMatch = matchExprInLines(r"^\s*map\s+(?P<macAddress>([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F]))\s+FPGA\s*$",ftReadLines(interfacesFile))
    if (not macAddressMatch):
        warnAndLog(f"getEthAdaptorName: Failed to get the mac address from {interfacesFile}.",doPrint=False)
    else:
        macAddress = macAddressMatch.group('macAddress')
        printAndLog(f"getEthAdaptorName: Mac address is <{macAddress}>",doPrint=False)
        if (tryToGetEthAdaptorName('MAC', macAddress=macAddress)):
            return
        else:
            printAndLog("getEthAdaptorName: Failed to find the adaptor with the found mac address!",doPrint=False)
    #Failed, have to try using the ip
    printAndLog("getEthAdaptorName: Trying to use the IP address instead...",doPrint=False)
    if (tryToGetEthAdaptorName('IP', ipAddress=getSetting('fpgaIpHost'))):
        return
    #Failed. Try again
    printAndLog(f"getEthAdaptorName: Failed to find the adaptor using the FPGA IP <{getSetting('fpgaIpHost')}>. Trying to <ifup -a> first...",doPrint=False)
    sudoShellCommand (['ifup', '-a'],f" You need sudo privileges to ifup all network adaptors: ")
    if (tryToGetEthAdaptorName('IP', ipAddress=getSetting('fpgaIpHost'))):
        return
    logAndExit("getEthAdaptorName: Failed to find the ethernet adaptor name!",exitCode=EXIT.Network)

@decorate.debugWrap
def sudoShellCommand (argsList, sudoPromptPrefix):
    try:
        sudoPrompt = sudoPromptPrefix + f" [sudo] password for {getpass.getuser()}: "
        command = ['sudo', '-p', sudoPrompt] + argsList
    except Exception as exc:
        logAndExit (f"sudo: Functions called with unsuitable arguments <{argsList}> and <{sudoPromptPrefix}>.",exc=exc,exitCode=EXIT.Dev_Bug)
    sudoOut = ftOpenFile(os.path.join(getSetting('workDir'),'sudo.out'),'a')
    sudoOut.write(f"\n\n{' '.join(command)}\n")
    try:
        subprocess.check_call(command,stdout=sudoOut,stderr=sudoOut,timeout=90)
    except Exception as exc:
        logAndExit (f"sudo: Failed to <{' '.join(command)}>. Check <sudo.out> for more details.",exc=exc,exitCode=EXIT.Network)
    sudoOut.close()

@decorate.debugWrap
def resetEthAdaptor ():
    #get the name if this is the first time called
    if (not doesSettingExist('ethAdaptor')):
        setEthAdaptorName ()
        printAndLog (f"Found ethernet adaptor name: <{getSetting('ethAdaptor')}>.",doPrint=False)

    sudoPromptPrefix = f"You need sudo privileges to reset the ethernet adaptor: "
    commands = [
                ['ip', 'addr', 'flush', 'dev', getSetting('ethAdaptor')],
                ['ifdown', getSetting('ethAdaptor')],
                ['ifup', getSetting('ethAdaptor')]
            ]
    
    nAttempts = 3
    isReset = False
    for iAttempt in range(nAttempts):
        for command in commands:
            sudoShellCommand(command,sudoPromptPrefix)
            time.sleep(1)
        time.sleep(2)
        try:
            isReset = psutil.net_if_stats()['eth1'].isup
        except Exception as exc:
            logAndExit (f"fpga.resetEthAdaptor: Failed to check that <{getSetting('ethAdaptor')}> is up.",exc=exc,exitCode=EXIT.Network)
        if (isReset):
            break
        elif (iAttempt < nAttempts - 1):
            printAndLog (f"fpga.resetEthAdaptor: Failed to reset <{getSetting('ethAdaptor')}>. Trying again...",doPrint=False)
            time.sleep(5)

    if (isReset):
        printAndLog (f"fpga.resetEthAdaptor: <{getSetting('ethAdaptor')}> is properly reset.",doPrint=False)
    else:
        logAndExit (f"fpga.resetEthAdaptor: Failed to reset <{getSetting('ethAdaptor')}>.",exitCode=EXIT.Network)
    
@decorate.debugWrap
def clearProcesses ():
    processesList = ['openocd', 'vivado_lab', 'hw_server', 'loader', 'pyprogram_fpga']
    procs = {p.pid : p.info for p in psutil.process_iter(['name', 'username'])}
    for pid, pinfo in procs.items():
        if ((pinfo['username'] == getpass.getuser()) and (pinfo['name'] in processesList)):
            if (psutil.pid_exists(pid)):
                warnAndLog (f"Killing the hanging process <{pinfo['name']}:{pid}>",doPrint=False)
                try:
                    os.kill(pid, signal.SIGKILL)
                except Exception as exc:
                    errorAndLog(f"Failed to kill <{pinfo['name']}:{pid}>.",doPrint=False,exc=exc)