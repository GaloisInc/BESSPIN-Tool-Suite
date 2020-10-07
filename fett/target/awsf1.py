import psutil, getpass
from fett.target.common import *
from fett.target.fpga import fpgaTarget

class firesimTarget(fpgaTarget, commonTarget):
    def __init__(self, targetId=None):

        commonTarget.__init__(self, targetId=targetId)
        fpgaTarget.__init__(self, targetId=targetId)

        self.ipTarget = getSetting('awsf1IpTarget')
        self.ipHost = getSetting('awsf1IpHost')  

        self.switch0Proc = None
        self.fswitchOut = None
        self.switch0timing = ['6405', '10', '200'] # dictated by cloudGFE

    @decorate.debugWrap
    @decorate.timeWrap
    def boot(self,endsWith="login:",timeoutDict={"boot":90}):
        if (getSetting('osImage') not in ['debian','FreeRTOS']):
            logAndExit (f"<firesimTarget.boot> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation)

        awsFiresimSimPath = os.path.join(getSetting('firesimPath'), 'sim')
        timeout = self.parseBootTimeoutDict (timeoutDict)

        # 0. Ensure the env is clear
        self.noNonsenseFiresim()
        
        # 1. Switch0
        self.fswitchOut = ftOpenFile(os.path.join(getSetting('workDir'),'switch0.out'),'ab')

        try:
            self.switch0Proc = pexpect.spawn(f"sudo ./switch0 {' '.join(self.switch0timing)}",logfile=self.fswitchOut,timeout=10,
                                        cwd=awsFiresimSimPath)
            self.switch0Proc.expect("Assuming tap0",timeout=10)
        except Exception as exc:
            self.shutdownAndExit(f"boot: Failed to spawn the switch0 process.",overrideShutdown=True,exc=exc,exitCode=EXIT.Run)

        # 2. fsim
        firesimCommand = ' '.join([
            "bash -c 'stty intr ^] &&", # Making `ctrl+]` the SIGINT for the session so that we can send '\x03' to target 
            'sudo',
            "LD_LIBRARY_PATH={}:$LD_LIBRARY_PATH".format(awsFiresimSimPath),
            './FireSim-f1',
            '+permissive',
            '+mm_relaxFunctionalModel=0',
            '+mm_openPagePolicy=1',
            '+mm_backendLatency=2',
            '+mm_schedulerWindowSize=8',
            '+mm_transactionQueueDepth=8',
            '+mm_dramTimings_tAL=0',
            '+mm_dramTimings_tCAS=14',
            '+mm_dramTimings_tCMD=1',
            '+mm_dramTimings_tCWD=10',
            '+mm_dramTimings_tCCD=4',
            '+mm_dramTimings_tFAW=25',
            '+mm_dramTimings_tRAS=33',
            '+mm_dramTimings_tREFI=7800',
            '+mm_dramTimings_tRC=47',
            '+mm_dramTimings_tRCD=14',
            '+mm_dramTimings_tRFC=160',
            '+mm_dramTimings_tRRD=8',
            '+mm_dramTimings_tRP=14',
            '+mm_dramTimings_tRTP=8',
            '+mm_dramTimings_tRTRS=2',
            '+mm_dramTimings_tWR=15',
            '+mm_dramTimings_tWTR=8',
            '+mm_rowAddr_offset=18',
            '+mm_rowAddr_mask=65535',
            '+mm_rankAddr_offset=16',
            '+mm_rankAddr_mask=3',
            '+mm_bankAddr_offset=13',
            '+mm_bankAddr_mask=7',
            '+mm_llc_wayBits=3',
            '+mm_llc_setBits=12',
            '+mm_llc_blockBits=7',
            '+mm_llc_activeMSHRs=8',
            '+debug_enable' if (isEqSetting('mode','evaluateSecurityTests') or isEnabled('gdbDebug')) else '\b',
            '+slotid=0',
            '+profile-interval=-1',
            f"+macaddr0={getSetting('awsf1MacAddrTarget')}",
            f"+blkdev0={getSetting('osImageImg')}",
            f"+niclog0={os.path.join(getSetting('workDir'),'niclog0.out')}",
            f"+blkdev-log0={os.path.join(getSetting('workDir'),'blkdev-log0.out')}",
            '+trace-select0=1',
            '+trace-start0=0',
            '+trace-end0=1',
            '+trace-output-format0=0',
            f"+dwarf-file-name0={getSetting('osImageDwarf')}",
            '+autocounter-readrate0=0',
            f"+autocounter-filename0={os.path.join(getSetting('workDir'),'AUTOCOUNTERFILE0.out')}",
            f"+linklatency0={self.switch0timing[0]}",
            f"+netbw0={self.switch0timing[2]}",
            '+shmemportname0=0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
            '+permissive-off',
            getSetting("osImageElf"),
            "\'"
        ])
        logging.debug(f"boot: firesimCommand = {firesimCommand}")
        targetSuffix = f'_{self.targetId}' if (self.targetId) else ''
        self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),f'tty{targetSuffix}.out'),'ab')

        try:
            self.ttyProcess = pexpect.spawn(firesimCommand,logfile=self.fTtyOut,timeout=30,
                                        cwd=awsFiresimSimPath)
            self.process = self.ttyProcess
            time.sleep(1)
        except Exception as exc:
            self.shutdownAndExit(f"boot: Failed to spawn the firesim process.",overrideShutdown=True,exc=exc,exitCode=EXIT.Run)

        if (isEqSetting('mode','evaluateSecurityTests') or isEnabled('gdbDebug')):
            self.expectFromTarget("Waiting for connection from gdb","Starting Firesim with GDB",timeout=30,overrideShutdown=True)
            self.fpgaStart(getSetting('osImageElf'))
        
        self.expectFromTarget(endsWith,"Booting",timeout=timeout,overrideShutdown=True)

        # The tap needs to be turned up AFTER booting
        if (isEqSetting('binarySource','Michigan')): #Michigan P1 needs some time before the network hook can detect the UP event
            time.sleep(20)
        setAdaptorUpDown(getSetting('awsf1TapAdaptorName'), 'up')

    @decorate.debugWrap
    def interact(self):
        if (isEqSetting('osImage','FreeRTOS')):
            printAndLog (f"FreeRTOS is left running on target. Press \"Ctrl + E\" to exit.")
        else:
            printAndLog (f"Entering interactive mode. Root password: \'{self.rootPassword}\'. Press \"Ctrl + E\" to exit.")
        super().interact()

    @decorate.debugWrap
    @decorate.timeWrap
    def activateEthernet(self):
        if (isEqSetting('osImage','debian')):
            if (not self.restartMode): #Was already done in the first start
                self.runCommand ("echo \"auto eth0\" > /etc/network/interfaces")
                self.runCommand ("echo \"iface eth0 inet static\" >> /etc/network/interfaces")
                self.runCommand (f"echo \"address {self.ipTarget}/24\" >> /etc/network/interfaces")
                self.runCommand (f"echo \"post-up ip route add default via {self.ipHost}\" >> /etc/network/interfaces")
            self.runCommand ("ifup eth0") # nothing comes out, but the ping should tell us
        elif (isEqSetting('osImage','FreeRTOS')):
            if (isEqSetting('binarySource','Michigan')):
                ntkReadyString = f"WebSocket server listening on port {getSettingDict('michiganInfo',['httpPort'])}"
                timeout = 120 #Yes, it needs time
            else:
                ntkReadyString = "<NTK-READY>"
                timeout = 30
            self.runCommand("isNetworkUp",endsWith=ntkReadyString,erroneousContents="(Error)",timeout=timeout)
        else:
            self.shutdownAndExit(f"<activateEthernet> is not implemented for<{getSetting('osImage')}> on <AWS:{getSetting('pvAWS')}>.")

        self.pingTarget()

        return

    @decorate.debugWrap
    def targetTearDown(self):
        if (isEqSetting('mode','evaluateSecurityTests')):
            self.fpgaTearDown()

        if (self.process.isalive()):
            # When executing the firesim command, we run it with `stty intr ^]` which changes
            # the interrupt char to be `^]` instead of `^C` to allow us sending the intr `^C`
            # to the target through firesim without interrupting firesim. In case the firesim 
            # process didn't return, which is the case for FreeRTOS as the scheduler never returns
            # but goes to the idle hook, if we don't send `^]`, some children processes stay as 
            # zombies, and if we run firesim again, the run gets messed up with those processes.
            # This also happens if a unix OS didn't exit properly. Towards the end of making each
            # run a standalone and independent of previous runs, we send this interrupt if the 
            # process is still alive.
            self.runCommand('\x1d\x1d',endsWith=pexpect.EOF,exitOnError=False,timeout=5,sendToNonUnix=True)

        self.noNonsenseFiresim()

        filesToClose = [self.fswitchOut]
        for xFile in filesToClose:
            try:
                xFile.close()
            except Exception as exc:
                warnAndLog(f"targetTearDown: Failed to close <{xFile.name}>.",doPrint=False,exc=exc)
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def noNonsenseFiresim (self):
        """
        This method ensures all relvant processes are killed. In a no-nonsense and brute way.
        """
        wereProcessesKilled = {'FireSim-f1':False, 'switch0':False} #False for wasKilled
        if (isEqSetting('mode','evaluateSecurityTests')):
            wereProcessesKilled.update({'openocd':False, 'riscv64-unknown-elf-gdb':False})

        def getAliveProcesses():
            return [proc for proc,wasKilled in wereProcessesKilled.items() if (not wasKilled)]

        # kill processes
        for proc in wereProcessesKilled:
            sudoShellCommand(['pkill', '-9', proc],check=False)

        # wait till the processes die
        nWaits = 5
        iWait = 0
        while ((iWait < nWaits) and (not all(wereProcessesKilled.values()))):
            time.sleep(1)
            iWait += 1
            for proc in getAliveProcesses():
                wereProcessesKilled[proc] = (sudoShellCommand(['pgrep', proc],check=False).returncode != 0)

        if (not all(wereProcessesKilled.values())):    
            warnAndLog (f"Failed to kill <{','.join(getAliveProcesses())}>.",doPrint=False)
        sudoShellCommand(['rm', '-rf', '/dev/shm/*'],check=False) #clear shared memory

    # ------------------ END OF CLASS firesimTarget ----------------------------------------

