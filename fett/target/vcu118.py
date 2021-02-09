#! /usr/bin/env python3
""" 
vcu118 class + misc vcu118 functions
"""

from fett.base.utils.misc import *
from fett.target.common import *
from fett.target.fpga import fpgaTarget, failStage
from fett.target.build import getTargetIp, getTargetMac, freeRTOSBuildChecks, buildFreeRTOS

import subprocess, psutil, tftpy
import serial, serial.tools.list_ports, usb
import sys, signal, os, socket, time
import pexpect, threading
from pexpect import fdpexpect
from math import sqrt

class vcu118Target (fpgaTarget, commonTarget):
    def __init__ (self, targetId=None):

        commonTarget.__init__(self, targetId=targetId)
        fpgaTarget.__init__(self, targetId=targetId)

        self.osImageElf = getSetting('osImageElf',targetId=self.targetId)

        self.ipHost = getSetting('vcu118IpHost')
        self.ipTarget = getTargetIp(targetId=targetId)
        self.macTarget = getTargetMac(targetId=targetId)

        self.uartSession = None

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
                success, netbootTimeoutDict, message = self.get_timeout_from_settings_dict("FreeRTOS")
                if not success:
                    self.terminateAndExit(**message)
                self.fpgaStart(getSetting('netbootElf',targetId=self.targetId),
                        elfLoadTimeout=self.parseBootTimeoutDict(netbootTimeoutDict,key="elfLoad"))
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
                with getSetting('tftpLock'):
                    serverThread = threading.Thread(target=server.listen, kwargs={'listenip': self.ipHost, 'listenport': listenPort})
                    serverThread.daemon = True
                    getSetting('trash').throwThread(serverThread, "TFTP server listening on host for netboot")
                    serverThread.start()
                    printAndLog (f"Started TFTP server on port {listenPort}.",doPrint=False)
                    time.sleep(1)
                    self.sendToTarget(f"boot -p {listenPort} {self.ipHost} {basename}\r\n")
                    self.expectFromTarget("Finished receiving","Netbooting",timeout=timeout,overrideShutdown=True)

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
            self.fpgaStart(self.osImageElf,elfLoadTimeout=self.parseBootTimeoutDict(timeoutDict,key="elfLoad")) 
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
            self.runCommand(f"ip link set dev eth0 address {self.macTarget}")
            # In case the TI ethernet chip doesn't come up, retry
            outCmd = self.runCommand ("ifup eth0",endsWith=['rx/tx','off'],expectedContents=['Link is Up'],exitOnError=False)
            isSuccess, _, _, _ = outCmd
            if not isSuccess:
                self.runCommand ("ifdown eth0",exitOnError=False)
                outCmd = self.runCommand ("ifup eth0",endsWith=['rx/tx','off'],expectedContents=['Link is Up'])
            self.runCommand(f"ip route add default via {self.ipHost}")
        elif (self.osImage=='busybox'):
            time.sleep(1)
            self.runCommand(f"ip link set dev eth0 address {self.macTarget}")
            self.runCommand ("ifconfig eth0 up",timeout=20)
            outCmd = self.runCommand(f"ifconfig eth0 {self.ipTarget}",endsWith=['rx/tx','off'],expectedContents=['Link is Up'],timeout=20)
        elif (self.osImage=='FreeRTOS'):
            isSuccess = False
            while ((not isSuccess) and (self.freertosNtkRetriesIdx < self.freertosNtkRetriesMax)):
                self.freertosNtkRetriesIdx += 1
                outCmd = self.runCommand("isNetworkUp",endsWith="<NTK-READY>",
                    erroneousContents=["(Error)","INVALID"],timeout=90,
                    exitOnError=False,suppressErrors=True
                    )
                isSuccess, _, _, _ = outCmd
                if (isSuccess):
                    isSuccess = self.pingTarget(exitOnError=False)
                if (not isSuccess):
                    if (self.freertosNtkRetriesIdx < self.freertosNtkRetriesMax):
                        warnAndLog(f"{self.targetIdInfo}Network is not up on target. Trying again ({self.freertosNtkRetriesIdx+1}/{self.freertosNtkRetriesMax})...")
                        self.fpgaReload(self.osImageElf,elfLoadTimeout=30)
                    else:
                        self.terminateAndExit(f"{self.targetIdInfo}Network is not up on target.",exitCode=EXIT.Network) 
        elif (self.osImage=='FreeBSD'):
            self.runCommand(f"ifconfig xae0 ethet {self.macTarget}")
            self.runCommand(f"route add default {self.ipHost}")
            outCmd = self.runCommand (f"ifconfig xae0 inet {self.ipTarget}/24",timeout=60)
        else:
            self.terminateAndExit(f"{self.targetIdInfo}<activateEthernet> is not implemented for<{self.osImage}> on <{self.target}>.")

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
    def getOpenocdCustomCfg(self,isReload=False):
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
                            f"the JTAG of HW ID <{hwId}>.",doPrint=(not isReload))
                        try:
                            usb.util.claim_interface(dev.dev,0)
                            usb.util.release_interface(dev.dev,0)
                        except Exception as exc:
                            warnAndLog(f"{self.targetIdInfo}getOpenocdCustomCfg: Failed to claim the interface "
                                f"of the USB port connected to the JTAG. Will continue anyway.",
                                exc=exc, doPrint=(not isReload))
                        # return: bus-port[.port...]
                        return f"; adapter usb location {bus.location}-{'.'.join([str(num) for num in dev.dev.port_numbers])}"
            logAndExit(f"{self.targetIdInfo}getOpenocdCmd: Failed to find the USB port that is connected to "
                f"the JTAG of HW ID <{hwId}>.",exitCode=EXIT.Configuration)
        else:
            # In case of a single board, the openocd configuration in `fett/target/utils/openocd_vcu118.cfg`
            # uses `ftdi_vid_pid` to select the device with the correct vendor ID and product ID, so no need
            # for further specification.
            return ''

    @decorate.debugWrap
    @decorate.timeWrap
    def setupUart(self): #The execution of this method is protected by openocdLock in fpga.py
        if (not doesSettingExist('vcu118UartDevice',targetId=self.targetId)):
            if (not doesSettingExist('vcu118UartDevices')):
                objUartDevices = self.findUartDevices()
                setSetting('vcu118UartDevices',objUartDevices)
                if (isEqSetting('mode','cyberPhys')):
                    if ((getSetting('nTargets') > len(objUartDevices.getAllUartDevices()))):
                        logAndExit(f"{self.targetIdInfo}setupUart: Number of UART devices "
                            f"(={len(objUartDevices.getAllUartDevices())}) < < Number of targets "
                            f"(={getSetting('nTargets')}).",exitCode=EXIT.Configuration)

            objUartDevices = getSetting('vcu118UartDevices')
            uartSNs = objUartDevices.getAllUartSNs()

            if (len(uartSNs)==0):
                logAndExit(f"{self.targetIdInfo}setupUart: The uart devices list is empty!", exitCode=EXIT.Configuration)
            elif(len(uartSNs)==1):
                uartSN = uartSNs.pop(0)
            else:
                uartSN = self.findTheRightUartDevice(objUartDevices)
            logging.debug(f"{self.targetIdInfo}setupUart: uartSN is <{uartSN}>.")
            uartDevice = objUartDevices.getUartDevice(uartSN)
            objUartDevices.removeUartDevice(uartSN)
            fpgaHwId = getSetting('vcu118HwTarget',targetId=self.targetId).split('/')[-1]
            objUartDevices.associateFpgaHwId(uartSN,fpgaHwId)
            printAndLog(f"{self.targetIdInfo}setupUart: Will use <{uartDevice}>.")
            uartSessionDict = self.startUartSession(uartDevice)
        else:
            # Not the first time to start the uart session
            uartSessionDict = self.startUartSession(getSetting('vcu118UartDevice',targetId=self.targetId))

        #set the uart related members
        for name,val in uartSessionDict.items():
            setattr(self,name,val)
        #Attach the uartDevice setting to the targetId
        setSetting('vcu118UartDevice',self.uartDevice,targetId=self.targetId)
        #The main process is the ttyProcess by default
        self.process = self.ttyProcess

    @decorate.debugWrap
    @decorate.timeWrap
    def startUartSession(self, uartDevice, ttyDir=None):
        # configure the serial connection
        uartSettings = getSetting('vcu118UartSettings')
        # Translate settings into serial settings
        if hasattr(serial, f"PARITY_{uartSettings['parity'].upper()}"):
            parity = getattr(serial, f"PARITY_{uartSettings['parity'].upper()}")
        else:
            logAndExit(f"startUartSession: parity {uartSettings['parity']} must be even, odd, or none.",exitCode=EXIT.Configuration)

        sbit_mapping = {1: serial.STOPBITS_ONE, 2: serial.STOPBITS_TWO}
        if uartSettings['stopbits'] in sbit_mapping:
            stopbits = sbit_mapping[uartSettings['stopbits']]
        else:
            logAndExit(f"startUartSession: stop bits {uartSettings['stopbits']} must be 1 or 2",exitCode=EXIT.Configuration)

        byte_mapping = {5: serial.FIVEBITS, 6: serial.SIXBITS, 7: serial.SEVENBITS, 8: serial.EIGHTBITS}
        if uartSettings['bytesize'] in byte_mapping:
            bytesize = byte_mapping[uartSettings['bytesize']]
        else:
            logAndExit(f"startUartSession: bytesize {uartSettings['bytesize']} must be 5,6,7 or 8",exitCode=EXIT.Configuration)

        try:
            uartSession = serial.Serial(
                port=uartDevice,
                baudrate=uartSettings['baudrate'],
                parity=parity,
                stopbits=stopbits,
                timeout=uartSettings['timeout'],
                bytesize=bytesize
            )

            if not uartSession.is_open:
                uartSession.open()
        except Exception as exc:
            logAndExit(f"{self.targetIdInfo}startUartSession: unable to open serial session on <{uartDevice}>.", exc=exc, exitCode=EXIT.Run)

        # start the tty process
        if (ttyDir is None): #default
            ttyDir = getSetting('workDir')
            ttySuffix = self.targetSuffix
        else: #looking for the right uart
            ttySuffix = f"_{uartDevice.split('/')[-1]}"
        fTtyOut = ftOpenFile(os.path.join(ttyDir,f'tty{ttySuffix}.out'),'ab')
        ttyProcess = fdpexpect.fdspawn(uartSession.fileno(),logfile=fTtyOut,timeout=30)

        return {'fTtyOut':fTtyOut,'ttyProcess':ttyProcess,'uartSession':uartSession,'uartDevice':uartDevice}

    @decorate.debugWrap
    def findUartDevices(self):
        # Initialize a UartDevices obj
        uartDevices = UartDevices()
        # Get a list of all serial ports with the desired VID/PID
        uartSettings = getSetting('vcu118UartSettings')
        vid = uartSettings['vid']
        pid = uartSettings['pid']
        for port in serial.tools.list_ports.comports():
            if ((port.vid != vid) or (port.pid != pid)):
                continue #not the CP2105 chips we're looking for
            if (port.location.endswith('1')): 
            # Silabs chip on VCU118 has two ports. Locate port 1 from the hardware description
                printAndLog(f"findUartDevices: located UART device at {port.device}"
                    f"with serial number {port.serial_number}", doPrint=False)
                uartDevices.addUartPort(port)
        logging.debug(f"findUartDevices: Found the following UART devices: <{','.join(uartDevices.getAllUartDevices())}>.")
        return uartDevices

    @decorate.debugWrap
    @decorate.timeWrap
    def findTheRightUartDevice(self,objUartDevices):
        """ Brute Force search for the uart devices """
        hwId = getSetting('vcu118HwTarget',targetId=self.targetId).split('/')[-1]
        
        # Check if it's saved
        uartSN = objUartDevices.getUartSerialNumber(hwId,"fpgaHwId")
        if (uartSN is not None):
            logging.debug(f"{self.targetIdInfo}findTheRightUartDevice: Already associated with <{uartSN}>.")
            return uartSN
        logging.debug(f"{self.targetIdInfo}findTheRightUartDevice: searching among <{','.join(objUartDevices.getAllUartDevices())}>.")

        #Prepare the minimal ELF
        smokeElf = self.buildSmokeElfForUartSearch(hwId)

        #Start listening on all UART devices
        uartDevicesDict = {}
        for uartDevice in objUartDevices.getAllUartDevices(): #No need to thread this as it should be immediate
            uartDevicesDict[uartDevice] = self.startUartSession(uartDevice,ttyDir=os.path.dirname(smokeElf))
        
        #Run the smoke program
        self.gdbProgStart(smokeElf,10,mainProg=False)
        
        def checkUartDevice(uartDevice,uartDevicesDict):
            _,uartDevicesDict[uartDevice]['wasTimeout'],_ = self.expectFromTarget(
                hwId, f"Searching for the UART connected to {hwId}",
                exitOnError=False, timeout=3, issueInterrupt=False,
                suppressWarnings=True,process=uartDevicesDict[uartDevice]['ttyProcess'])
            logging.debug(f"{self.targetIdInfo}Closing uart_session <{uartDevice}>.")
            try:
                uartDevicesDict[uartDevice]['uartSession'].close()
            except Exception as exc:
                warnAndLog(f"{self.targetIdInfo}findTheRightUartDevice: unable to close the serial "
                    f" session on {uartDevice}.",exc=exc,doPrint=False)
            fTtyOut = uartDevicesDict[uartDevice]['fTtyOut']
            try:
                fTtyOut.close()
            except Exception as exc:
                warnAndLog(f"{self.targetIdInfo}findTheRightUartDevice: Failed to close "
                    f" <{fTtyOut.name}>.",doPrint=False,exc=exc)

        #Check which one received the text
        for uartDevice in objUartDevices.getAllUartDevices():
            xThread = threading.Thread(target=checkUartDevice, args=(uartDevice,uartDevicesDict))
            uartDevicesDict[uartDevice]['checkThread'] = xThread
            xThread.daemon = True
            getSetting('trash').throwThread(xThread,f"checkUartDevice-target{self.targetId}-{self.targetId}-{uartDevice}")
            xThread.start()

        goldenDevice = None
        for uartDevice in objUartDevices.getAllUartDevices():
            uartDevicesDict[uartDevice]['checkThread'].join()
            if (not uartDevicesDict[uartDevice]['wasTimeout']):
                if (goldenDevice is not None):
                    warnAndLog(f"{self.targetIdInfo}findTheRightUartDevice: <{uartDevice}> received the text too!")
                else:
                    goldenDevice = uartDevice

        #Close gdb with the smoke program
        self.interruptGdb()
        self.gdbDetach()
        self.runCommandGdb("quit",endsWith=pexpect.EOF,exitOnError=False)
        try:
            self.fGdbOut.close()
        except Exception as exc:
            warnAndLog(f"{self.targetIdInfo}findTheRightUartDevice: Failed to close <{xFile.name}>.",doPrint=False,exc=exc)

        if (goldenDevice is not None):
            logging.debug(f"{self.targetIdInfo}findTheRightUartDevice: golden device is {goldenDevice}.")
            return objUartDevices.getUartSerialNumber(goldenDevice,"uartDevice")
        
        self.fpgaTearDown(stage=failStage.openocd)
        logAndExit(f"{self.targetIdInfo}findTheRightUartDevice: Brute Force device search failed to find the uart "
            f"device connected to {hwId}.",exitCode=EXIT.Configuration)

    @decorate.debugWrap
    @decorate.timeWrap
    def buildSmokeElfForUartSearch(self,hwId):
        freeRTOSBuildChecks(targetId=self.targetId)
        if (not doesSettingExist('buildDir',targetId=self.targetId)): #In case of busybox for instance
            buildDir = os.path.join(getSetting('workDir'), f'build{self.targetSuffix}')
            mkdir(buildDir)
            setSetting('buildDir',buildDir,targetId=self.targetId)
        buildDir = os.path.join(getSetting('buildDir',targetId=self.targetId),'buildSmokeElfForUart')
        mkdir(buildDir)

        #Copy the C files
        copyDir(os.path.join(getSetting('repoDir'),'fett','target','utils','srcMinimalFreeRTOS'),buildDir,copyContents=True)

        #The needed configs
        fConfig = ftOpenFile(os.path.join(buildDir,'fettFreeRTOSConfig.h'),'a')
        fConfig.write(f"#define\tFETT_HWID\t\"{hwId}\"\n")
        fConfig.close()

        configHfile = ftOpenFile (os.path.join(buildDir,'fettUserConfig.h'),'a')
        configHfile.write(f"#define BIN_SOURCE_{getSetting('binarySource',targetId=self.targetId).replace('-','_')}\n")
        configHfile.close()

        #build the elf
        buildFreeRTOS(doPrint=False, targetId=self.targetId, buildDir=buildDir)

        return os.path.join(buildDir,'FreeRTOS.elf')


