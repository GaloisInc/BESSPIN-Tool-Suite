#! /usr/bin/env python3
""" 
Main fpga class + misc fpga functions
"""

from fett.base.utils.misc import *
from fett.target.common import *
from fett.target.utils.gfe import Openocd

import subprocess, psutil, tftpy
import sys, signal, os, socket, time, hashlib
import pexpect
from pexpect import fdpexpect

import serial
import serial.tools.list_ports



class fpgaTarget (commonTarget):
    def __init__ (self):

        super().__init__()

        self.ipTarget = getSetting('fpgaIpTarget')
        self.ipHost = getSetting('fpgaIpHost')  
        self.portTarget = getSetting('fpgaPortTarget')
        self.portHost = getSetting('fpgaPortHost')

        # Important for the Web Server
        self.httpPortTarget  = getSetting('HTTPPortTarget')
        self.httpsPortTarget = getSetting('HTTPSPortTarget')
        self.votingHttpPortTarget  = getSetting('VotingHTTPPortTarget')
        self.votingHttpsPortTarget = getSetting('VotingHTTPSPortTarget')

        self.gfeOutPath = os.path.join(getSetting('workDir'),'gfe.out')
        self.gdbOutPath = os.path.join(getSetting('workDir'),'gdb.out')

        self.gdb_session = None
        self.gdb_logfile = None
        self.uart_session = None
        return

    def terminateGfe(self):
        if not self.gdb_session:
            return
        self.interruptGdb()
        self.runCommandGdb("disassemble", ops=20)
        self.runCommandGdb("info registers all", ops=100)
        self.runCommandGdb("flush regs")
        self.runCommandGdb("info threads", ops=100)

    @decorate.debugWrap
    @decorate.timeWrap
    def boot(self,endsWith="login:",timeout=90):
        
        @decorate.debugWrap
        def loadJTAG(binary): 
            if (getSetting('osImage') not in ['debian', 'FreeBSD', 'busybox', 'FreeRTOS']):
                self.shutdownAndExit(f"<loadJTAG> is not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",exitCode=EXIT.Dev_Bug)
            if (isEqSetting('osImage','FreeRTOS')):
                if (isEqSetting('procFlavor','bluespec')):
                    print(self.softReset())
                print(self.interruptGdb())
            elif (getSetting('osImage') in ['debian', 'FreeBSD', 'busybox']):
                #The following values are hardcoded as copied from GFE. When GFE updates the testing platform, we'll change this accordingly
                #This soft resets the processor
                self.runCommandGdb("set $a0 = 0")
                self.runCommandGdb("set $a1 = 0x70000020")
            self.setupUart()
            # setup process over uart_session object
            self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),'tty.out'),'ab')
            self.ttyProcess = fdpexpect.fdspawn(self.uart_session.fileno(),logfile=self.fTtyOut,timeout=30)
            self.process = self.ttyProcess
            self.runCommandGdb(f"file {binary}")
            self.loadGdb(False) #has some asserts. False not to verify compare-sections and MIS.
            self.continueGdb(wait=False)

        # start GDB process(es)
        self.startGdb()

        # reset the board
        self.softReset()

        if (getSetting('osImage') in ['debian', 'FreeBSD', 'busybox']):
            if (isEqSetting('elfLoader','JTAG')):
                loadJTAG(getSetting('osImageElf'))
            elif (isEqSetting('elfLoader','netboot')):
                loadJTAG(getSetting('netbootElf'))
            else:
                self.shutdownAndExit (f"boot: ELF loader <{getSetting('elfLoader')}> not implemented.",overwriteShutdown=True,exitCode=EXIT.Dev_Bug)

            if (isEqSetting('elfLoader','netboot')):
                self.expectFromTarget('>',"Starting netboot loader",timeout=60)
                dirname, basename = os.path.split(os.path.abspath(getSetting('osImageElf')))
                listenPort = None
                rangeStart = getSetting('netbootPortRangeStart')
                rangeEnd = getSetting('netbootPortRangeEnd')
                if (rangeStart > rangeEnd):
                    self.shutdownAndExit(f"boot: The netboot port range {rangeStart}-{rangeEnd} is too small. Please choose a wider range.", overwriteShutdown=True,exitCode=EXIT.Configuration)
                for i in range(rangeStart, rangeEnd+1):
                    if (checkPort(i, self.ipHost)):
                        listenPort = i
                if listenPort is None:
                    self.shutdownAndExit(f"boot: Could not find open ports in the range {rangeStart}-{rangeEnd}. Please choose another range.",exitCode=EXIT.Network)
                try:
                    #Need to divert the tftpy logging. Otherwise, in case of debug (`-d`), our logging will get smothered.
                    logging.getLogger('tftpy').propagate = False
                    logging.getLogger('tftpy').addHandler(logging.FileHandler(os.path.join(getSetting('workDir'),'tftpy.log'),'w'))
                    server = tftpy.TftpServer(dirname)
                except Exception as exc:
                    self.shutdownAndExit(f"boot: Could not create TFTP server for netboot.", exc=exc,overwriteShutdown=True,exitCode=EXIT.Run)

                serverThread = threading.Thread(target=server.listen, kwargs={'listenip': self.ipHost, 'listenport': listenPort})
                serverThread.daemon = True
                getSetting('trash').throwThread(serverThread, "TFTP server listening on host for netboot")
                serverThread.start()
                printAndLog (f"Started TFTP server on port {listenPort}.",doPrint=False)
                time.sleep(1)
                self.sendToTarget(f"boot -p {listenPort} {self.ipHost} {basename}\r\n")

            time.sleep(1)
            self.expectFromTarget(endsWith,"Booting",timeout=timeout)

            if (isEqSetting('elfLoader','netboot')):
                server.stop()
                serverThread.join(timeout=30)
                if (serverThread.is_alive()):
                    # It isn't a fatal error if the server doesn't shut down, since we already know booting has succeeded.
                    warnAndLog(f"boot: TFTP server thread still running after attempted shutdown.",doPrint=False)

            # onlySsh happens here
            # starting prompt is still '#'
            if (self.onlySsh):
                if (not self.openSshConn(endsWith="\r\n#")):
                    self.shutdownAndExit("Boot: In <onlySsh> mode, and failed to open SSH.")

        elif (isEqSetting('osImage','FreeRTOS')):
            loadJTAG(getSetting('osImageElf')) 
            time.sleep(1)
            self.expectFromTarget(endsWith,"Booting",timeout=timeout)
        else:
            self.shutdownAndExit(f"<boot> is not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.")

    @decorate.debugWrap
    @decorate.timeWrap
    def activateEthernet (self):
        if self.onlySsh:
            return ''
        if (isEqSetting('osImage','debian')):
            self.runCommand ("echo \"auto eth0\" > /etc/network/interfaces")
            self.runCommand ("echo \"iface eth0 inet static\" >> /etc/network/interfaces")
            self.runCommand (f"echo \"address {self.ipTarget}/24\" >> /etc/network/interfaces")
            self.runCommand(f"ip route add default via {self.ipHost}")
            outCmd = self.runCommand ("ifup eth0",endsWith=['rx/tx','off'],expectedContents=['Link is Up'])
        elif (isEqSetting('osImage','busybox')):
            time.sleep(1)
            self.runCommand ("ifconfig eth0 up",endsWith=['rx/tx','off'],expectedContents=['Link is Up'],timeout=20)
            outCmd = self.runCommand (f"ip addr add {self.ipTarget}/24 dev eth0",timeout=20)
        elif (isEqSetting('osImage','FreeRTOS')):
            outCmd = self.runCommand("isNetworkUp",endsWith="<NTK-READY>",erroneousContents="(Error)",timeout=30)
        elif (isEqSetting('osImage','FreeBSD')):
            self.runCommand(f"route add default {self.ipHost}")
            outCmd = self.runCommand (f"ifconfig xae0 inet {self.ipTarget}/24",timeout=60)
        else:
            self.shutdownAndExit(f"<activateEthernet> is not implemented for<{getSetting('osImage')}> on <{getSetting('target')}>.")

        self.pingTarget()

        if (isEqSetting('osImage','FreeBSD')): #use ssh instead of JTAG
            self.openSshConn()
        return outCmd

    @decorate.debugWrap
    def targetTearDown(self):
        def kill_process(proc):
            if (self.process.isalive()):
                try:
                    subprocess.check_call(['sudo', 'kill', '-9', f"{proc.pid}"],
                                          stdout=self.fTtyOut, stderr=self.fTtyOut)
                except Exception as exc:
                    warnAndLog("targetTearDown: Failed to kill process.",doPrint=False,exc=exc)
        try:
            self.terminateGfe()
            kill_process(self.gdb_session)
            kill_process(self.uart_session)
            return True
        except Exception as exc:
            warnAndLog ("targetTearDown: Failed to tearDown peacefully.",doPrint=False,exc=exc)
            return False

    @decorate.debugWrap
    def interact (self):
        #This method gives the control back to the user
        # could not use "pexpect.spawn.interact" as "fdpexpect.spawn" does not have the method
        if (self.inInteractMode):
            return #avoid recursive interact mode
        self.inInteractMode = True
        if (self.isSshConn): #only interact on the JTAG
            self.closeSshConn()
        if (isEqSetting('osImage','FreeRTOS')):
            printAndLog (f"FreeRTOS is left running on target. Enter \"--exit + Enter\" to exit.")
        else:
            printAndLog (f"Entering pseudo-interactive mode. Root password: \'{self.rootPassword}\'. Enter \"--exit + Enter\" to exit.")
            printAndLog ("Please use \"--ctrlc\" for interrupts. (Ctrl-C would exit the whole FETT tool).")
        if (self.userCreated):
            if isEnabled("useCustomCredentials"):
                # Log out to prompt user to log in using their credentials.
                # We can't log in for them because we only have the hash of
                # their password
                output = self.runCommand("exit", endsWith="login:")[1]
                printAndLog("Note that there is another user.  User name: "
                            f"\'{self.userName}\'")
                printAndLog("Please log in using the credentials you supplied")

                # Print login prompt from OS.  Drop the first 2 lines because
                # those contain the exit / logout messages from running the
                # `exit` command
                print("\n".join(output.split("\n")[2:]), end="")
            else:
                printAndLog (f"Note that there is another user. User name: \'{self.userName}\'. Password: \'{self.userPassword}\'.")
                printAndLog ("Now the shell is logged in as: \'{0}\'.".format('root' if self.isCurrentUserRoot else self.userName))
        
        def keepReadingFromFdpexpect (stopEvent=None,timeStep=5):
            if (stopEvent is None):
                errorAndLog ("interact: Failed to read from target. StopEvent is None.")
                return
            while (not stopEvent.is_set()):
                try:
                    textBack = self.process.read_nonblocking(timeout=timeStep)
                    sys.stdout.write(str(textBack,'utf-8'))
                    sys.stdout.flush()
                except pexpect.TIMEOUT:
                    logging.debug("interactiveMode: timeout in keepReadingFromFdpexpect.")
                except Exception as exc:
                    errorAndLog ("interact: Failed to read from target.",exc=exc)
                    return

        stopReading = threading.Event() #event to stop the reading process in the end
        readThread = threading.Thread(target=keepReadingFromFdpexpect, kwargs=dict(timeStep=5,stopEvent=stopReading))
        readThread.daemon = True
        getSetting('trash').throwThread(readThread,"Interact reading thread")
        stopReading.clear() #the event that controls the interactive mode keepReadingFromFdpexpect
        readThread.start() #start the reading thread
        exitTerminal = False
        while ((not exitTerminal) and readThread.is_alive()):
            try:
                instruction = input ("")
            except Exception as exc:
                warnAndLog(f"Invalid Command. Please use interpreter commands such as \'--ctrlc\' and \'--exit\' instead of direct interrupts.",exc=exc)
                sys.stdout.flush()
                continue
            if (instruction == '--exit'): #exit
                exitTerminal = True
            elif (instruction == '--ctrlc'):
                self.sendToTarget(b'\x03\r\n',shutdownOnError=False)
            elif (('shutdown' in instruction) or ('poweroff' in instruction) or ('halt' in instruction)):
                warnAndLog ("Please use \'--exit\' instead of direct shutting down command.")
                self.sendToTarget(" ",shutdownOnError=False)
            else:
                self.sendToTarget(instruction,shutdownOnError=False)
                time.sleep(1)

        stopReading.set()
        time.sleep(5)
        return

    # ------ Gdb Methods -----
    def runCommandGdb(self, command, ops=1, **kwargs):
        """convenience runCommand for GDB"""
        return self.runCommand(command, endsWith=[r"\r\n\(gdb\)"],
                                sendToNonUnix=True,
                                timeout=ops*60,
                                process=self.gdb_session, **kwargs)[1]

    @decorate.debugWrap
    def continueGdb(self, wait=True, asynch=False):
        """implement wait/no-wait, synch/asynch GDB continue"""
        asynch = "&" if asynch else ""
        ops = 10
        if wait:
            return self.runCommandGdb('c' + asynch, expectedContents='Continuing', ops=ops)
        else:
            return self.runCommand('c' + asynch,
                                   timeout=ops * 60,
                                   endsWith=["Continuing"],
                                   sendToNonUnix=True,
                                   process=self.gdb_session)[1]

    @decorate.debugWrap
    def loadGdb(self, verify=True):
        """implement GDB load command"""
        output = self.runCommandGdb("load", ops=1000, erroneousContents="failed", expectedContents="Transfer rate")
        if verify:
            output = self.runCommandGdb("compare-sections", ops=1000, expectedContent="MIS")
        return output

    @decorate.debugWrap
    def interruptGdb(self):
        """implement keyboardInterrupt for GDB"""
        self.gdb_session.send("\003")
        self.gdb_session.expect("(gdb)", timeout=6000)
        return self.gdb_session.before.strip()

    @decorate.debugWrap
    def startGdb(self, binary=None):
        server_cmd = getSettingDict("gfeInfo", "openocdCommand")
        config = getSettingDict("gfeInfo", "openocdCfgPath")
        riscv_gdb_cmd = getSettingDict("gfeInfo", "gdbPath")
        self.openocd_session = Openocd(
            server_cmd=server_cmd,
            config=config,
            debug=False)
        port = self.openocd_session.gdb_ports[0]
        self.gdb_logfile = ftOpenFile(os.path.join(getSetting('workDir'), f'gdb.out'), 'ab')
        self.gdb_session = pexpect.spawn(riscv_gdb_cmd, logfile=self.gdb_logfile, timeout=30)
        self.gdb_session.expect(r"\r\n\(gdb\)")
        self.runCommandGdb("set confirm off")
        self.runCommandGdb("set width 0")
        self.runCommandGdb("set height 0")
        self.runCommandGdb("set print entry-values no")
        self.runCommandGdb(f"set remotetimeout %d" % 60)
        self.runCommandGdb("set architecture riscv:rv%d" % getSetting('xlen'))
        self.runCommandGdb("target extended-remote localhost:%d" % port)
        if binary:
            self.runCommandGdb("file %s" % binary)

    def endGdb(self):
        self.openocd_session.tearDown()

    def riscvWrite(self, address, value, size):
        size_options = {8: "char", 32: "int"}

        # Validate input
        if size not in size_options:
            logAndExit(f"fpgaTarget: riscvWrite write size {size} must be one of {list(size_options.keys())}")

        if not self.gdb_session:
            self.startGdb()

        # Perform the write command using the gdb set command
        self.runCommandGdb(
            "set *(({} *) 0x{:x}) = 0x{:x}".format(
                size_options[size], address, value), erroneousContents="Cannot access memory")

    @decorate.debugWrap
    def softReset(self):
        self.riscvWrite(int(getSettingDict("gfeInfo", "resetBase"), base=16),
                        int(getSettingDict("gfeInfo", "resetVal"), base=16),
                        32)
        self.endGdb()
        self.startGdb()
        # Note: There is a bug that prevents loading an elf later in the test script
        # without first continuing and interrupting. This is fine for now, but may
        # not be compatible with future tests that require a completely clean start point
        self.continueGdb(wait=False)
        self.interruptGdb()

    # ------ Uart Methods -----
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
        logAndExit(f"fpgaTarget: findUartPort could not find a UART port with expected VID:PID = {search_vid:X}:{search_pid:X}")

    @decorate.debugWrap
    def setupUart(self, timeout=1, baud=115200, parity="NONE",
        stopbits=2, bytesize=8):

        port = getSettingDict("gfeInfo", "uartSerialDev")

        # Get the UART port
        if port == "auto":
            port = self.findUartPort()

        # Translate inputs into serial settings
        if hasattr(serial, f"PARITY_{parity.upper()}"):
            parity = getattr(serial, f"PARITY_{parity.upper()}")
        else:
            logAndExit(f"fpgaTarget: setupUart parity {parity} must be even or odd")

        sbit_mapping = {1: serial.STOPBITS_ONE, 2: serial.STOPBITS_TWO}
        if stopbits in sbit_mapping:
            stopbits = sbit_mapping[stopbits]
        else:
            logAndExit(f"fpgaTarget: setupUart stop bits {stopbits} must be 1 or 2")

        byte_mapping = {5: serial.FIVEBITS, 6: serial.SIXBITS, 7: serial.SEVENBITS, 8: serial.EIGHTBITS}
        if bytesize in byte_mapping:
            bytesize = byte_mapping[bytesize]
        else:
            logAndExit(f"fpgaTarget: setupUart bytesize {bytesize} must be 5,6,7 or 8")

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
            logAndExit(f"fpgaTarget: unable to open serial session", exc=exc)