class connectalTarget(commonTarget):
    def __init__(self, targetId=None):
        super().__init__(targetId=targetId)
        self.ipTarget = getSetting('awsf1IpTarget')
        self.ipHost = getSetting('awsf1IpHost')

    @decorate.debugWrap
    @decorate.timeWrap
    def boot(self,endsWith="login:",timeoutDict={"boot":90}):
        if getSetting('osImage') not in ['debian', 'FreeBSD']:
            logAndExit (f"<connectalTarget.boot> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation)

        awsConnectalHostPath = os.path.join(getSetting('connectalPath'), 'sim')
        timeout = self.parseBootTimeoutDict (timeoutDict)

        extraArgs = getSetting('ssithAwsFpgaExtraArgs', default=[])
        tapName = getSetting('awsf1TapAdaptorName')
        connectalCommand = ' '.join([
            os.path.join(awsConnectalHostPath, "ssith_aws_fpga"),
            f"--dtb={getSetting('osImageDtb')}",
            f"--block={getSetting('osImageImg')}",
            f"--elf={getSetting('osImageElf')}"] + ([
            f"--elf={getSetting('osImageExtraElf')}"] if getSetting('osImageExtraElf') is not None else []) + [
            f"--tun={tapName}"] + extraArgs)

        printAndLog(f"<awsf1.connectalTarget.boot> connectal command: \"{connectalCommand}\"", doPrint=False)
        targetSuffix = f'_{self.targetId}' if (self.targetId) else ''
        self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),f'tty{targetSuffix}.out'),'ab')

        try:
            self.ttyProcess = pexpect.spawn(connectalCommand,logfile=self.fTtyOut,timeout=90,
                                         cwd=awsConnectalHostPath)
            self.process = self.ttyProcess
            time.sleep(1)
            self.expectFromTarget(endsWith,"Booting",timeout=timeout,overrideShutdown=True)
        except Exception as exc:
            self.shutdownAndExit(f"boot: Failed to spawn the connectal process.",overrideShutdown=True,exc=exc,exitCode=EXIT.Run)

         # The tap needs to be turned up AFTER booting
        setAdaptorUpDown(getSetting('awsf1TapAdaptorName'), 'up')

    def interact(self):
        printAndLog (f"Entering interactive mode. Root password: \'{self.rootPassword}\'. Press \"Ctrl + E\" to exit.")
        super().interact()

    @decorate.debugWrap
    @decorate.timeWrap
    def activateEthernet(self):
        if (isEqSetting('osImage','debian')):
            if (not self.restartMode): #Was already done in the first start
                self.runCommand ("echo \"auto eth0\" > /etc/network/interfaces")
                self.runCommand ("echo \"iface eth0 inet static\" >> /etc/network/interfaces")
                self.runCommand (f"echo \"address {self.ipTarget}/24\" >> /etc/network/interfaces")
                self.runCommand (f"echo \"post-up ip route add default via {self.ipHost}\" >> /etc/network/interfaces")
            self.runCommand ("ifup eth0") # nothing comes out, but the ping should tell us
        elif (isEqSetting('osImage', 'FreeBSD')):
            if (not self.restartMode): #Was already done in the first start
                self.runCommand ("ifconfig vtnet0 up")
                self.runCommand (f"ifconfig vtnet0 {self.ipTarget}/24")
                self.runCommand (f"ifconfig vtnet0 ether {getSetting('awsf1MacAddrTarget')}")
                self.runCommand(f"route add default {self.ipHost}")
            
                # For future restart
                self.runCommand (f"echo 'ifconfig_vtnet0=\"ether {getSetting('awsf1MacAddrTarget')}\"' >> /etc/rc.conf")
                self.runCommand (f"echo 'ifconfig_vtnet0_alias0=\"inet {self.ipTarget}/24\"' >> /etc/rc.conf")
                self.runCommand (f"echo 'defaultrouter=\"{self.ipHost}\"' >> /etc/rc.conf")
        else:
            self.shutdownAndExit(f"<activateEthernet> is not implemented for<{getSetting('osImage')}> on <AWS:{getSetting('pvAWS')}>.")

        self.pingTarget()
        return 

    @decorate.debugWrap
    def targetTearDown(self):
        if (self.process.isalive()):
            # connectal exits with "Ctrl-A x". In case smth needed interruption. If not, it will timeout, which is fine.
            self.runCommand("\x01x",endsWith=pexpect.EOF,exitOnError=False,timeout=5)

            if (self.process.isalive()):
                try:
                    subprocess.check_call(['sudo', 'kill', '-9', f"{self.process.pid}"],
                                        stdout=self.fTtyOut, stderr=self.fTtyOut)
                except Exception as exc:
                    warnAndLog("targetTearDown: Failed to kill <connectal> process.",doPrint=False,exc=exc)
        return
    # ------------------ END OF CLASS connectalTarget ----------------------------------------