#--- END OF CLASS vcu118Target------------------------------
class UartDevices:
    def __init__(self):
        # Load the saved map if any
        self._uartHwIdMap = safeLoadJsonFile (getSetting("uartDevicesSavedMap"), emptyIfNoFile=True)
        self._uartDevicesMap = {}

    def addUartPort(self,objPort):
        serialNumber = objPort.serial_number
        if (serialNumber not in self._uartHwIdMap):
            self._uartHwIdMap[serialNumber] = None
        self._uartDevicesMap[serialNumber] = objPort.device
    
    def associateFpgaHwId(self,uartSerialNumber,fpgaHwId):
        self._uartHwIdMap[uartSerialNumber] = fpgaHwId
        self.exportUartMap() #Save it every time the HwIdMap is updated

    def getUartDevice(self,serialNumber):
        if (serialNumber in self._uartDevicesMap):
            return self._uartDevicesMap[serialNumber]
        else:
            return None

    def getUartSerialNumber(self,val,valType):
        if (valType == "fpgaHwId"):
            xDict = self._uartHwIdMap
        elif (valType == "uartDevice"):
            xDict = self._uartDevicesMap
        else:
            logAndExit(f"getUartSerialNumber: Unknown valType <{valType}>.",exitCode=EXIT.Dev_Bug)
        for serialNumber,xVal in xDict.items():
            if (xVal == val):
                return serialNumber
        return None

    def getAllUartSNs(self):
        return list(self._uartDevicesMap.keys())

    def getAllUartDevices(self):
        return list(self._uartDevicesMap.values())

    def removeUartDevice(self,uartSerialNumber):
        self._uartDevicesMap.pop(uartSerialNumber,None)

    def exportUartMap(self):
        safeDumpJsonFile(self._uartHwIdMap, getSetting("uartDevicesSavedMap"))