#--- END OF CLASS fpgaTarget------------------------------

def programFpga(bitStream, probeFile, attempts=2):
    """programs the fpga with a given bitstream and probe file
    matches the functionality of gfe-program-fpga
    :param bitStream: valid filepath
    :param probeFile: valid probe file
    """
    # top level params
    vivado = 'vivado_lab'
    sourceDir = os.path.join(getSetting('repoDir'), 'fett', 'target', 'utils')
    cwd = os.path.join(getSetting('workDir'), 'gfe')

    # copy files over to workDir
    cp(os.path.join(sourceDir, 'tcl', 'prog_bit.tcl'), cwd)

    # check that the input files exist
    if not os.path.exists(bitStream):
        logAndExit(f"programFpga: bitstream file {bitStream} does not exist")
    if not os.path.exists(probeFile):
        logAndExit(f"programFpga: probe file {probeFile} does not exist")

    # run tcl files to program the bitstreams, and clean up output
    retProc = shellCommand([vivado,'-nojournal','-notrace','-nolog','-source','./prog_bit.tcl',
            '-mode','batch','-tclargs',bitStream, probeFile],timeout=90,cwd=cwd,check=False)
    if retProc.returncode != 0:
        if attempts > 0:
            errorAndLog(f"programFpga: failed to program the FPGA. Trying again...",doPrint=True)
            programFpga(bitStream, probeFile, attempts=attempts-1)
        else:
            logAndExit(f"programFpga: failed to program the FPGA.",exitCode=EXIT.Run)


