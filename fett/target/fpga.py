#! /usr/bin/env python3
""" 
Main fpga class + misc fpga functions
"""

from fett.base.utils.misc import *
from fett.target.common import *
from fett.target.gfe import Gfe

import subprocess, psutil, tftpy
import sys, signal, os, socket, time, hashlib
import pexpect

class fpgaTarget (commonTarget, Gfe):
    def __init__ (self):

        commonTarget.__init__(self)
        Gfe.__init__(self)

        self.ipTarget = getSetting('fpgaIpTarget')
        self.ipHost = getSetting('fpgaIpHost')  
        self.portTarget = getSetting('fpgaPortTarget')
        self.portHost = getSetting('fpgaPortHost')

        # Important for the Web Server
        self.httpPortTarget  = getSetting('HTTPPortTarget')
        self.httpsPortTarget = getSetting('HTTPSPortTarget')
        self.votingHttpPortTarget  = getSetting('VotingHTTPPortTarget')
        self.votingHttpsPortTarget = getSetting('VotingHTTPSPortTarget')

        return

    @decorate.debugWrap
    @decorate.timeWrap
    def boot(self,endsWith="login:",timeout=90):

        if (getSetting('osImage') in ['debian', 'FreeBSD', 'busybox']):
            if (isEqSetting('elfLoader','JTAG')):
                self.gfeStart(getSetting('osImageElf'))
            elif (isEqSetting('elfLoader','netboot')):
                self.gfeStart(getSetting('netbootElf'))
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
            self.gfeStart(getSetting('osImageElf')) 
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
        self.gfeTearDown()
        return True

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

#--- END OF CLASS fpgaTarget------------------------------

@decorate.debugWrap
@decorate.timeWrap
def programBitfile (doPrint=True):
    printAndLog("Preparing the FPGA environment...",doPrint=False)
    clearProcesses()
    gfeOut = ftOpenFile(os.path.join(getSetting('workDir'),'gfe.out'),'a')
    printAndLog("Clearing the flash...",doPrint=False)
    gfeOut.write("\n\ngfe-clear-flash\n")
    try:
        subprocess.check_call(['gfe-clear-flash'],stdout=gfeOut,stderr=gfeOut,timeout=90)
    except Exception as exc:
        errorAndLog(f"<gfe-clear-flash> has failed. Will continue anyway.",doPrint=False,exc=exc)

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

    printAndLog("Programming the bitfile...",doPrint=False)
    nAttempts = 2
    for iAttempt in range(nAttempts):
        gfeOut.write("\n\ngfe-program-fpga\n")
        clearProcesses()
        try:
            subprocess.check_call(['gfe-program-fpga', getSetting('processor'), '--bitstream', bitAndProbefiles[0], '--probe-file', bitAndProbefiles[1]],stdout=gfeOut,stderr=subprocess.STDOUT,timeout=90)
            printAndLog(f"Programmed bitfile {bitAndProbefiles[0]} (md5: {md5.hexdigest()})",doPrint=False)
            break
        except Exception as exc:
            if (iAttempt < nAttempts-1):
                errorAndLog(f"Failed to program the FPGA. Trying again...",doPrint=True,exc=exc)
            else:
                logAndExit(f"Failed to program the FPGA.",exc=exc,exitCode=EXIT.Run)

    gfeOut.close()
    printAndLog("FPGA was programmed successfully!",doPrint=False)

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
