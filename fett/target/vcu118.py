#! /usr/bin/env python3
""" 
Main vcu118 class + misc vcu118 functions
"""

from fett.base.utils.misc import *
from fett.target.common import *
from fett.target.fpga import fpgaTarget
from fett.target.build import getTargetIp

import subprocess, psutil, tftpy, usb
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
                self.terminateAndExit (f"boot: ELF loader <{self.elfLoader}> not implemented.",overrideShutdown=True,exitCode=EXIT.Dev_Bug)

            if (self.elfLoader=='netboot'):
                self.expectFromTarget('>',"Starting netboot loader",timeout=60,overrideShutdown=True)
                dirname, basename = os.path.split(os.path.abspath(self.osImageElf))
                listenPort = self.findPort(portUse='netboot')
                printAndLog(f"{self.targetIdInfo}boot: netboot port is <{listenPort}>.")
                try:
                    #Need to divert the tftpy logging. Otherwise, in case of debug (`-d`), our logging will get smothered.
                    logging.getLogger('tftpy').propagate = False
                    logging.getLogger('tftpy').addHandler(logging.FileHandler(os.path.join(getSetting('workDir'),'tftpy.log'),'w'))
                    server = tftpy.TftpServer(dirname)
                except Exception as exc:
                    self.terminateAndExit(f"boot: Could not create TFTP server for netboot.", exc=exc,overrideShutdown=True,exitCode=EXIT.Run)

                serverThread = threading.Thread(target=server.listen, kwargs={'listenip': self.ipHost, 'listenport': listenPort})
                serverThread.daemon = True
                getSetting('trash').throwThread(serverThread, "TFTP server listening on host for netboot")
                serverThread.start()
                printAndLog (f"Started TFTP server on port {listenPort}.",doPrint=False)
                time.sleep(1)
                self.sendToTarget(f"boot -p {listenPort} {self.ipHost} {basename}\r\n")

            time.sleep(1)
            self.expectFromTarget(endsWith,"Booting",timeout=timeout,overrideShutdown=True)

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
                    self.terminateAndExit("Boot: In <onlySsh> mode, and failed to open SSH.")

        elif (self.osImage=='FreeRTOS'):
            self.fpgaStart(self.osImageElf,elfLoadTimeout=60) 
            time.sleep(1)
            self.expectFromTarget(endsWith,"Booting",timeout=timeout,overrideShutdown=True)
        else:
            self.terminateAndExit(f"<boot> is not implemented for <{self.osImage}> on <{self.target}>.",overrideShutdown=True)

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
                    exitOnError=False,suppressErrors=True
                    )
                isSuccess, _, wasTimeout, _ = outCmd
                if (isSuccess):
                    isSuccess = self.pingTarget(exitOnError=False)
                if (not isSuccess):
                    if (self.freertosNtkRetriesIdx < self.freertosNtkRetriesMax):
                        warnAndLog(f"Network is not up on target. Trying again ({self.freertosNtkRetriesIdx+1}/{self.freertosNtkRetriesMax})...")
                        self.fpgaReload(self.osImageElf,elfLoadTimeout=30)
                    else:
                        self.terminateAndExit("Network is not up on target.",exitCode=EXIT.Network) 
        elif (self.osImage=='FreeBSD'):
            self.runCommand(f"route add default {self.ipHost}")
            outCmd = self.runCommand (f"ifconfig xae0 inet {self.ipTarget}/24",timeout=60)
        else:
            self.terminateAndExit(f"<activateEthernet> is not implemented for<{self.osImage}> on <{self.target}>.")

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
                self.sendToTarget(b'\x03\r\n',exitOnError=False)
            elif (('shutdown' in instruction) or ('poweroff' in instruction) or ('halt' in instruction)):
                warnAndLog ("Please use \'--exit\' instead of direct shutting down command.")
                self.sendToTarget(" ",exitOnError=False)
            else:
                self.sendToTarget(instruction,exitOnError=False)
                time.sleep(1)

        stopReading.set()
        time.sleep(5)
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def getOpenocdCustomCfg(self):
        # For many targets, we need to choose on which USB port to start openocd
        if (isEnabled('IsThereMoreThanOneVcu118Target')):
            hwId = getSetting('vcu118HwTarget',targetId=self.targetId).split('/')[-1]
            for bus in usb.busses():
                for dev in bus.devices:
                    try:
                        #hasattr() returns true, but getattr gives an error, so we have to work around it
                        serial_number = dev.dev.serial_number 
                    except:
                        continue
                    if (serial_number == hwId): #Found the USB port connected to the JTAG of this hw target
                        printAndLog(f"{self.targetIdInfo}getOpenocdCmd: USB device <{dev.dev.address}> is connected to "
                            f"the JTAG of HW ID <{hwId}>.")
                        # return: bus-port[.port...]
                        return f"; adapter usb location {bus.location}-{'.'.join(dev.dev.port_numbers)}"
            logAndExit(f"{self.targetIdInfo}getOpenocdCmd: Failed to find the USB port that is connected to "
                f"the JTAG of HW ID <{hwId}>.",exitCode=EXIT.Configuration)
        else:
            # In case of a single board, the openocd configuration in `fett/target/utils/openocd_vcu118.cfg`
            # uses `ftdi_vid_pid` to select the device with the correct vendor ID and product ID, so no need
            # for further specification.
            return ''

