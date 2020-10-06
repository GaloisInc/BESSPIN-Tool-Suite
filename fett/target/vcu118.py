#! /usr/bin/env python3
""" 
Main vcu118 class + misc vcu118 functions
"""

from fett.base.utils.misc import *
from fett.target.common import *
from fett.target.fpga import fpgaTarget
from fett.target.build import getTargetIp

import subprocess, psutil, tftpy
import sys, signal, os, socket, time, hashlib
import pexpect

class vcu118Target (fpgaTarget, commonTarget):
    def __init__ (self, targetId=None):

        commonTarget.__init__(self, targetId=targetId)
        fpgaTarget.__init__(self, targetId=targetId)

        self.osImageElf = getSetting('osImageElf',targetId=self.targetId)

        self.ipHost = getSetting('vcu118IpHost')
        self.ipTarget = getTargetIp(targetId=targetId)

        #Reloading till the network is up
        self.freertosNtkRetriesMax = 3
        self.freertosNtkRetriesIdx = 0
        #Reloading till the fpga starts
        self.fpgaStartRetriesMax = 3
        self.fpgaStartRetriesIdx = 0
        #Retrying to boot bluespec_p3
        self.bluespec_p3BootAttemptsMax = 5
        self.bluespec_p3BootAttemptsIdx = 0

        return

    @decorate.debugWrap
    @decorate.timeWrap
    def boot(self,endsWith="login:",timeoutDict={"elfLoad":90, "boot":90}):
        timeout = self.parseBootTimeoutDict(timeoutDict)
        if (self.osImage in ['debian', 'FreeBSD', 'busybox']):
            if (self.elfLoader=='JTAG'):
                elfLoadTimeout = self.parseBootTimeoutDict(timeoutDict,key="elfLoad")
                self.fpgaStart(self.osImageElf,elfLoadTimeout=elfLoadTimeout)
            elif (self.elfLoader=='netboot'):
                self.fpgaStart(getSetting('netbootElf',targetId=self.targetId),elfLoadTimeout=30)
            else:
                self.shutdownAndExit (f"boot: ELF loader <{self.elfLoader}> not implemented.",overwriteShutdown=True,exitCode=EXIT.Dev_Bug)

            if (self.elfLoader=='netboot'):
                self.expectFromTarget('>',"Starting netboot loader",timeout=60)
                dirname, basename = os.path.split(os.path.abspath(self.osImageElf))
                listenPort = self.findPort(portUse='netboot')
                printAndLog(f"{self.targetIdInfo}boot: netboot port is <{listenPort}>.")
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

            if (self.elfLoader=='netboot'):
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

        elif (self.osImage=='FreeRTOS'):
            self.fpgaStart(self.osImageElf,elfLoadTimeout=60) 
            time.sleep(1)
            self.expectFromTarget(endsWith,"Booting",timeout=timeout)
        else:
            self.shutdownAndExit(f"<boot> is not implemented for <{self.osImage}> on <{self.target}>.")

    @decorate.debugWrap
    @decorate.timeWrap
    def activateEthernet (self):
        if self.onlySsh:
            return ''
        if (self.osImage=='debian'):
            self.runCommand ("echo \"auto eth0\" > /etc/network/interfaces")
            self.runCommand ("echo \"iface eth0 inet static\" >> /etc/network/interfaces")
            self.runCommand (f"echo \"address {self.ipTarget}/24\" >> /etc/network/interfaces")
            self.runCommand(f"ip route add default via {self.ipHost}")
            outCmd = self.runCommand ("ifup eth0",endsWith=['rx/tx','off'],expectedContents=['Link is Up'])
        elif (self.osImage=='busybox'):
            time.sleep(1)
            self.runCommand ("ifconfig eth0 up",endsWith=['rx/tx','off'],expectedContents=['Link is Up'],timeout=20)
            outCmd = self.runCommand (f"ip addr add {self.ipTarget}/24 dev eth0",timeout=20)
        elif (self.osImage=='FreeRTOS'):
            isSuccess = False
            while ((not isSuccess) and (self.freertosNtkRetriesIdx < self.freertosNtkRetriesMax)):
                self.freertosNtkRetriesIdx += 1
                outCmd = self.runCommand("isNetworkUp",endsWith="<NTK-READY>",
                    erroneousContents=["(Error)","INVALID"],timeout=20,
                    shutdownOnError=False,suppressErrors=True
                    )
                isSuccess, _, wasTimeout, _ = outCmd
                if (isSuccess):
                    isSuccess = self.pingTarget(exitOnError=False)
                if (not isSuccess):
                    if (self.freertosNtkRetriesIdx < self.freertosNtkRetriesMax):
                        warnAndLog(f"Network is not up on target. Trying again ({self.freertosNtkRetriesIdx+1}/{self.freertosNtkRetriesMax})...")
                        self.fpgaReload(self.osImageElf,elfLoadTimeout=30)
                    else:
                        self.shutdownAndExit("Network is not up on target.",exitCode=EXIT.Network) 
        elif (self.osImage=='FreeBSD'):
            self.runCommand(f"route add default {self.ipHost}")
            outCmd = self.runCommand (f"ifconfig xae0 inet {self.ipTarget}/24",timeout=60)
        else:
            self.shutdownAndExit(f"<activateEthernet> is not implemented for<{self.osImage}> on <{self.target}>.")

        if (self.osImage!='FreeRTOS'):
            self.pingTarget()

        if (self.osImage=='FreeBSD'): #use ssh instead of JTAG
            self.openSshConn()
        return outCmd

    @decorate.debugWrap
    def targetTearDown(self):
        self.fpgaTearDown()
        return

    @decorate.debugWrap
    def interact (self):
        #This method gives the control back to the user
        # could not use "pexpect.spawn.interact" as "fdpexpect.spawn" does not have the method
        if (self.inInteractMode):
            return #avoid recursive interact mode
        self.inInteractMode = True
        if (self.isSshConn): #only interact on the JTAG
            self.closeSshConn()
        if (self.osImage=='FreeRTOS'):
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