def clearFlash(attempts=2):
    """ clear flash memory on Fpga
    matches the functionality of gfe-clear-flash
    """
    sourceDir = os.path.join(getSetting('repoDir'), 'fett', 'target', 'utils', 'tcl')
    cwd = os.path.join(getSetting('workDir'), 'gfe')

    # copy files over to workDir
    cp(os.path.join(sourceDir, 'program_flash'), cwd)
    cp(os.path.join(sourceDir, 'small.bin'), cwd)

    # "normal" operation exits code 1, so check=False
    retProc = shellCommand(['./program_flash', 'datafile', './small.bin'],timeout=90,check=False,cwd=cwd)
    if retProc.returncode != 1:
        if attempts > 0:
            errorAndLog(f"clearFlash: failed to clear flash. Trying again...",doPrint=True)
            clearFlash(attempts=attempts-1)
        else:
            logAndExit(f"programFpga: failed to clear flash for the FPGA.",exitCode=EXIT.Run)

@decorate.debugWrap
@decorate.timeWrap
def programBitfile ():
    printAndLog("Preparing the FPGA environment...")
    clearProcesses()
    gfeOut = ftOpenFile(os.path.join(getSetting('workDir'),'gfe.out'),'a')
    gfeDir = os.path.join(getSetting('workDir'), 'gfe')
    if not os.path.exists(gfeDir):
        mkdir (gfeDir)

    printAndLog("Clearing the flash...",doPrint=False)
    gfeOut.write("\n\ngfe-clear-flash\n")
    clearFlash()

    bitAndProbefiles = selectBitAndProbeFiles()
    for xFile in bitAndProbefiles:
        if not os.path.isfile(xFile):
            logAndExit(f"<{xFile}> does not exist.", exitCode=EXIT.Files_and_paths)

    try:
        bitfile = ftOpenFile(bitAndProbefiles[0], "rb")
        md5 = hashlib.md5()
        while True:
            chunk = bitfile.read(65536)
            if not chunk:
                break
            md5.update(chunk)
        bitfile.close()
    except Exception as exc:
        logAndExit(f"Could not compute md5 for file <{bitAndProbefiles[0]}>.", exc=exc, exitCode=EXIT.Run)

    printAndLog("Programming the bitfile...")
    programFpga(*bitAndProbefiles)
    printAndLog(f"Programmed bitfile {bitAndProbefiles[0]} (md5: {md5.hexdigest()})")

    gfeOut.close()
    printAndLog("FPGA was programmed successfully!")