#--- END OF CLASSES ------------------------------

_MAX_PROG_ATTEMPTS = 3

@decorate.debugWrap
@decorate.timeWrap
def programVcu118(mode, attempts=_MAX_PROG_ATTEMPTS-1, targetId=None):
    """programs the vcu118 fpga, either with a given bitstream and probe file or the flash with the bitstream and the os binary
    """
    targetInfo = f"<target{targetId}>: " if (targetId) else ''
    cwd = getSetting('gfeWorkDir',targetId=targetId)

    # copy tcl file over to workDir
    cp(os.path.join(getSetting('tclSourceDir'), 'prog_vcu118.tcl'), cwd)
    if (mode=="bitstream"):
        tclMode = "bitstream_nonpersistent"
        extraFile = getSetting('bitAndProbefiles',targetId=targetId)[1]
        timeout = 120
    elif(mode=="flash"):
        tclMode = "bitstreamAndData_flash"
        extraFile = getSetting('osImageElf',targetId=targetId)
        # timeout depends on the files sizes; this equation is empirical (250*sqrt(bit)+200*sqrt(data)-850) + 15% margin
        try:
            bitstreamSize = os.path.getsize(getSetting('bitAndProbefiles',targetId=targetId)[0])/(1024*1024)
            datafileSize = os.path.getsize(extraFile)/(1024*1024)
            timeout = int(1.15*(250*sqrt(bitstreamSize) + 200*sqrt(datafileSize) - 850))
            logging.debug(f"{targetInfo}programVcu118: Will use flash timeout of <{timeout}>.")
        except Exception as exc:
            timeout = 2400 #fallout value
            errorAndLog(f"{targetInfo}programVcu118: Failed to compute the flashing timeout. "
                f"Will use the default value <{timeout}>.",exc=exc)
    else:
        logAndExit(f"{targetInfo}programVcu118: Called with a non-recognized mode <{mode}>.",exitCode=EXIT.Dev_Bug)

    with getSetting('openocdLock'):
        retProc = shellCommand([getSetting('vivadoCmd'),'-nojournal','-source','./prog_vcu118.tcl',
                    '-log', os.path.join(cwd,'prog_vcu118.log'),'-mode','batch',
                    '-tclargs',tclMode,getSetting('vcu118HwTarget',targetId=targetId),
                    getSetting('bitAndProbefiles',targetId=targetId)[0], extraFile],
                    timeout=timeout,cwd=cwd,check=False)
        isSuccess = (retProc.returncode == 0)
        if ((mode=="flash") and (retProc.returncode==1)): #check for the tcmalloc weird error exception
            logText = ftReadLines(os.path.join(cwd,'prog_vcu118.log'),splitLines=False)
            isSuccess = ( (len(re.findall("Program/Verify Operation successful.",logText))==3)
                            and (re.search("out of memory",logText) is not None) ) #looks like it went well

    if (not isSuccess):
        if attempts > 0:
            errorAndLog(f"{targetInfo}programVcu118: failed to program the FPGA. " 
                f"Trying again ({_MAX_PROG_ATTEMPTS-attempts+1}/{_MAX_PROG_ATTEMPTS})...",doPrint=True)
            programVcu118(mode, attempts=attempts-1, targetId=targetId)
        else:
            logAndExit(f"{targetInfo}programVcu118: failed to program the FPGA.",exitCode=EXIT.Run)