@decorate.debugWrap
def configTapAdaptor():
    tapAdaptor = getSetting('awsf1TapAdaptorName')

    #get main adaptor and its main IP
    gotMainAdaptorInfo = False
    for xAdaptor in psutil.net_if_addrs():
        if (xAdaptor not in ['lo', tapAdaptor]):
            setSetting('awsf1MainAdaptorName',xAdaptor)
            setSetting('awsf1MainAdaptorIP',getAddrOfAdaptor(xAdaptor,'IP'))
            gotMainAdaptorInfo = True
            break
    if (not gotMainAdaptorInfo):
        logAndExit(f"configTapAdaptor: Failed to find the main ethernet adaptor info.",exitCode=EXIT.Network)

    commands = {
        'create' : [
            ['ip', 'tuntap', 'add', 'mode', 'tap', 'dev', tapAdaptor, 'user', getpass.getuser()]
        ],
        'disableIpv6' : [
			['sysctl', '-w', 'net.ipv6.conf.' + tapAdaptor + '.disable_ipv6=1']
		],
        'natSetup' : [
            # Enable ipv4 forwarding
            ['sysctl', '-w', 'net.ipv4.ip_forward=1'],
            # Add productionTargetIp to main adaptor
            ['ip', 'addr', 'add', getSetting('productionTargetIp'), 'dev',
             getSetting('awsf1MainAdaptorName')],
            # Reject mainIP:uartFwdPort if coming from FPGA
            ['iptables',
             '-A', 'INPUT',
             '-i', tapAdaptor,
             '-p', 'tcp',
             '--dport', str(getSetting('uartFwdPort')),
             '-d', getSetting('awsf1MainAdaptorIP'),
             '-s', getSetting('awsf1IpTarget'),
             '-j', 'REJECT'],
            # Route incoming to productionTargetIp:uartFwdPort to mainIP
            ['iptables',
             '-t', 'nat',
             '-A', 'PREROUTING',
             '-i', getSetting('awsf1MainAdaptorName'),
             '-p', 'tcp',
             '--dport', str(getSetting('uartFwdPort')),
             '-d', getSetting('productionTargetIp'),
             '-j', 'DNAT',
             '--to-destination', getSetting('awsf1MainAdaptorIP')],
            # Route packets from FPGA to productionTargetIp
            ['iptables',
             '-t', 'nat',
             '-A', 'POSTROUTING',
             '-o', getSetting('awsf1MainAdaptorName'),
             '-s', getSetting('awsf1IpTarget'),
             '-j', 'SNAT',
             '--to-source', getSetting('productionTargetIp')],
            # Route packets from productionTargetIp to FPGA
            ['iptables',
             '-t', 'nat',
             '-A', 'PREROUTING',
             '-i', getSetting('awsf1MainAdaptorName'),
             '-d', getSetting('productionTargetIp'),
             '-j', 'DNAT',
             '--to-destination', getSetting('awsf1IpTarget')],
            # Allow forwarding from productionTargetIp
            ['iptables',
             '-A', 'FORWARD',
             '-s', getSetting('productionTargetIp'),
             '-j', 'ACCEPT'],
            # Allow forwarding to FPGA
            ['iptables',
             '-A', 'FORWARD',
             '-d', getSetting('awsf1IpTarget'),
             '-j', 'ACCEPT']
        ],
        'refresh' : [
            ['ip', 'addr', 'flush', 'dev', tapAdaptor]
        ],
        'config' : [
            ['ip','addr','add',f"{getSetting('awsf1IpHost')}/24",'dev',tapAdaptor],
            ['ifconfig', tapAdaptor, 'hw', 'ether', getSetting('awsf1TapAdaptorMacAddress')],
        ],
        'down' : [
            ['ip','link','set', tapAdaptor, 'down'],
        ]
    }

    def execSudoCommands (commandNames):
        for xName in commandNames:
            for command in commands[xName]:
                sudoShellCommand(command)
                time.sleep(1)

    # Check if the adaptor exists
    if (getAddrOfAdaptor(tapAdaptor,'MAC',exitIfNoAddr=False) == 'NotAnAddress'):
        printAndLog (f"configTapAdaptor: <{tapAdaptor}> was never configured. Configuring...",doPrint=False)
        configCommands = ['create','config','natSetup']
        if (isEqSetting('pvAWS','firesim')):
            configCommands.insert(-1,'disableIpv6') #insert before natSetup
        execSudoCommands(configCommands)
    else:
        # was created --> re-configure
        execSudoCommands(['refresh','config'])

    # Check configuration
    if (getAddrOfAdaptor(tapAdaptor,'IP') != getSetting('awsf1IpHost')):
        logAndExit(f"configTapAdaptor: The <{tapAdaptor}> IP does not match <{getSetting('awsf1IpHost')}>",exitCode=EXIT.Network)
    if (getAddrOfAdaptor(tapAdaptor,'MAC') != getSetting('awsf1TapAdaptorMacAddress')):
        logAndExit(f"configTapAdaptor: The <{tapAdaptor}> MAC address does not match <{getSetting('awsf1TapAdaptorMacAddress')}>",exitCode=EXIT.Network)

    if (isEqSetting('pvAWS','firesim')):
        # The adaptor needs to be DOWN for firesim
        execSudoCommands(['down'])

    printAndLog (f"awsf1.configTapAdaptor: <{tapAdaptor}> is properly configured.",doPrint=False)