#--- END OF CLASS vcu118Target------------------------------

def programFpga(bitStream, probeFile, attempts=2, targetId=None):
    """programs the fpga with a given bitstream and probe file
    matches the functionality of the old `gfe-program-fpga`
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
            programFpga(bitStream, probeFile, attempts=attempts-1, targetId=targetId)
        else:
            logAndExit(f"programFpga: failed to program the FPGA.",exitCode=EXIT.Run)


def clearFlash(attempts=2, targetId=None):
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
            clearFlash(attempts=attempts-1, targetId=targetId)
        else:
            logAndExit(f"programFpga: failed to clear flash for the FPGA.",exitCode=EXIT.Run)

@decorate.debugWrap
@decorate.timeWrap
def programBitfile (doPrint=True,isReload=False,targetId=None):
    printAndLog("Preparing the FPGA environment...",doPrint=doPrint)
    clearProcesses()
    if (not isReload):
        gfeDir = os.path.join(getSetting('workDir'), 'gfe')
        if not os.path.exists(gfeDir):
            mkdir (gfeDir)

    printAndLog("Clearing the flash...",doPrint=False)
    clearFlash(targetId=targetId)

    if (not doesSettingExist('bitAndProbefiles',targetId=targetId)):
        bitAndProbefiles = selectBitAndProbeFiles(targetId=targetId)
        setSetting('bitAndProbefiles',bitAndProbefiles,targetId=targetId)
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
            setSetting('md5bifile',md5.hexdigest(),targetId=targetId)
        except Exception as exc:
            logAndExit(f"Could not compute md5 for file <{bitAndProbefiles[0]}>.", exc=exc, exitCode=EXIT.Run)

    printAndLog("Programming the bitfile...",doPrint=doPrint)
    programFpga(*getSetting('bitAndProbefiles',targetId=targetId),targetId=targetId)
    printAndLog(f"Programmed bitfile {getSetting('bitAndProbefiles',targetId=targetId)[0]} "
        f"(md5: {getSetting('md5bifile',targetId=targetId)})",doPrint=doPrint)

    printAndLog("FPGA was programmed successfully!",doPrint=doPrint)

@decorate.debugWrap
def selectBitAndProbeFiles (targetId=None):
    bitfileName = "soc_" + getSetting('processor',targetId=targetId) + ".bit"
    probfileName = "soc_" + getSetting('processor',targetId=targetId) + ".ltx"

    if getSetting('useCustomProcessor',targetId=targetId):
        bitfileDir = getSetting('pathToCustomProcessorSource',targetId=targetId)
    else:
        useNix = False
        # If source is GFE, we check the nix environment for latest bitfiles
        if getSetting('binarySource',targetId=targetId) == 'GFE':
            envBitfileDir = getSettingDict('nixEnv', ['gfeBitfileDir'])
            if envBitfileDir in os.environ:
                bitfileDir = os.environ[envBitfileDir]
                useNix = True
            else:
                printAndLog(f"Could not find bitfileDir for <{getSetting('processor',targetId=targetId)}> in nix environment. Falling back to binary repo.", doPrint=False)
        if (not useNix): #use binaries repo
            bitfileDir = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource',targetId=targetId), 'bitfiles', 'vcu118')
    
    return (os.path.join(bitfileDir, bitfileName),os.path.join(bitfileDir, probfileName))

@decorate.debugWrap
def checkEthAdaptorIsUp ():
    try:
        return psutil.net_if_stats()[getSetting('ethAdaptor')].isup
    except Exception as exc:
        logAndExit (f"vcu118.checkEthAdaptorIsUp: Failed to check that <{getSetting('ethAdaptor')}> is up.",exc=exc,exitCode=EXIT.Network)

@decorate.debugWrap
def resetEthAdaptor ():
    #In cyberPhys, this can be called many times, so have to be careful
    if (isEqSetting('mode','cyberPhys')):
        getSetting('networkLock').acquire()
        if doesSettingExist('vcu118EthAdaptorReset') and isEnabled('vcu118EthAdaptorReset'): #for future compatibility if needed to re-reset
            getSetting('networkLock').release()
            return #already reset
        else:
            setSetting('vcu118EthAdaptorReset',True)

    #get the name and check configuration if this is the first time called
    if (not doesSettingExist('ethAdaptor')):
        ethAdaptor= getSetting('vcu118EthAdaptorName')
        if (getAddrOfAdaptor(ethAdaptor,'MAC') != getSetting('vcu118EthAdaptorMacAddress')):
            logAndExit(f"checkEthAdaptorConfiguration: <{ethAdaptor}> does not have the expected mac address <{getSetting('vcu118EthAdaptorMacAddress')}>. Please check the network configuration.",exitCode=EXIT.Network)
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
            if (getAddrOfAdaptor(getSetting('ethAdaptor'),'IP',exitIfNoAddr=False) == getSetting('vcu118IpHost')):
                break
            else:
                printAndLog (f"vcu118.resetEthAdaptor: <{getSetting('ethAdaptor')}> is up, but it does not have the right IP. Will try to assign it.",doPrint=False)
                sudoShellCommand(['ip','addr','add',f"{getSetting('vcu118IpHost')}/24",'dev',getSetting('ethAdaptor')],sudoPromptPrefix)
                time.sleep(3)
                isReset = checkEthAdaptorIsUp ()
                if (isReset):
                    break

        if ((not isReset) and (iAttempt < nAttempts - 1)):
            printAndLog (f"vcu118.resetEthAdaptor: Failed to reset <{getSetting('ethAdaptor')}>. Trying again...",doPrint=False)
            time.sleep(3)

    if (not isReset):
        logAndExit (f"vcu118.resetEthAdaptor: Failed to reset <{getSetting('ethAdaptor')}>.",exitCode=EXIT.Network)

    printAndLog (f"vcu118.resetEthAdaptor: <{getSetting('ethAdaptor')}> is properly reset.",doPrint=False)

    if (isEqSetting('mode','cyberPhys')):
        getSetting('networkLock').release()

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