@decorate.debugWrap
@decorate.timeWrap
def prepareFpgaEnv(targetId=None):
    with getSetting('openocdLock'):
        if (doesSettingExist('vcu118PrepareFpgaEnv') and isEnabled('vcu118PrepareFpgaEnv')):
            firstTime = False
        else:
            firstTime = True
            setSetting('vcu118PrepareFpgaEnv',True)
        
        if (firstTime or (not isEqSetting('mode','cyberPhys'))):
            # Clear processes
            processesList = ['openocd', getSetting('vivadoCmd'), 'hw_server', 'loader', 'pyprogram_fpga']
            if (isEqSetting('mode','cyberPhys')):
                processesList.append('socat') # targets' UART get piped
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
                logAndExit(f"{targetInfo}prepareFpgaEnv: Not enough vcu118 HW targets found!",exitCode=EXIT.Configuration)
            
            if (isEnabled('useCustomHwTarget',targetId=targetId)):
                if (getSetting('customHwTarget',targetId=targetId) not in curList):
                    logAndExit(f"{targetInfo}prepareFpgaEnv: Custom target {getSetting('customHwTarget',targetId=targetId)} not found!",
                        exitCode=EXIT.Configuration)
                thisTarget = getSetting('customHwTarget',targetId=targetId)
                curList.remove(getSetting('customHwTarget',targetId=targetId))
            else:
                thisTarget = curList.pop(0)
            printAndLog(f"{targetInfo}prepareFpgaEnv: Using HW target <{thisTarget}>.")
            setSetting('vcu118HwTarget',thisTarget,targetId=targetId)
            setSetting('listVcu118HwTargets',curList) #to update the list