#--- END OF CLASS vcu118Target------------------------------

@decorate.debugWrap
@decorate.timeWrap
def programFpga(bitStream, probeFile, attempts=2, targetId=None):
    """programs the fpga with a given bitstream and probe file
    matches the functionality of the old `gfe-program-fpga`
    :param bitStream: valid filepath
    :param probeFile: valid probe file
    """
    targetInfo = f"<target{targetId}>: " if (targetId) else ''
    cwd = getSetting('gfeWorkDir',targetId=targetId)

    # copy files over to workDir
    cp(os.path.join(getSetting('tclSourceDir'), 'prog_bit.tcl'), cwd)

    # check that the input files exist
    if not os.path.exists(bitStream):
        logAndExit(f"{targetInfo}programFpga: bitstream file {bitStream} does not exist")
    if not os.path.exists(probeFile):
        logAndExit(f"{targetInfo}programFpga: probe file {probeFile} does not exist")

    retProc = shellCommand([getSetting('vivadoCmd'),'-nojournal','-source','./prog_bit.tcl',
                '-log', os.path.join(cwd,'prog_bit.log'),'-mode','batch',
                '-tclargs',getSetting('vcu118HwTarget',targetId=targetId),bitStream, probeFile],
                timeout=90,cwd=cwd,check=False)
    if retProc.returncode != 0:
        if attempts > 0:
            errorAndLog(f"{targetInfo}programFpga: failed to program the FPGA. Trying again...",doPrint=True)
            programFpga(bitStream, probeFile, attempts=attempts-1, targetId=targetId)
        else:
            logAndExit(f"{targetInfo}programFpga: failed to program the FPGA.",exitCode=EXIT.Run)

@decorate.debugWrap
@decorate.timeWrap
def clearFlash(attempts=2, targetId=None):
    """ clear flash memory on Fpga
    matches the functionality of gfe-clear-flash
    """
    targetInfo = f"<target{targetId}>: " if (targetId) else ''
    cwd = getSetting('gfeWorkDir',targetId=targetId)

    # copy files over to workDir
    cp(os.path.join(getSetting('tclSourceDir'), 'prog_flash.tcl'), cwd)
    cp(os.path.join(getSetting('tclSourceDir'), 'small.bin'), cwd)

    retProc = shellCommand([getSetting('vivadoCmd'),'-nojournal','-source','./prog_flash.tcl',
                '-log', os.path.join(cwd,'prog_flash.log'),'-mode','batch',
                '-tclargs',getSetting('vcu118HwTarget',targetId=targetId),'./small.bin'],
                timeout=90,cwd=cwd,check=False)
    if retProc.returncode != 0:
        if attempts > 0:
            errorAndLog(f"{targetInfo}clearFlash: failed to clear flash. Trying again...",doPrint=True)
            clearFlash(attempts=attempts-1, targetId=targetId)
        else:
            logAndExit(f"{targetInfo}clearFlash: failed to clear flash for the FPGA.",exitCode=EXIT.Run)