@decorate.debugWrap
def programAFI(doPrint=True):
    """ perform AFI Management Commands for f1.2xlarge """
    agfiId = getSetting("agfiId")
    clearFpgas(doPrint=doPrint)
    flashFpgas(agfiId,doPrint=doPrint)

@decorate.debugWrap
def _sendKmsg(message):
    """send message to /dev/kmsg"""
    # TODO: replace all whitespace with underscores?
    command = f"echo \"{message}\" | sudo tee /dev/kmsg"
    shellCommand(command, check=False, shell=True)

@decorate.debugWrap
@decorate.timeWrap
def _poll_command(command, trigger, maxTimeout=10):
    for i in range(maxTimeout):
        out = subprocess.getoutput(command)
        if trigger not in out:
            time.sleep(1)
        else:
            return
    logAndExit(f"<awsf1._poll_command>: command <{command}> timed out <{maxTimeout} attempts> on trigger <{trigger}>")

@decorate.debugWrap
def clearFpga(slotno):
    """clear FPGA in a given slot id and wait until finished """
    _sendKmsg(f"about to clear fpga {slotno}")
    shellCommand(['fpga-clear-local-image','-S',f"{slotno}",'-A'])
    _sendKmsg(f"done clearing fpga {slotno}")

    # wait until the FPGA has been cleared
    _sendKmsg(f"checking for fpga slot {slotno}")
    _poll_command(f"fpga-describe-local-image -S {slotno} -R -H", "cleared")
    _sendKmsg(f"done checking fpga slot {slotno}")