@decorate.debugWrap
def selectBitAndProbeFiles ():
    bitfileName = "soc_" + getSetting('processor') + ".bit"
    probfileName = "soc_" + getSetting('processor') + ".ltx"

    if getSetting('useCustomProcessor'):
        bitfileDir = getSetting('pathToCustomProcessorSource')
    else:
        useNix = False
        # If source is GFE, we check the nix environment for latest bitfiles
        if getSetting('binarySource') == 'GFE':
            envBitfileDir = getSettingDict('nixEnv', ['gfeBitfileDir'])
            if envBitfileDir in os.environ:
                bitfileDir = os.environ[envBitfileDir]
                useNix = True
            else:
                printAndLog(f"Could not find bitfileDir for <{getSetting('processor')}> in nix environment. Falling back to binary repo.", doPrint=False)
        if (not useNix): #use binaries repo
            bitfileDir = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'), 'bitfiles', 'fpga')
    
    return (os.path.join(bitfileDir, bitfileName),os.path.join(bitfileDir, probfileName))

@decorate.debugWrap
def checkEthAdaptorIsUp ():
    try:
        return psutil.net_if_stats()[getSetting('ethAdaptor')].isup
    except Exception as exc:
        logAndExit (f"fpga.checkEthAdaptorIsUp: Failed to check that <{getSetting('ethAdaptor')}> is up.",exc=exc,exitCode=EXIT.Network)