@decorate.debugWrap
@decorate.timeWrap
def programBitfile (doPrint=True,targetId=None):
    targetInfo = f"<target{targetId}>: " if (targetId) else ''
    printAndLog(f"{targetInfo}Preparing the VCU118 FPGA...",doPrint=doPrint)
    prepareFpgaEnv(targetId=targetId)

    if (not doesSettingExist('bitAndProbefiles',targetId=targetId)):
        bitAndProbefiles = selectBitAndProbeFiles(targetId=targetId)
        setSetting('bitAndProbefiles',bitAndProbefiles,targetId=targetId)
        for xFile in bitAndProbefiles:
            if not os.path.isfile(xFile):
                logAndExit(f"<{xFile}> does not exist.", exitCode=EXIT.Files_and_paths)
        setSetting('md5bifile',computeMd5ForFile(bitAndProbefiles[0]),targetId=targetId)

    mode = getSetting('vcu118Mode',targetId=targetId)
    if (mode=='nonPersistent'):
        printAndLog(f"{targetInfo}Programming the bitfile...",doPrint=doPrint)
        programVcu118("bitstream",targetId=targetId)
        printAndLog(f"{targetInfo}Programmed bitfile {getSetting('bitAndProbefiles',targetId=targetId)[0]} "
            f"(md5: {getSetting('md5bifile',targetId=targetId)})",doPrint=doPrint)
    elif (mode=='flashProgramAndBoot'):
        checkThatUartIsKnownForFlash(targetId=targetId)
        prepareOsBinaryForFlash(targetId=targetId)
        printAndLog(f"{targetInfo}Programming the flash...",doPrint=doPrint)
        programVcu118("flash",targetId=targetId)
        printAndLog(f"{targetInfo}Programmed with bitstream {getSetting('bitAndProbefiles',targetId=targetId)[0]} "
            f"(md5: {getSetting('md5bifile',targetId=targetId)})",doPrint=doPrint)
        waitForTargetsAndUser(targetId=targetId)
    elif (mode=='flashBoot'):
        checkThatUartIsKnownForFlash(targetId=targetId)
        warnAndLog(f"{targetInfo} Will proceed assuming the VCU118 flash was programmed and powercycled.")
    else:
        logAndExit(f"{targetInfo}programBitfile: Unrecognized VCU118 mode <{mode}>.",exitCode=EXIT.Dev_Bug)

    printAndLog(f"{targetInfo}FPGA is ready!",doPrint=doPrint)