@decorate.debugWrap
@decorate.timeWrap
def prepareFpgaEnv(targetId=None):
    if (isEqSetting('mode','cyberPhys')):
        getSetting('vcu118Lock').acquire()

    if (doesSettingExist('vcu118PrepareFpgaEnv') and isEnabled('vcu118PrepareFpgaEnv')):
        firstTime = False
    else:
        firstTime = True
        setSetting('vcu118PrepareFpgaEnv',True)
    
    if (firstTime or (not isEqSetting('mode','cyberPhys'))):
        # Clear processes
        processesList = ['openocd', getSetting('vivadoCmd'), 'hw_server', 'loader', 'pyprogram_fpga']
        for proc in processesList:
            sudoShellCommand(['pkill', '-9', proc],check=False)

    # Create workDir/gfe
    targetSuffix = f'_{targetId}' if (targetId is not None) else ''
    gfeWorkDir = os.path.join(getSetting('workDir'), f'gfe{targetSuffix}')
    mkdir(gfeWorkDir,exitIfExists=False)
    setSetting('gfeWorkDir',gfeWorkDir,targetId=targetId)

    if (firstTime):
        # Find the target(s) names
        cp(os.path.join(getSetting('tclSourceDir'), 'get_hw_targets.tcl'), gfeWorkDir)
        getTargetsCmd = [getSetting('vivadoCmd'),'-nojournal','-source','./get_hw_targets.tcl',
                        '-log', os.path.join(gfeWorkDir,'get_hw_targets.log'), '-mode','batch']
        try:
            retCmd = subprocess.run(getTargetsCmd,capture_output=True,timeout=90,check=True,cwd=gfeWorkDir)
        except Exception as exc:
            logAndExit (f"prepareFpgaEnv: Failed to <{getTargetsCmd}>. "
                f"Check <{os.path.join(gfeWorkDir,'get_hw_targets.log')}> for more details.",exc=exc,exitCode=EXIT.Run)

        try:
            listTargetsMatch = matchExprInLines(r"listTargets=<(?P<listTargets>.*)>",retCmd.stdout.decode('utf-8').splitlines())
            listTargets = listTargetsMatch.group('listTargets').split()
        except Exception as exc:
            logAndExit (f"prepareFpgaEnv: Failed to find HW targets list.",exc=exc,exitCode=EXIT.Run)
        
        setSetting('listVcu118HwTargets',listTargets)
        printAndLog(f'prepareFpgaEnv: Found the following vcu118 targets:<{" ".join(listTargets)}>',doPrint=False)
        setSetting('IsThereMoreThanOneVcu118Target', (len(listTargets)>1))

    if (not doesSettingExist('vcu118HwTarget',targetId=targetId)):
        targetInfo = f"<target{targetId}>: " if (targetId) else ''
        curList = getSetting('listVcu118HwTargets')
        if (len(curList) == 0):
            logAndExit(f"{targetInfo}prepareFpgaEnv: Not enough vcu118 HW targets found!",exc=exc,exitCode=EXIT.Configuration)
        thisTarget = curList.pop(0)
        printAndLog(f"{targetInfo}prepareFpgaEnv: Using HW target <{thisTarget}>.")
        setSetting('vcu118HwTarget',thisTarget,targetId=targetId)
        setSetting('listVcu118HwTargets',curList) #to update the list

    if (isEqSetting('mode','cyberPhys')):
        getSetting('vcu118Lock').release()

@decorate.debugWrap
@decorate.timeWrap
def programBitfile (doPrint=True,isReload=False,targetId=None):
    targetInfo = f"<target{targetId}>: " if (targetId) else ''
    printAndLog(f"{targetInfo}Preparing the VCU118 FPGA...",doPrint=doPrint)
    prepareFpgaEnv(targetId=targetId)

    printAndLog(f"{targetInfo}Clearing the flash...",doPrint=False)
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

    printAndLog(f"{targetInfo}Programming the bitfile...",doPrint=doPrint)
    programFpga(*getSetting('bitAndProbefiles',targetId=targetId),targetId=targetId)
    printAndLog(f"{targetInfo}Programmed bitfile {getSetting('bitAndProbefiles',targetId=targetId)[0]} "
        f"(md5: {getSetting('md5bifile',targetId=targetId)})",doPrint=doPrint)

    printAndLog(f"{targetInfo}FPGA was programmed successfully!",doPrint=doPrint)

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
@decorate.timeWrap
def checkEthAdaptorIsUp ():
    try:
        return psutil.net_if_stats()[getSetting('ethAdaptor')].isup
    except Exception as exc:
        logAndExit (f"vcu118.checkEthAdaptorIsUp: Failed to check that <{getSetting('ethAdaptor')}> is up.",exc=exc,exitCode=EXIT.Network)

@decorate.debugWrap
@decorate.timeWrap
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
