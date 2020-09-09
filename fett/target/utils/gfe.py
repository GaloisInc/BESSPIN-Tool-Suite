import shlex
import collections
import pipes

import pexpect
from pexpect import fdpexpect
import serial, subprocess
import serial.tools.list_ports

from fett.base.utils.misc import *

class Gfe(object):
    def __init__(self):
        self.gdbProcess = None 
        self.openocdProcess = None
        self.uart_session = None

        self.fGdbOut = None
        self.fOpenocdOut = None

        self.gdbPort = getSetting('gdbRemotePort')

    @decorate.debugWrap
    @decorate.timeWrap
    def gfeStart (self, elfPath, elfLoadTimeout=15):
        # setup UART
        self.setupUart()

        # start the openocd process
        openocdCfg = os.path.join(getSetting('repoDir'),'fett','target','utils','openocd_vcu118.cfg')
        self.fOpenocdOut = ftOpenFile(os.path.join(getSetting('workDir'),'openocd.out'), 'ab')

        try:
            self.openocdProcess = pexpect.spawn(
                f"openocd --command 'gdb_port {self.gdbPort}' -f {openocdCfg}",
                    logfile=self.fOpenocdOut, timeout=15, echo=False)
            self.openocdProcess.expect("telnet server disabled", timeout=15)
        except Exception as exc:
            self.shutdownAndExit(f"gfeStart: Failed to spawn the openocd process.",overwriteShutdown=True,exc=exc,exitCode=EXIT.Run)

        # start the gdb process
        self.fGdbOut = ftOpenFile(os.path.join(getSetting('workDir'), f'gdb.out'), 'wb')
        try:
            self.gdbProcess = pexpect.spawn(
                f"riscv64-unknown-elf-gdb {elfPath}",
                    logfile=self.fGdbOut, timeout=elfLoadTimeout, echo=False)
            self.gdbProcess.expect(self.getGdbEndsWith(), timeout=elfLoadTimeout)
        except Exception as exc:
            self.shutdownAndExit(f"gfeStart: Failed to spawn the openocd process.",overwriteShutdown=True,exc=exc,exitCode=EXIT.Run)

        # configure gdb
        self.runCommandGdb("set confirm off")
        self.runCommandGdb("set width 0")
        self.runCommandGdb("set height 0")
        self.runCommandGdb("set print entry-values no")
        self.runCommandGdb("set remotetimeout 60")
        self.runCommandGdb(f"set architecture riscv:rv{getSetting('xlen')}")
        self.runCommandGdb("define hook-continue\ndont-repeat\nend") #we don't want to 'continue' on extra presses due to encoding and such

        self.gdbConnect()

        # reset the board
        self.softReset()

        # start the tty process
        self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),'tty.out'),'ab')
        self.ttyProcess = fdpexpect.fdspawn(self.uart_session.fileno(),logfile=self.fTtyOut,timeout=30)
        self.process = self.ttyProcess

        # gdbContinue
        self.runCommandGdb("load",timeout=elfLoadTimeout,erroneousContents="failed", expectedContents="Transfer rate")
        self.expectOnOpenocd (f"Disabling abstract command writes to CSRs.","load")
        self.runCommandGdb('c', endsWith='Continuing')

        return
   
    @decorate.debugWrap
    @decorate.timeWrap
    def gdbConnect (self):
        self.runCommandGdb(f"target remote localhost:{self.gdbPort}")
        self.expectOnOpenocd (f"accepting 'gdb' connection on tcp/{self.gdbPort}","connect")

    @decorate.debugWrap
    @decorate.timeWrap
    def softReset (self, isRepeated=False):
        # reset hart
        if (isEqSetting('xlen',32)):
            self.riscvWrite(int("0x6FFF0000", base=16),1,32) # set *(0x6fff0000)=1
        elif (isEqSetting('xlen',64)):
            self.runCommandGdb("set $a0 = 0")
            self.runCommandGdb("set $a1 = 0x70000020")
        self.expectOnOpenocd ("unexpectedly reset!","softReset")

        # disconnect from gdb
        self.runCommandGdb("disconnect")
        self.expectOnOpenocd ("dropped 'gdb' connection","disconnect")

        # Re-connect
        self.gdbConnect()

        if ((not isRepeated) and isEqSetting('osImage','FreeRTOS')):
            if (isEqSetting('procFlavor','bluespec')):
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
            "set *(({} *) 0x{:x}) = 0x{:x}".format(
                size_options[size], address, value), erroneousContents="Cannot access memory")

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
                                process=self.gdbProcess, **kwargs)[1]

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
                    printAndLog(f"fpgaTarget: located UART device ats {port.device} "
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
                    except:
                        warnAndLog (f"fpgaTarget: failed to get the status of {port.device}. {extraMsg}")
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
            self.uart_session = serial.Serial(
                port=port,
                baudrate=baud,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
                bytesize=bytesize
            )

            if not self.uart_session.is_open:
                self.uart_session.open()
        except Exception as exc:
            logAndExit(f"setupUart: unable to open serial session", exc=exc, exitCode=EXIT.Run)

    @decorate.debugWrap
    @decorate.timeWrap
    def gfeTearDown (self):
        if (self.uart_session.is_open):
            try:
                self.uart_session.close()
            except Exception as exc:
                warnAndLog(f"gfeTearDown: unable to close the serial session", exc=exc,doPrint=False)

        self.interruptGdb()
        self.runCommandGdb("detach")

        try:
            self.openocdProcess.terminate() 
        except Exception as exc:
            warnAndLog("gfeTearDown: Failed to kill the openocd process.",doPrint=False,exc=exc)

        self.runCommandGdb("quit",endsWith=pexpect.EOF)

        processes = ['riscv64-unknown-elf-gdb', 'openocd']
        for proc in processes:
            sudoShellCommand(['pkill', '-9', f"{proc}"],check=False)

        filesToClose = [self.fTtyOut, self.fGdbOut, self.fOpenocdOut]
        for xFile in filesToClose:
            if (xFile is None):
                continue
            try:
                xFile.close()
            except Exception as exc:
                warnAndLog(f"targetTearDown: Failed to close <{xFile.name}>.",doPrint=False,exc=exc)