@decorate.debugWrap
def checkThatUartIsKnownForFlash (targetId=None):
    """ Pre-target class, check that there is an associated UART before proceeding with Flash """
    targetInfo = f"<target{targetId}>: " if (targetId) else ''
    hwId = getSetting('vcu118HwTarget',targetId=targetId).split('/')[-1]
    if (not doesSettingExist('vcu118UartDevices')):
        objUartDevices = UartDevices()
    else:
        objUartDevices = getSetting('vcu118UartDevices')

    if (objUartDevices.getUartSerialNumber(hwId,"fpgaHwId") is None):
        logAndExit(f"{targetInfo}: There is no saved UART serial number for "
            f"<{getSetting('vcu118HwTarget',targetId=targetId)}>! Cannot use flash modes before "
            "having UART configuration saved first.",exitCode=EXIT.Run)

@decorate.debugWrap
@decorate.timeWrap
def prepareOsBinaryForFlash(targetId=None):
    targetInfo = f"<target{targetId}>: " if (targetId) else ''
    targetSuffix = f'_{targetId}' if (targetId) else ''
    if (not doesSettingExist('buildDir',targetId=targetId)): #In case of busybox for instance
        buildDir = os.path.join(getSetting('workDir'), f'build{targetSuffix}')
        mkdir(buildDir)
        setSetting('buildDir',buildDir,targetId=targetId)
    buildDir = os.path.join(getSetting('buildDir',targetId=targetId),'vcu118FlashBuild')
    mkdir(buildDir)

    #Copy the necessary files
    copyDir(os.path.join(getSetting('repoDir'),'fett','target','utils','vcu118FlashBuild'),buildDir,copyContents=True)
    cp(getSetting('osImageElf',targetId=targetId),os.path.join(buildDir,"prog.elf"))

    printAndLog (f"{targetInfo}Building the flash binary...",doPrint=False)
    envVars = []
    envVars.append(f"XLEN={getSetting('xlen',targetId=targetId)}")
    envVars.append(f"BIN_SOURCE={getSetting('binarySource',targetId=targetId).replace('-','_')}")
    envVars.append(f"PROG=prog.elf")
    make (envVars,buildDir,buildDir=buildDir)
    setSetting('osImageElf',os.path.join(buildDir,"bootmem.bin"),targetId=targetId) #use the new binary
    return

