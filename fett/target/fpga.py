#! /usr/bin/env python3
""" 
Main fpga class + misc fpga functions
"""

from fett.base.utils.misc import *
from fett.target.common import *

import subprocess, getpass, psutil
import sys, signal, os

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
    try:
        subprocess.call(['gfe-clear-flash'],stdout=gfeOut,stderr=gfeOut,timeout=90)
    except Exception as exc:
        errorAndLog(f"<gfe-clear-flash> has failed. Will continue anyway.",doPrint=False,exc=exc)

    printAndLog("Programming the bitfile...")
    nAttempts = 2
    for iAttempt in range(nAttempts):
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
def resetEthAdaptor ():
    logAndExit (f"<fpga.resetEthAdaptor> is not yet implemented.",exitCode=EXIT.Implementation)


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