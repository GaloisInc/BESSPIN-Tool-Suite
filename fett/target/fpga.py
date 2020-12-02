#! /usr/bin/env python3
""" 
fpgaTarget class
"""

from fett.base.utils.misc import *
from fett.target.common import *
from fett.target import vcu118
from fett.target import common

import pexpect, subprocess, enum, re

class failStage (enum.Enum):
    openocd = enum.auto()
    gdb = enum.auto()
    uart = enum.auto()
    network = enum.auto()
    unknown = enum.auto()

    def __gt__(self, other):
        if (str(self.__class__) == str(other.__class__)):
            return self.value > other.value
        logAndExit (f"failStage: __gt__ not implemented for inputs of type {type(self)} and {type(other)}.",exitCode=EXIT.Dev_Bug)

    def __lt__(self, other):
        if (str(self.__class__) == str(other.__class__)):
            return self.value < other.value
        logAndExit (f"failStage: __lt__ not implemented for inputs of type {type(self)} and {type(other)}.",exitCode=EXIT.Dev_Bug)

class fpgaTarget(object):
    def __init__(self, targetId=None):
        self.gdbProcess = None 
        self.openocdProcess = None

        self.fGdbOut = None
        self.fOpenocdOut = None

        self.gdbPort = self.findPort(portUse='GDB')
        printAndLog(f"{self.targetIdInfo}fpgaTarget: gdb port is <{self.gdbPort}>.",
            doPrint=not (isEqSetting('mode', 'evaluateSecurityTests') and (self.osImage=='FreeRTOS')))
        if (self.useOpenocd()):
            self.openocdPort = self.findPort(portUse='openocd')
            printAndLog(f"{self.targetIdInfo}fpgaTarget: openocd telnet port is <{self.openocdPort}>.",
                doPrint=not (isEqSetting('mode', 'evaluateSecurityTests') and (self.osImage=='FreeRTOS')))

        self.readGdbOutputUnix = 0 #beginning of file

    @decorate.debugWrap
    def useOpenocd (self):
        return ((self.target=='vcu118') or ((self.target=='awsf1') and (self.pvAWS=='firesim')))

    @decorate.debugWrap
    @decorate.timeWrap
    def fpgaStart (self, elfPath, elfLoadTimeout=15, isReload=False):
        if (self.processor=='bluespec_p3'):
            time.sleep(3) #need time after programming the fpga

        if (self.useOpenocd()):
            # start the openocd process
            cfgSuffix = self.target if (self.target!='awsf1') else self.pvAWS
            openocdCfg = os.path.join(getSetting('repoDir'),'fett','target','utils',f'openocd_{cfgSuffix}.cfg')
            self.fOpenocdOut = ftOpenFile(os.path.join(getSetting('workDir'),f'openocd{self.targetSuffix}.out'), 'ab')

            # Please be careful editing this part. It is protected by `openocdLock`, and it cannot be done 
            # using a context manager to avoid deadlocks in case of retries (use of fpgaReload).
            getSetting('openocdLock').acquire()
            openocdExtraCmds = (f"set _CHIPNAME riscv{self.targetSuffix}; gdb_port {self.gdbPort}; "
                f"telnet_port {self.openocdPort}{self.getOpenocdCustomCfg(isReload=isReload)}")
            try:
                self.openocdProcess = pexpect.spawn(
                    f"openocd --command '{openocdExtraCmds}' -f {openocdCfg}",
                        logfile=self.fOpenocdOut, timeout=15, echo=False)
                self.openocdProcess.expect(f"Listening on port {self.openocdPort} for telnet", timeout=15)
            except Exception as exc:
                if ((self.target=='vcu118') and (self.fpgaStartRetriesIdx < self.fpgaStartRetriesMax - 1)):
                    self.fpgaStartRetriesIdx += 1
                    errorAndLog (f"{self.targetIdInfo}fpgaStart: Failed to spawn the openocd process. Trying again ({self.fpgaStartRetriesIdx+1}/{self.fpgaStartRetriesMax})...",exc=exc)
                    getSetting('openocdLock').release()
                    return self.fpgaReload (elfPath, elfLoadTimeout=elfLoadTimeout, stage=failStage.openocd)
                self.terminateAndExit(f"{self.targetIdInfo}fpgaStart: Failed to spawn the openocd process.",overrideShutdown=True,exc=exc,exitCode=EXIT.Run)
            getSetting('openocdLock').release()

        self.setupUart()

        self.gdbProgStart(elfPath,elfLoadTimeout)
        
        if ((self.processor=='bluespec_p3') and (self.target=='vcu118')):
            _,wasTimeout,_ = self.expectFromTarget("bbl loader", f"attempt to boot {self.processor}",
                exitOnError=False, timeout=15, issueInterrupt=False,
                suppressWarnings=True, sshRetry=False)
            if (wasTimeout):
                if ((self.bluespec_p3BootAttemptsIdx < self.bluespec_p3BootAttemptsMax - 1)):
                    self.stopShowingTime.set()
                    time.sleep(1) #wait for the function to print "Completed" on the screen
                    printAndLog(f"{self.targetIdInfo}Failed to boot {self.processor}. "
                        f"Trying again ({self.bluespec_p3BootAttemptsIdx+2}/{self.bluespec_p3BootAttemptsMax})...")
                    self.fpgaTearDown(isReload=True,stage=failStage.uart)
                    self.stopShowingTime = common.showElapsedTime (getSetting('trash'),estimatedTime=self.sumTimeout)
                    return self.fpgaStart(elfPath, elfLoadTimeout=elfLoadTimeout)
                else:
                    self.terminateAndExit(f"{self.targetIdInfo}Failed to boot {self.processor}.",overrideShutdown=True,
                        overrideConsole=True,exitCode=EXIT.Run)

        return

    @decorate.debugWrap
    @decorate.timeWrap
    def gdbProgStart(self,elfPath,elfLoadTimeout,mainProg=True):
        # start the gdb process
        self.fGdbOut = ftOpenFile(os.path.join(getSetting('workDir'), f'gdb{self.targetSuffix}.out'), 'wb')
        try:
            self.gdbProcess = pexpect.spawn(
                f"riscv64-unknown-elf-gdb {elfPath}",
                    logfile=self.fGdbOut, timeout=15, echo=False)
            self.gdbProcess.expect(self.getGdbEndsWith(), timeout=15)
        except Exception as exc:
            if ((self.target=='vcu118') and (self.fpgaStartRetriesIdx < self.fpgaStartRetriesMax)):
                self.fpgaStartRetriesIdx += 1
                errorAndLog (f"{self.targetIdInfo}gdbProgStart: Failed to spawn the gdb process. Trying again ({self.fpgaStartRetriesIdx+1}/{self.fpgaStartRetriesMax})...",exc=exc)
                return self.fpgaReload (elfPath, elfLoadTimeout=elfLoadTimeout, stage=failStage.gdb)
            self.terminateAndExit(f"{self.targetIdInfo}gdbProgStart: Failed to spawn the gdb process.",overrideShutdown=True,exc=exc,exitCode=EXIT.Run)

        # configure gdb
        if (mainProg):
            self.runCommandGdb("set confirm off")
            self.runCommandGdb("set width unlimited")
            self.runCommandGdb("set height unlimited")
            self.runCommandGdb("set print entry-values no")
            self.runCommandGdb("set remotetimeout 60")
            self.runCommandGdb("set pagination off")
        self.runCommandGdb(f"set architecture riscv:rv{self.xlen}")
        self.runCommandGdb("define hook-continue\ndont-repeat\nend") #we don't want to 'continue' on extra presses due to encoding and such

        self.gdbConnect()

        if ((self.target=='awsf1') and (self.pvAWS=='firesim')):
            self.runCommandGdb ('set $pc=0xC0000000')
        elif (self.target=='vcu118'):
            # reset the board
            self.softReset()

            self.gdbLoad (elfLoadTimeout=elfLoadTimeout)

            if (self.processor=='bluespec_p3'):
                time.sleep(3) # Bluespec_p3 needs time here before being able to properly continue.
        if (mainProg and isEqSetting('mode','evaluateSecurityTests') and isEnabled('useCustomScoring')):
            self.setupGdbCustomScoring()

        self.continueGdb()

    @decorate.debugWrap
    @decorate.timeWrap
    def gdbLoad (self,elfLoadTimeout=15):
        self.runCommandGdb("load",timeout=elfLoadTimeout,erroneousContents="failed", expectedContents="Transfer rate")

    @decorate.debugWrap
    @decorate.timeWrap
    def gdbDetach (self):
        self.runCommandGdb("detach")
        if (self.useOpenocd()):
            self.expectOnOpenocd ("dropped 'gdb' connection","detach")

    @decorate.debugWrap
    @decorate.timeWrap
    def fpgaReload (self, elfPath, elfLoadTimeout=15, stage=failStage.unknown):
        if (self.target!='vcu118'):
            self.terminateAndExit(f"{self.targetIdInfo}<fpgaReload> is not implemented for target {self.target}.",overrideShutdown=True)
        self.fpgaTearDown(isReload=True,stage=stage)
        vcu118.programBitfile(doPrint=False, targetId=self.targetId)
        time.sleep(3) #sometimes after programming the fpga, the OS needs a second to release the resource to be used by openocd
        self.fpgaStart(elfPath, elfLoadTimeout=elfLoadTimeout, isReload=True)
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def startGdbDebug (self):
        self.interruptGdb()
        self.gdbDetach()
        self.runCommandGdb("quit",endsWith=pexpect.EOF,exitOnError=False)
        printAndLog('*'*15 + " <gdbDebug> mode " + '*'*15)
        printAndLog(f"GDB Launch: In a separate window, run <riscv64-unknown-elf-gdb {getSetting('osImageElf',targetId=self.targetId)}>.")
        printAndLog(f"GDB Connect: In the GDB console, run <target remote localhost:{self.gdbPort}>.")
        printAndLog("Continue: To resume the run, you have to continue <c>.")
        printAndLog("Exit: Please <detach> then <quit> before exitting FETT.")

    @decorate.debugWrap
    @decorate.timeWrap
    def endGdbDebug (self):
        try:
            self.gdbProcess = pexpect.spawn(
                f"riscv64-unknown-elf-gdb {getSetting('osImageElf',targetId=self.targetId)}",
                    logfile=self.fGdbOut, timeout=15, echo=False)
            self.gdbProcess.expect(self.getGdbEndsWith(), timeout=15)
        except Exception as exc:
            self.terminateAndExit(f"fpgaStart: Failed to spawn the gdb process.",overrideShutdown=True,exc=exc,exitCode=EXIT.Run)
        self.runCommandGdb("define hook-continue\ndont-repeat\nend")
        self.gdbConnect()
        self.continueGdb()
   
    @decorate.debugWrap
    @decorate.timeWrap
    def gdbConnect (self):
        with getSetting('openocdLock'):
            self.runCommandGdb(f"target remote localhost:{self.gdbPort}",erroneousContents="Failed")
            if (self.useOpenocd()):
                self.expectOnOpenocd (f"accepting 'gdb' connection on tcp/{self.gdbPort}","connect")

    @decorate.debugWrap
    @decorate.timeWrap
    def softReset (self, isRepeated=False):
        if (self.target!='vcu118'):
            self.terminateAndExit(f"<softReset> is not implemented for target {self.target}.",overrideShutdown=True)
        # reset hart
        self.riscvWrite(int("0x6FFF0000", base=16),1,32) # set *(0x6fff0000)=1
        if (self.procFlavor=='chisel'):
            self.expectOnOpenocd ("unexpectedly reset!","softReset")
        else:
            time.sleep(1)

        if (self.processor=='bluespec_p3'):
            self.setUnixBluespecP3()

        # detach from gdb
        self.gdbDetach()

        # Re-connect
        self.gdbConnect()

        if (self.processor=='bluespec_p3'):
            self.setUnixBluespecP3()

        if ((not isRepeated) and (self.osImage=='FreeRTOS')):
            if (self.procFlavor=='bluespec'):
                self.softReset(isRepeated=True)

    @decorate.debugWrap
    @decorate.timeWrap
    def setUnixBluespecP3 (self):
        # required to boot unix on bluespec_p3
        self.runCommandGdb("set $a0 = 0")
        time.sleep(1)
        self.runCommandGdb("set $a1 = 0x70000020")
        time.sleep(3)

    @decorate.debugWrap
    @decorate.timeWrap
    def riscvWrite(self,address,value, size):
        size_options = {8: "char", 32: "int"}

        # Validate input
        if size not in size_options:
            logAndExit(f"riscvWrite: write size {size} must be one of {list(size_options.keys())}",exitCode=EXIT.Dev_Bug)

        # Perform the write command using the gdb set command
        self.runCommandGdb(
            f"set *(({size_options[size]} *) 0x{address:x}) = 0x{value:x}", erroneousContents="Cannot access memory")

    @decorate.debugWrap
    @decorate.timeWrap
    def expectOnOpenocd (self,endsWith,command,**kwargs):
        if (not self.useOpenocd()):
            self.terminateAndExit("<expectOnOpenocd> should not be called when <useOpenocd> is disabled.",
                exitCode=EXIT.Dev_Bug)
        return self.expectFromTarget (endsWith,command=f"openocd:{command}",
                overrideShutdown=True,process=self.openocdProcess,**kwargs)

    @decorate.debugWrap
    def runCommandGdb(self, command, endsWith=None, timeout=15, **kwargs):
        endsWith = self.getGdbEndsWith() if endsWith is None else endsWith
        """convenience runCommand for GDB"""
        return self.runCommand(command,
                                endsWith=endsWith,
                                sendToNonUnix=True,
                                timeout=timeout,
                                process=self.gdbProcess,
                                overrideShutdown=True,
                                **kwargs)

    @decorate.debugWrap
    def getGdbEndsWith (self):
        return r"\(gdb\)"

    @decorate.debugWrap
    def interruptGdb(self):
        """implement keyboardInterrupt for GDB"""
        if ((self.target=='awsf1') and (self.pvAWS=='firesim')):
            self.sendToTarget('\x03',exitOnError=False,process=self.gdbProcess) #send one extra \x03
        self.keyboardInterrupt(exitOnError=False,retryCount=1,process=self.gdbProcess,
            endsWith=self.getGdbEndsWith(),sendToNonUnix=True,timeout=15,
            respondEndsWith=(r"Stop debugging it\? \(y or n\)","y"))

    @decorate.debugWrap
    def continueGdb(self):
        self.runCommandGdb('c', endsWith='Continuing')

    @decorate.debugWrap
    @decorate.timeWrap
    def getRegsValues(self,regNames=None):
        if (regNames is None):
            if (self.target=='awsf1'):
                warnAndLog("getRegsValues: There is a problem with GDB on AWSf1 when returning <info all-registers>. "
                    f"This command might result in error. Please specify the needed regs instead.")
            regSpec = "all-registers"
        elif (isinstance(regNames,list)):
            regSpec = f"registers {' '.join(regNames)}"
        else:
            warnAndLog("getRegsValues: <regNames> should either be None for all regs, or a list of register "
                f"names. Will use <{regNames} as is.")
            regSpec = f"registers {regNames}"
        _,retGdb,_,_ = self.runCommandGdb(f"info {regSpec}")
        regsDict = dict()
        for line in retGdb.splitlines():
            regMatch = re.match(r"\s*(?P<regName>[a-z][a-z0-9]+)\s+(?P<hexVal>0x[0-9a-f]+)\s.*$",line)
            if (regMatch is not None):
                try:
                    hexVal = int(regMatch.group('hexVal'),16)
                except Exception as exc:
                    warnAndLog(f"getRegsValues: Failed to read the value <{regMatch.group('hexVal')}> "
                        f"of reg:<{regMatch.group('regName')}>",exc=exc,doPrint=False)
                    continue
                regsDict[regMatch.group('regName')] = hexVal
        return regsDict

    @decorate.debugWrap     
    def getOpenocdCustomCfg(self, isReload=False):
        return '' #virtual implementation

    @decorate.debugWrap
    def setupUart(self):
        return #virtual implementation

    @decorate.debugWrap
    @decorate.timeWrap
    def setupGdbCustomScoring (self):
        for funcCheckpoint in getSettingDict('customizedScoring','funcCheckpoints'):
            retCommand = self.runCommandGdb (f"dprintf {funcCheckpoint},\"<GDB-CHECKPOINT>:{funcCheckpoint}\\n\"",
                erroneousContents="not defined", exitOnError=False)
            if (not retCommand[0]):
                warnAndLog (f"setupGdbCustomScoring: Failed to insert a checkpoint at {funcCheckpoint}."
                            f"See <{self.fGdbOut.name}> for more details.")
        if (getSettingDict('customizedScoring','memAddress') != -1):
            memAddress = getSettingDict('customizedScoring','memAddress')
            retCommand = self.runCommandGdb (f"display/x * (int *) 0x{memAddress:08x}",
                erroneousContents=['No symbol', 'warning'], exitOnError=False)
            if (not retCommand[0]):
                warnAndLog (f"setupGdbCustomScoring: Unexpecte output while reading 0x{memAddress:08x}."
                            f"See <{self.fGdbOut.name}> for more details.")
            else:
                self.runCommandGdb (f"watch * (int *) 0x{memAddress:08x}", exitOnError=False)
                setCmd = f"set * (int *) 0x{memAddress:08x} = {getSettingDict('customizedScoring','memResetValue')}"
                self.runCommandGdb (f"commands\n{setCmd}\nc\nend", exitOnError=False)

    @decorate.debugWrap
    @decorate.timeWrap
    def getGdbOutput(self):
        gdbOut = "\n~~~GDB LOGGING~~~\n"
        try:
            gdbLines = '\n'.join(ftReadLines(self.fGdbOut.name, "r"))
            if (self.readGdbOutputUnix == 0): #We don't want the GDB out before the string "Continuing."
                gdbOut += gdbLines[gdbLines.find("Continuing."):]
            elif (self.readGdbOutputUnix < len(gdbLines)): #Only the new lines
                gdbOut += gdbLines[self.readGdbOutputUnix:]
            self.readGdbOutputUnix = len(gdbLines) #move the cursor
        except Exception as exc:
            gdbOut += "<Warning-No-Logs>"
            warnAndLog("<getGdbOutput> failed to obtain the GDB output.",
                        exc=exc)
        gdbOut += "\n~~~~~~~~~~~~~~~~~\n"
        return gdbOut

    @decorate.debugWrap
    @decorate.timeWrap
    def fpgaTearDown (self,isReload=False,stage=failStage.unknown):
        if (isEqSetting('mode','evaluateSecurityTests') and (not isReload) and (stage > failStage.gdb)):
            # Analyze gdb output for FreeRTOS
            if (self.osImage=='FreeRTOS'):
                self.interruptGdb ()
                self.gdbOutLines = ftReadLines(self.fGdbOut.name)
                relvSigs = ['SIGTRAP', 'SIGINT'] # first match list
                testLogFile = getSetting("currentTest")[3]
                sigFound = None
                for xSig in relvSigs:
                    if (matchExprInLines(rf"^.*{xSig}.*$",self.gdbOutLines)):
                        sigFound = xSig
                        break
                # Fetch relevant registers values
                if (sigFound):
                    relvRegs = {'mcause':'Unknown', 'mepc':'Unknown'}
                    for relvReg in relvRegs:
                        try:
                            self.gdbProcess.sendline(f"p/x ${relvReg}")
                            self.gdbProcess.expect(r"\$\d+\s*=\s*0x[\dabcdef]+", timeout=5)
                            regpxStr = str(self.gdbProcess.after,'utf-8')
                            regpxVal = regpxStr.split('=')[-1].strip()
                            relvRegs[relvReg] = regpxVal
                        except Exception as exc:
                            warnAndLog (f"targetTearDown: Failed to fetch the value of ${relvReg}.",exc=exc,doPrint=False) 
                            break
                    regsValuesStr = ','.join([f"{relvReg}={relvRegs[relvReg]}" for relvReg in relvRegs])
                    testLogFile.write(f"\n<GDB-{sigFound}> with {regsValuesStr}\n")

        if ((self.target=='vcu118') and (self.uartSession is not None) and self.uartSession.is_open):
            try:
                logging.debug(f"{self.targetIdInfo}Closing uart_session.")
                self.uartSession.close()
            except Exception as exc:
                warnAndLog(f"{self.targetIdInfo}fpgaTearDown: unable to close the serial session", exc=exc,doPrint=False)

        if (stage > failStage.gdb):
            self.interruptGdb()
            self.gdbDetach()

        if (self.useOpenocd()):
            # quit openocd
            shellCommand(f"echo 'shutdown' | nc localhost {self.openocdPort}",check=False,shell=True,timeout=5)
            try:
                self.openocdProcess.expect(pexpect.EOF,timeout=10)
            except Exception as exc:
                warnAndLog(f"{self.targetIdInfo}fpgaTearDown: Failed to shutdown the openocd process.",doPrint=False,exc=exc)

        # quit gdb
        if (stage > failStage.gdb):
            self.runCommandGdb("quit",endsWith=pexpect.EOF,exitOnError=False)

        filesToClose = [self.fGdbOut, self.fOpenocdOut]
        if (self.target=='vcu118'):
            processes = [('riscv64-unknown-elf-gdb',self.gdbProcess), ('openocd',self.openocdProcess)]
            for pName, proc in processes:
                if (isEqSetting('mode','cyberPhys')): #have to kill selectively
                    try:
                        pID = os.getpgid(proc.pid)
                    except Exception as exc:
                        warnAndLog(f"{self.targetIdInfo}Can't get pgid. Process <{pName}> was already killed.",exc=exc,doPrint=False)
                        continue #process was already killed
                    sudoShellCommand(['kill', '-9', f"{pID}"],check=False)
                else: #nonsense-free
                    sudoShellCommand(['pkill', '-9', f"{pName}"],check=False)
            if (isReload):
                filesToClose.append(self.fTtyOut)

        for xFile in filesToClose:
            if (xFile is None):
                continue
            try:
                xFile.close()
            except Exception as exc:
                warnAndLog(f"{self.targetIdInfo}fpgaTearDown: Failed to close <{xFile.name}>.",doPrint=False,exc=exc)