@decorate.debugWrap
@decorate.timeWrap
def waitForTargetsAndUser (targetId=None):
    # Wait for all targets
    if (isEqSetting('mode','cyberPhys')):
        if (not getSetting('vcu118FlashCounter').incAndCheck()): #not done yet
            getSetting('vcu118FlashCounter').waitForEverything()
            return
    # Wait for user
    printAndLog("Power cycle the FPGA(s) then press Enter to continue...")
    input()
    if (isEqSetting('mode','cyberPhys')):
        getSetting('vcu118FlashCounter').userIsReady()

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
def findMainAdaptorInfo ():
    if doesSettingExist('mainAdaptorName'):
        return getSetting('mainAdaptorName')
    #blindly find an adaptor connected to internet (hopefully -- maybe needs to be more sophisticated if needed)
    for xAdaptor in psutil.net_if_addrs():
        if ((xAdaptor != 'lo') and (not xAdaptor.startswith('docker')) and (not xAdaptor.startswith('tap')) and (not xAdaptor.endswith('fpga'))):
            setSetting('mainAdaptorName',xAdaptor)
            return xAdaptor

    logAndExit(f"findMainAdaptorInfo: Failed to blindly find an adaptor connected to internet.",exitCode=EXIT.Network)

@decorate.debugWrap
@decorate.timeWrap
def resetEthAdaptor ():
    with getSetting('networkLock'):
        if doesSettingExist('vcu118EthAdaptorReset') and isEnabled('vcu118EthAdaptorReset'): #for future compatibility if needed to re-reset
            return #already reset
        else:
            setSetting('vcu118EthAdaptorReset',True)

        #Check the ipv4 forwarding
        try:
            ipForward = int(subprocess.getoutput('sudo sysctl net.ipv4.ip_forward').split()[-1])
        except Exception as exc:
            logAndExit ("Failed to find the values of 'net.ipv4.ip_forward'.",exc=exc,exitCode=EXIT.Run)
        if (ipForward != 1):
            printAndLog("IP forwarding was not enabled, enabling now.")
            sudoShellCommand(['sysctl', '-w', 'net.ipv4.ip_forward=1'])

        mainAdaptorName = findMainAdaptorInfo()
        printAndLog(f"Found main Ethernet adaptor <{mainAdaptorName}>.")

        #Check the postrouting nat rule
        try:
            natTables = subprocess.getoutput('sudo iptables -t nat -S').splitlines()
            isNatRule = (f"-A POSTROUTING -o {mainAdaptorName} -j MASQUERADE" in natTables)
        except Exception as exc:
            logAndExit ("Failed to find out whether the main adaptor NAT was set up.",exc=exc,exitCode=EXIT.Run)
        if (not isNatRule):
            printAndLog("Enabling NAT on main adaptor.")
            sudoShellCommand(['iptables','-t', 'nat','-A','POSTROUTING',
                '-o',mainAdaptorName,'-j','MASQUERADE'])
            sudoShellCommand(['iptables', '-P', 'FORWARD', 'ACCEPT'])

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