@decorate.debugWrap
def getNumFpgas():
    """return number of FPGAS"""
    try:
        out = subprocess.check_output("fpga-describe-local-image-slots".split())
        out = out.decode('utf-8')
    except Exception as exc:
        logAndExit(f'<awsf1.getNumFpgas>: error getting fpga local slot description', exc=exc, exitCode=EXIT.Run)
    lines = out.split('\n')[:-1]

    #check that the output is an AFIDEVICE
    regexPattern = r'(AFIDEVICE\s+\w\s+\w+\s+\w+\s+.*)'
    for l in lines:
        if not bool(re.match(regexPattern, l)):
            logAndExit(f'<awsf1.getNumFpgas>: unknown output for fpga-describe-local-image-slots <{l}>')
    numLines = len(lines)
    return numLines

@decorate.debugWrap
def clearFpgas(doPrint=True):
    """ clear ALL FPGAs """
    numFpgas = getNumFpgas()
    printAndLog(f"<awsf1.clearFpgas>: Found {numFpgas} FPGA(s) to clear",doPrint=doPrint)
    for sn in range(numFpgas):
        clearFpga(sn)

@decorate.debugWrap
def flashFpga(agfi, slotno):
    """flash FPGA in a given slot with a given AGFI ID and wait until finished """
    # fpgaLoadExtraSettings may be specified in agfi_id.json
    fpgaLoadExtraSettings = getSetting('fpgaLoadExtraSettings', default=[])
    shellCommand(['fpga-load-local-image','-F','-S',f"{slotno}",'-I', agfi,'-A'] + fpgaLoadExtraSettings)

    # wait until the FPGA has been flashed
    _poll_command(f"fpga-describe-local-image -S {slotno} -R -H", "loaded")