@decorate.debugWrap
def getAddrOfAdaptor (ethAdaptor,addrType,exitIfNoAddr=True):
    
    def noAddrFound(errMessage):
        if (exitIfNoAddr):
            logAndExit(f"fpga.getAddrOfAdaptor: Failed to {errMessage}. Please check the network configuration.",exitCode=EXIT.Network)
        else:
            printAndLog(f"fpga.getAddrOfAdaptor: Failed to {errMessage}.",doPrint=False)
            return 'NotAnAddress'

    if (addrType == 'MAC'):
        family = psutil.AF_LINK
    elif (addrType == 'IP'):
        family = socket.AF_INET
    else:
        logAndExit (f"fpga.getAddrOfAdaptor: Unrecognized address type <{addrType}> is up.",exitCode=EXIT.Dev_Bug)
    
    if (ethAdaptor not in psutil.net_if_addrs()):
        return noAddrFound(f"find the adaptor <{ethAdaptor}>")
    
    for addr in psutil.net_if_addrs()[ethAdaptor]:
        if (addr.family == family):
            printAndLog(f"fpga.getAddrOfAdaptor: <{addrType} address> of <{ethAdaptor}> = <{addr.address}>",doPrint=False)
            return addr.address

    return noAddrFound(f"get the <{addrType} address> of <{ethAdaptor}>")

