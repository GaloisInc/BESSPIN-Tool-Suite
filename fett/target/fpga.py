import pexpect, signal
from pexpect import fdpexpect
import serial, subprocess, enum
import serial.tools.list_ports

from fett.base.utils.misc import *
from fett.target import vcu118

class failStage (enum.Enum):
    openocd = enum.auto()
    gdb = enum.auto()
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
        self.uartSession = None

        self.fGdbOut = None
        self.fOpenocdOut = None

        portsInc = 1 if (targetId is None) else targetId
        self.gdbPort = getSetting('gdbRemotePortBase') + portsInc
        self.openocdPort = getSetting('openocdTelnetPortBase') + portsInc

        self.readGdbOutputUnix = 0 #beginning of file

    @decorate.debugWrap
    @decorate.timeWrap
    def fpgaStart (self, elfPath, elfLoadTimeout=15):
        if (self.target=='vcu118'):
            # setup UART
            self.setupUart()

        # start the openocd process
        cfgSuffix = self.target if (self.target!='awsf1') else self.pvAWS
        openocdCfg = os.path.join(getSetting('repoDir'),'fett','target','utils',f'openocd_{cfgSuffix}.cfg')
        self.fOpenocdOut = ftOpenFile(os.path.join(getSetting('workDir'),'openocd.out'), 'ab')

        try:
            self.openocdProcess = pexpect.spawn(
                f"openocd --command 'gdb_port {self.gdbPort}; telnet_port {self.openocdPort}' -f {openocdCfg}",
                    logfile=self.fOpenocdOut, timeout=15, echo=False)
            self.openocdProcess.expect(f"Listening on port {self.openocdPort} for telnet", timeout=15)
        except Exception as exc:
            if ((self.target=='vcu118') and (self.fpgaStartRetriesIdx < self.fpgaStartRetriesMax - 1)):
                self.fpgaStartRetriesIdx += 1
                errorAndLog (f"fpgaStart: Failed to spawn the openocd process. Trying again ({self.fpgaStartRetriesIdx+1}/{self.fpgaStartRetriesMax})...",exc=exc)
                return self.fpgaReload (elfPath, elfLoadTimeout=elfLoadTimeout, stage=failStage.openocd)
            self.shutdownAndExit(f"fpgaStart: Failed to spawn the openocd process.",overwriteShutdown=True,exc=exc,exitCode=EXIT.Run)

        # start the gdb process
        self.fGdbOut = ftOpenFile(os.path.join(getSetting('workDir'), f'gdb.out'), 'wb')
        try:
            self.gdbProcess = pexpect.spawn(
                f"riscv64-unknown-elf-gdb {elfPath}",
                    logfile=self.fGdbOut, timeout=15, echo=False)
            self.gdbProcess.expect(self.getGdbEndsWith(), timeout=15)
        except Exception as exc:
            if ((self.target=='vcu118') and (self.fpgaStartRetriesIdx < self.fpgaStartRetriesMax)):
                self.fpgaStartRetriesIdx += 1
                errorAndLog (f"fpgaStart: Failed to spawn the gdb process. Trying again ({self.fpgaStartRetriesIdx+1}/{self.fpgaStartRetriesMax})...",exc=exc)
                return self.fpgaReload (elfPath, elfLoadTimeout=elfLoadTimeout, stage=failStage.gdb)
            self.shutdownAndExit(f"fpgaStart: Failed to spawn the gdb process.",overwriteShutdown=True,exc=exc,exitCode=EXIT.Run)

        # configure gdb
        self.runCommandGdb("set confirm off")
        self.runCommandGdb("set width 0")
        self.runCommandGdb("set height 0")
        self.runCommandGdb("set print entry-values no")
        self.runCommandGdb("set remotetimeout 60")
        self.runCommandGdb(f"set architecture riscv:rv{self.xlen}")
        self.runCommandGdb("define hook-continue\ndont-repeat\nend") #we don't want to 'continue' on extra presses due to encoding and such

        self.gdbConnect()

        if ((self.target=='awsf1') and (self.pvAWS=='firesim')):
            self.runCommandGdb ('set $pc=0xC0000000')
        elif (self.target=='vcu118'):
            # reset the board
            self.softReset()

            # start the tty process
            self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),'tty.out'),'ab')
            self.ttyProcess = fdpexpect.fdspawn(self.uartSession.fileno(),logfile=self.fTtyOut,timeout=30)
            self.process = self.ttyProcess

            self.gdbLoad (elfLoadTimeout=elfLoadTimeout)

        if (isEqSetting('mode','evaluateSecurityTests') and isEnabled('useCustomScoring')):
            self.setupGdbCustomScoring()

        self.runCommandGdb('c', endsWith='Continuing')

        return

    @decorate.debugWrap
    @decorate.timeWrap
    def gdbLoad (self,elfLoadTimeout=15):
        self.runCommandGdb("load",timeout=elfLoadTimeout,erroneousContents="failed", expectedContents="Transfer rate")
        if (self.procFlavor=='chisel'):
            self.expectOnOpenocd (f"Disabling abstract command writes to CSRs.","load")
        else:
            time.sleep(1)

    @decorate.debugWrap
    @decorate.timeWrap
    def gdbDetach (self):
        self.runCommandGdb("detach")
        self.expectOnOpenocd ("dropped 'gdb' connection","detach")

    @decorate.debugWrap
    @decorate.timeWrap
    def fpgaReload (self, elfPath, elfLoadTimeout=15, stage=failStage.unknown):
        if (self.target!='vcu118'):
            self.shutdownAndExit(f"<fpgaReload> is not implemented for target {self.target}.")
        self.fpgaTearDown(isReload=True,stage=stage)
        vcu118.programBitfile(doPrint=False, isReload=True)
        time.sleep(3) #sometimes after programming the fpga, the OS needs a second to release the resource to be used by openocd
        self.fpgaStart(elfPath, elfLoadTimeout=elfLoadTimeout)
        return
   
    @decorate.debugWrap
    @decorate.timeWrap
    def gdbConnect (self):
        self.runCommandGdb(f"target remote localhost:{self.gdbPort}",erroneousContents="Failed")
        self.expectOnOpenocd (f"accepting 'gdb' connection on tcp/{self.gdbPort}","connect")

    @decorate.debugWrap
    @decorate.timeWrap
    def softReset (self, isRepeated=False):
        if (self.target!='vcu118'):
            self.shutdownAndExit(f"<softReset> is not implemented for target {self.target}.")
        # reset hart
        self.riscvWrite(int("0x6FFF0000", base=16),1,32) # set *(0x6fff0000)=1
        if (self.procFlavor=='chisel'):
            self.expectOnOpenocd ("unexpectedly reset!","softReset")
        else:
            time.sleep(1)

        # detach from gdb
        self.gdbDetach()

        # Re-connect
        self.gdbConnect()

        if ((not isRepeated) and (self.osImage=='FreeRTOS')):
            if (self.procFlavor=='bluespec'):
                self.softReset(isRepeated=True)

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
        return self.expectFromTarget (endsWith,command=f"openocd:{command}",
                overwriteShutdown=True,process=self.openocdProcess,**kwargs)

    @decorate.debugWrap
    def runCommandGdb(self, command, endsWith=None, timeout=15, **kwargs):
        endsWith = self.getGdbEndsWith() if endsWith is None else endsWith
        """convenience runCommand for GDB"""
        return self.runCommand(command,
                                endsWith=endsWith,
                                sendToNonUnix=True,
                                timeout=timeout,
                                process=self.gdbProcess, **kwargs)

    @decorate.debugWrap
    def getGdbEndsWith (self):
        return r"\(gdb\)"

    @decorate.debugWrap
    def interruptGdb(self):
        """implement keyboardInterrupt for GDB"""
        self.keyboardInterrupt(shutdownOnError=False,retryCount=1,process=self.gdbProcess,
            endsWith=self.getGdbEndsWith(),sendToNonUnix=True,timeout=15)

    @staticmethod
    def findUartPort(search_vid=0x10C4,search_pid=0xEA70):
        # Get a list of all serial ports with the desired VID/PID
        ports = [port for port in serial.tools.list_ports.comports() if port.vid == search_vid and port.pid == search_pid]

        for port in ports:
            # Silabs chip on VCU118 has two ports. Locate port 1 from the hardware description
            m = re.search('LOCATION=.*:1.(\d)', port.hwid)
            if m:
                if m.group(1) == '1':
                    printAndLog(f"fpgaTarget: located UART device at {port.device} "
                                f"with serial number {port.serial_number}", doPrint=False)
                    extraMsg = "In case there is no output shown from the target's UART, "
                    extraMsg += "please make sure the tty is not used by any other tool (e.g. minicom), "
                    extraMsg += f"and is reset properly (use 'stty -F {port.device} min 0 time 0' to reset it)."
                    try:
                        #Check if no one else is using the serial port. Especially Minicom.
                        sttyOut = str(subprocess.check_output (f"stty -F {port.device} | grep min",
                                                               stderr=subprocess.STDOUT,shell=True),'utf-8')
                        sttyMatch = re.match(r"^.*min = (?P<vMin>\d+); time = (?P<vTime>\d+);$", sttyOut)
                        if ( (int(sttyMatch.group('vMin')) != 0) or (int(sttyMatch.group('vTime')) != 0)):
                            warnAndLog (f"fpgaTarget: the UART {port.device} status is not as expected. {extraMsg}")
                    except Exception as exc:
                        warnAndLog (f"fpgaTarget: Failed to get the status of {port.device}. {extraMsg}",exc=exc)
                    return port.device

        logAndExit(f"findUartPort: Failed to find a UART port with expected VID:PID = {search_vid:X}:{search_pid:X}")

    @decorate.debugWrap
    def setupUart(self, timeout=1, baud=115200, parity="NONE",
        stopbits=2, bytesize=8):

        port = self.findUartPort()

        # Translate inputs into serial settings
        if hasattr(serial, f"PARITY_{parity.upper()}"):
            parity = getattr(serial, f"PARITY_{parity.upper()}")
        else:
            logAndExit(f"setupUart: parity {parity} must be even or odd")

        sbit_mapping = {1: serial.STOPBITS_ONE, 2: serial.STOPBITS_TWO}
        if stopbits in sbit_mapping:
            stopbits = sbit_mapping[stopbits]
        else:
            logAndExit(f"setupUart: stop bits {stopbits} must be 1 or 2")

        byte_mapping = {5: serial.FIVEBITS, 6: serial.SIXBITS, 7: serial.SEVENBITS, 8: serial.EIGHTBITS}
        if bytesize in byte_mapping:
            bytesize = byte_mapping[bytesize]
        else:
            logAndExit(f"setupUart: bytesize {bytesize} must be 5,6,7 or 8")

        # configure the serial connections
        try:
            self.uartSession = serial.Serial(
                port=port,
                baudrate=baud,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
                bytesize=bytesize
            )

            if not self.uartSession.is_open:
                self.uartSession.open()
        except Exception as exc:
            logAndExit(f"setupUart: unable to open serial session", exc=exc, exitCode=EXIT.Run)

    @decorate.debugWrap
    @decorate.timeWrap
    def setupGdbCustomScoring (self):
        for funcCheckpoint in getSettingDict('customizedScoring','funcCheckpoints'):
            retCommand = self.runCommandGdb (f"dprintf {funcCheckpoint},\"<GDB-CHECKPOINT>:{funcCheckpoint}\\n\"",
                erroneousContents="not defined", shutdownOnError=False)
            if (not retCommand[0]):
                warnAndLog (f"setupGdbCustomScoring: Failed to insert a checkpoint at {funcCheckpoint}."
                            f"See <{self.fGdbOut.name}> for more details.")
        if (getSettingDict('customizedScoring','memAddress') != -1):
            memAddress = getSettingDict('customizedScoring','memAddress')
            retCommand = self.runCommandGdb (f"display/x * (int *) 0x{memAddress:08x}",
                erroneousContents=['No symbol', 'warning'], shutdownOnError=False)
            if (not retCommand[0]):
                warnAndLog (f"setupGdbCustomScoring: Unexpecte output while reading 0x{memAddress:08x}."
                            f"See <{self.fGdbOut.name}> for more details.")
            else:
                self.runCommandGdb (f"watch * (int *) 0x{memAddress:08x}", shutdownOnError=False)
                setCmd = f"set * (int *) 0x{memAddress:08x} = {getSettingDict('customizedScoring','memResetValue')}"
                self.runCommandGdb (f"commands\n{setCmd}\nc\nend", shutdownOnError=False)

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
            self.interruptGdb ()
            
            # Analyze gdb output for FreeRTOS
            if (self.osImage=='FreeRTOS'):
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

        if ((self.target=='vcu118') and self.uartSession.is_open):
            try:
                logging.debug("Closing uart_session.")
                self.uartSession.close()
            except Exception as exc:
                warnAndLog(f"fpgaTearDown: unable to close the serial session", exc=exc,doPrint=False)

        if (stage > failStage.gdb):
            self.interruptGdb()
            self.gdbDetach()

        # quit openocd
        shellCommand(f"echo 'shutdown' | nc localhost {self.openocdPort}",check=False,shell=True)
        try:
            self.openocdProcess.expect(pexpect.EOF,timeout=10)
        except Exception as exc:
            warnAndLog("fpgaTearDown: Failed to shutdown the openocd process.",doPrint=False,exc=exc)

        # quit gdb
        if (stage > failStage.gdb):
            self.runCommandGdb("quit",endsWith=pexpect.EOF,shutdownOnError=False)

        filesToClose = [self.fGdbOut, self.fOpenocdOut]
        if (self.target=='vcu118'):
            processes = [('riscv64-unknown-elf-gdb',self.gdbProcess), ('openocd',self.openocdProcess)]
            for pName, proc in processes:
                try:
                    pID = os.getpgid(proc.pid)
                except Exception as exc:
                    warnAndLog(f"Can't get pgid. Process <{pName}> was already killed.",exc=exc,doPrint=False)
                    continue #process was already killed
                sudoShellCommand(['kill', '-9', f"{pID}"],check=False)
                sudoShellCommand(['pkill', '-9', f"{pName}"],check=False)
            if (isReload):
                filesToClose.append(self.fTtyOut)

        for xFile in filesToClose:
            if (xFile is None):
                continue
            try:
                xFile.close()
            except Exception as exc:
                warnAndLog(f"fpgaTearDown: Failed to close <{xFile.name}>.",doPrint=False,exc=exc)