@decorate.debugWrap
def flashFpgas(agfi,doPrint=True):
    """
    NOTE: FireSim documentation came with a note. If an instance is chosen that has more than one FPGA, leaving one
    in a cleared state can cause XDMA to hang. Accordingly, it is advised to flash all the FPGAs in a slot with
    something. This method might need to be extended to flash all available slots with our AGFI
    """
    printAndLog(f"<awsf1.flashFpgas>: Flashing FPGAs with agfi: {agfi}.",doPrint=doPrint)
    numFpgas = getNumFpgas()
    printAndLog(f"<awsf1.flashFpgas>: Found {numFpgas} FPGA(s) to flash",doPrint=doPrint)
    for sn in range(numFpgas):
        flashFpga(agfi, sn)

def getAgfiId(jsonFile):
    keyName = 'agfi_id'
    contents = safeLoadJsonFile(jsonFile)
    if keyName not in contents:
        logAndExit(f"<awsf1.getAgfiJson>: unable to find key <agfi_id> in {jsonFile}")
    return contents[keyName]

def getAgfiSettings(jsonFile):
    contents = safeLoadJsonFile(jsonFile)
    return contents

def copyAWSSources():
    pvAWS = getSetting('pvAWS')

    if pvAWS not in ['firesim', 'connectal']:
        logAndExit(f"<awsf1.copyAWSSources>: called with incompatible AWS PV \"{pvAWS}\"")

    if (isEnabled('useCustomProcessor')):
        awsSourcePath = getSetting('pathToCustomProcessorSource')
    else:
        awsSourcePath = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'),
                                 'bitfiles', pvAWS, getSetting('processor'))

    awsWorkPath = os.path.join(getSetting("workDir"), pvAWS)

    # populate workDir with available subdirectories
    try:
        subdirectories = [os.path.join(awsSourcePath, o) for o in os.listdir(awsSourcePath) if os.path.isdir(os.path.join(awsSourcePath,o))]
        if len(subdirectories) > 0:
            mkdir(awsWorkPath,addToSettings=f'{pvAWS}Path')
            for awsDirPath in subdirectories:
                copyDir(os.path.join(awsSourcePath, awsDirPath), awsWorkPath)
    except Exception as exc:
        logAndExit(f"<awsf1.copyAWSSources>: error populating subdirectories of AWS PV {pvAWS}", exc=exc, exitCode=EXIT.Files_and_paths)

    # aws resources need an image file:
    imageFile = os.path.join(getSetting('osImagesDir'), f"{getSetting('osImage')}.img")
    setSetting("osImageImg",imageFile)
    if (isEqSetting('osImage','FreeRTOS')): # create a filesystem -- 256MB [Note that size >=256MB (for mkfs.fat 4.1, but for v.3.0 has to be >256Mb)]
        shellCommand(['dd','if=/dev/zero',f"of={imageFile}",'bs=256M','count=1'])
        shellCommand(['mkfs.vfat','-S','512','-n',"\"DATA42\"",'-F','32', imageFile])
    else: #an empty file will do
        touch(imageFile)

    # extract the agfi and put it in setting
    agfiJsonPath = os.path.join(awsSourcePath, 'agfi_id.json')
    agfiSettings = getAgfiSettings(agfiJsonPath)
    setSetting('agfiId', agfiSettings['agfi_id'])
    for k in agfiSettings:
        if k == "_afgi-id.json":
            continue
        setSetting(k, agfiSettings[k])

@decorate.debugWrap
def removeKernelModules():
    # Firesim:  ['xocl', 'xdma', 'edma', 'nbd']
    # Connectal: ['xocl', 'xdma', 'pcieportal', 'portalmem']
    # For production (i.e. on a fresh instance), it doesn't matter to remove the _other_ modules
    # However, for dev, the _other_ modules interfere. Deleting them works.
    kmodsToClean = ['xocl', 'xdma', 'edma', 'nbd', 'pcieportal', 'portalmem']
    for kmod in kmodsToClean:
        sudoShellCommand(['rmmod', kmod],check=False)
        _sendKmsg (f"<awsf1.removeKernelModules>: Removing {kmod} if it exists.")