@decorate.debugWrap
def resetEthAdaptor ():
    #get the name and check configuration if this is the first time called
    if (not doesSettingExist('ethAdaptor')):
        ethAdaptor= getSetting('fpgaEthAdaptorName')
        if (getAddrOfAdaptor(ethAdaptor,'MAC') != getSetting('fpgaEthAdaptorMacAddress')):
            logAndExit(f"checkEthAdaptorConfiguration: <{ethAdaptor}> does not have the expected mac address <{getSetting('fpgaEthAdaptorMacAddress')}>. Please check the network configuration.",exitCode=EXIT.Network)
        #Set the adaptor's name
        setSetting('ethAdaptor',ethAdaptor)
        printAndLog (f"<{getSetting('ethAdaptor')}> exists and its MAC address is properly configured.",doPrint=False)

    #make the link go down, then up
    sudoPromptPrefix = f"You need sudo privileges to reset the ethernet adaptor: "
    commands = [
                ['ip', 'addr', 'flush', 'dev', getSetting('ethAdaptor')],
                ['ip','link','set', getSetting('ethAdaptor'), 'down'],
                ['ip','link','set', getSetting('ethAdaptor'), 'up']
            ]
    nAttempts = 3
    isReset = False
    for iAttempt in range(nAttempts):
        for command in commands:
            sudoShellCommand(command,sudoPromptPrefix)
            time.sleep(1)
        time.sleep(2)
        isReset = checkEthAdaptorIsUp ()
        if (isReset):
            #check that the IP address is properly set
            if (getAddrOfAdaptor(getSetting('ethAdaptor'),'IP',exitIfNoAddr=False) == getSetting('fpgaIpHost')):
                break
            else:
                printAndLog (f"fpga.resetEthAdaptor: <{getSetting('ethAdaptor')}> is up, but it does not have the right IP. Will try to assign it.",doPrint=False)
                sudoShellCommand(['ip','addr','add',f"{getSetting('fpgaIpHost')}/24",'dev',getSetting('ethAdaptor')],sudoPromptPrefix)
                time.sleep(3)
                isReset = checkEthAdaptorIsUp ()
                if (isReset):
                    break

        if ((not isReset) and (iAttempt < nAttempts - 1)):
            printAndLog (f"fpga.resetEthAdaptor: Failed to reset <{getSetting('ethAdaptor')}>. Trying again...",doPrint=False)
            time.sleep(3)

    if (not isReset):
        logAndExit (f"fpga.resetEthAdaptor: Failed to reset <{getSetting('ethAdaptor')}>.",exitCode=EXIT.Network)

    printAndLog (f"fpga.resetEthAdaptor: <{getSetting('ethAdaptor')}> is properly reset.",doPrint=False)

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