@decorate.debugWrap
def installKernelModules():
    """install necessary kernel modules for an AWS PV"""
    awsModPath = os.path.join(getSetting(f'{getSetting("pvAWS")}Path'), 'kmods')

    #load our modules
    if (isEqSetting('pvAWS','firesim')):
        sudoShellCommand(['insmod', f"{awsModPath}/nbd.ko", 'nbds_max=128'])
        _sendKmsg (f"FETT-firesim: Installing nbd.ko.")
        sudoShellCommand(['insmod', f"{awsModPath}/xdma.ko", 'poll_mode=1'])
        _sendKmsg (f"FETT-firesim: Installing xdma.ko.")

    elif (isEqSetting('pvAWS', 'connectal')):
        sudoShellCommand(['insmod', f"{awsModPath}/pcieportal.ko"])
        _sendKmsg (f"FETT-connectal: Installing pcieportal.ko.")
        sudoShellCommand(['insmod', f"{awsModPath}/portalmem.ko"])
        _sendKmsg (f"FETT-connectal: Installing portalmem.ko.")
        ## make the connectal device nodes accessible to non-root users
        sudoShellCommand(['bash', '-c', 'chmod agu+rw /dev/portal* /dev/connectal'])
    else:
        logAndExit(f"<awsf1.installKernelModules> not implemented for <{getSetting('pvAWS')}> PV.",exitCode=EXIT.Implementation)

# ------------------ FireSim Functions ----------------------------------------

def prepareFiresim():
    """prepare the firesim binaries for the FETT work directory"""
    copyAWSSources()

    if isEqSetting('osImage', 'debian'):
        nixImage = getSettingDict('nixEnv', ['debian-rootfs', 'firesim'])
        if isEqSetting('binarySource', 'GFE') and nixImage in os.environ:
            imageSourcePath = os.environ[nixImage]
        else:
            imageSourcePath = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'), 'osImages', 'firesim', 'debian.img.zst')
        imageFile = os.path.join(getSetting('osImagesDir'), 'debian.img')
        zstdDecompress(imageSourcePath, imageFile)
        try:
            os.chmod(imageFile, 0o664) # If the image was copied from the Nix store, it was read-only
        except Exception as exc:
            logAndExit(f"Could not change permissions on file {imageFile}", exc=exc, exitCode=EXIT.Files_and_paths)

    dwarfFile = os.path.join(getSetting('osImagesDir'), f"{getSetting('osImage')}.dwarf")
    setSetting("osImageDwarf",dwarfFile)
    touch(dwarfFile)

# ------------------ Connectal Functions ----------------------------------------

def prepareConnectal():
    """connectal environment preparation"""
    copyAWSSources()

    imageDir = getSetting('osImagesDir')
    pvAWS = "connectal"
    
    if isEqSetting('binarySource', 'MIT') and isEqSetting('osImage', 'debian'):
        # extraFiles may be specified in agfi_id.json
        extraFiles = getSetting('extraFiles', default=[])
        for extraFile in extraFiles:
            dname = os.path.dirname(extraFile)
            bname = os.path.basename(extraFile)
            if dname == 'osImages':
                srcname = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'), 'osImages', 'connectal', bname)
                dstname = os.path.join(getSetting('osImagesDir'), bname)
                cp (srcname, dstname)
            else:
                warnAndLog(f"unhandled directory for extra file {extraFile}")

        imageSourcePath = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'),
                                       'osImages', pvAWS, "debian.img")
        imageFile = os.path.join(imageDir, f"{getSetting('osImage')}.img")
        cp(imageSourcePath, imageFile)

    elif isEqSetting('binarySource', 'SRI-Cambridge'):
        imageSourcePath = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'),
                'osImages', 'common', f"disk-image-cheri{getSetting('SRI-Cambridge-imageVariantSuffix')}.img.zst")
        imageFile = os.path.join(imageDir, f"{getSetting('osImage')}.img")
        zstdDecompress(imageSourcePath, imageFile)

    elif isEqSetting('binarySource', 'GFE') and isEqSetting("osImage", "FreeBSD"):
        imageSourcePath = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'),
                                       'osImages', 'connectal', "freebsd.img.zst")
        imageFile = os.path.join(imageDir, f"{getSetting('osImage')}.img")
        zstdDecompress(imageSourcePath, imageFile)
 
    # connectal requires a device tree blob
    dtbsrc = os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'), 'osImages', 'connectal', "devicetree.dtb")
    dtbFile = os.path.join(getSetting('osImagesDir'), 'devicetree.dtb')
    setSetting("osImageDtb",dtbFile)
    cp (dtbsrc, dtbFile)

# ------------------ Monitoring Functions ----------------------------------------

@decorate.debugWrap
def startRemoteLogging (target):
    printAndLog ("Setting up remote logging ...")

    if (not target.restartMode):
        # clear the directory for non-fresh instances
        sudoShellCommand(['rm','-rf',f'/var/log/{target.ipTarget}'],check=False)

    # configure target rsyslog
    if (isEqSetting('osImage','debian')):
        if (not target.restartMode):
            # prepare the logTuples to create the conf file
            syslogsFiles = ['alternatives.log','bootstrap.log','debug','kern.log','btmp',
                        'dpkg.log','lastlog','syslog','auth.log','daemon.log','faillog','messages','wtmp']
            syslogs = [f"/var/log/{syslog}" for syslog in syslogsFiles]
            logTuples = [(xPath,os.path.splitext(os.path.basename(xPath))[0]) for xPath in syslogs]
            if (webserver in target.appModules):
                weblogs = getSetting("webserverLogs")
                logTuples += [(f"{weblogs['root']}/{logFile}",f"nginx_{os.path.splitext(logFile)[0]}") for logFile in weblogs["logs"]]

            # Create conf file
            syslogConfName = "logFett.conf"
            syslogConfFile = ftOpenFile(os.path.join(getSetting('workDir'),syslogConfName),'w')
            syslogConfFile.write('module(load="imfile")\n')
            syslogConfFile.write('\nruleset(name="sendToLogserver") {\n')
            syslogConfFile.write(f'\taction(type="omfwd" Target="{target.ipHost}" Port="{getSetting("rsyslogPort")}" Protocol="udp")\n')
            syslogConfFile.write('}\n')
            for logPath, logTag in logTuples:
                syslogConfFile.write('\ninput(type="imfile"\n')
                syslogConfFile.write(f'\tfile="{logPath}"\n')
                syslogConfFile.write(f'\tTag="{logTag}:"\n')
                syslogConfFile.write(f'\tRuleset="sendToLogserver")\n')
            syslogConfFile.close()

            # send the conf file
            target.sendFile(
                    getSetting('workDir'), syslogConfName,
                    toTarget=True, exitOnError=False
                )
            target.runCommand(f"mv {syslogConfName} /etc/rsyslog.d/",exitOnError=False)

        # restart rsyslog
        target.runCommand("service rsyslog restart",exitOnError=False)

    elif (isEqSetting('osImage','FreeBSD')):
        if (not target.restartMode):
            # configure syslogd to use the UDP port
            target.runCommand(f'echo "*.*     @{target.ipHost}:{getSetting("rsyslogPort")}" > /etc/syslog.d/logFett.conf')
        target.runCommand("service syslogd restart")
        
        if (webserver in target.appModules):
            nginxSrc = '/usr/local' if (not isEqSetting('binarySource','SRI-Cambridge')) else '/fett'
            nginxService = 'nginx' if (not isEqSetting('binarySource','SRI-Cambridge')) else 'fett_nginx'

            remoteLogsCommands = (f'access_log syslog:server={target.ipHost}:{getSetting("rsyslogPort")},tag=nginx_access,'
            f'severity=info;\\nerror_log syslog:server={target.ipHost}:{getSetting("rsyslogPort")},tag=nginx_error,'
            f'severity=debug;\\n')

            if (not target.restartMode):
                target.runCommand(f'printf "{remoteLogsCommands}" > {nginxSrc}/nginx/conf/sites/remoteLogFett.conf',erroneousContents=["Unmatched", "No such file or directory"])
            target.runCommand(f"service {nginxService} restart")
         
    printAndLog ("Setting up remote logging is _supposedly_ complete.")

@decorate.debugWrap
def startUartPiping(target):
    try:
        target.uartSocatProc = subprocess.Popen(
            ['socat', 'STDIO,ignoreeof', f"TCP-LISTEN:{getSetting('uartFwdPort')},reuseaddr,fork,max-children=1"],
            stdout=target.process.child_fd,stdin=target.process.child_fd,stderr=target.process.child_fd)
    except Exception as exc:
        target.shutdownAndExit(f"startUartPiping: Failed to start the listening process.",exc=exc,exitCode=EXIT.Run)

@decorate.debugWrap
def endUartPiping(target):
    try:
        target.uartSocatProc.kill() # No need for fancier ways as we use Popen with shell=False
    except Exception as exc:
        warnAndLog("endUartPiping: Failed to kill the listening process.",doPrint=False,exc=exc)

