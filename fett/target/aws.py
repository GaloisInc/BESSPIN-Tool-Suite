import pexpect, psutil, getpass
from fett.target.common import *
from fett.target import fpga

class firesimTarget(commonTarget):
    def __init__(self):

        super().__init__()

        self.switch0Proc = None

        self.fswitchOut = None
        self.switch0timing = ['6405', '10', '200'] # dictated by cloudGFE

        self.rootPassword = 'firesim'

    @decorate.debugWrap
    @decorate.timeWrap
    def boot(self,endsWith="login:",timeout=90):

        # 1. Switch0
        self.fswitchOut = ftOpenFile(os.path.join(getSetting('workDir'),'switch0.out'),'a')
        self.switch0Proc = subprocess.Popen(['sudo', './switch0']+self.switch0timing,
                                            stdout=self.fswitchOut, stderr=self.fswitchOut,
                                            cwd=getSetting("awsFiresimSimPath"), preexec_fn=os.setpgrp)

        # 2. fsim
        imageFile = os.path.join(getSetting("awsFiresimSimPath"), "linux-uniform0-br-base.img")
        dwarfFile = os.path.join(getSetting("awsFiresimSimPath"), "linux-uniform0-br-base-bin-dwarf")
        firesimCommand = ' '.join([
            'sudo',
            "LD_LIBRARY_PATH={}:$LD_LIBRARY_PATH".format(getSetting("awsFiresimSimPath")),
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
            '+slotid=0',
            '+profile-interval=-1',
            f"+macaddr0={getSetting('awsTargetMacAddress')}",
            f"+blkdev0={imageFile}",
            f"+niclog0={os.path.join(getSetting('workDir'),'niclog0.out')}",
            f"+blkdev-log0={os.path.join(getSetting('workDir'),'blkdev-log0.out')}",
            '+trace-select0=1',
            '+trace-start0=0',
            '+trace-end0=-1',
            '+trace-output-format0=0',
            f"+dwarf-file-name0={dwarfFile}",
            '+autocounter-readrate0=0',
            f"+autocounter-filename0={os.path.join(getSetting('workDir'),'AUTOCOUNTERFILE0.out')}",
            f"+linklatency0={self.switch0timing[0]}",
            f"+netbw0={self.switch0timing[2]}",
            '+shmemportname0=0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
            '+permissive-off',
            getSetting("osImageElf")
        ])
        logging.debug(f"boot: firesimCommand = {firesimCommand}")
        self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),'tty.out'),'ab')

        try:
            self.ttyProcess = pexpect.spawn(firesimCommand,logfile=self.fTtyOut,timeout=30,
                                        cwd=getSetting("awsFiresimSimPath"))
            self.process = self.ttyProcess
            time.sleep(1)
            self.expectFromTarget(endsWith,"Booting",timeout=timeout,overwriteShutdown=True)
        except Exception as exc:
            self.shutdownAndExit(f"boot: Failed to spawn the firesim process.",overwriteShutdown=True,exc=exc,exitCode=EXIT.Run)

        # The tap needs to be turned up AFTER booting
        getTapAdaptorUp ()

    def interact(self):
        printAndLog (f"Entering interactive mode. Root password: \'{self.rootPassword}\'. Press \"Ctrl + C\" to exit.")
        super().interact()

    def runCommand (self,command,endsWith=None,expectedContents=None, **kwargs):
        """ this is for the firesim debian build, but not the ones FETT will use """
        # TODO: ELEW use actual images and remove
        if endsWith is None:
            if isEqSetting('osImage','debian'):
                if (self.isCurrentUserRoot):
                    endsWith = "#"
        return super().runCommand(command, endsWith=endsWith, **kwargs)

    @decorate.debugWrap
    @decorate.timeWrap
    def activateEthernet(self):
        return

    @decorate.debugWrap
    def targetTearDown(self):
        try:
            subprocess.check_call(['sudo', 'kill', f"{os.getpgid(self.switch0Proc.pid)}"],
                                stdout=self.fswitchOut, stderr=self.fswitchOut)
        except Exception as exc:
            warnAndLog("targetTearDown: Failed to kill <switch0> process.",doPrint=False,exc=exc)
        try:
            self.fswitchOut.close()
        except Exception as exc:
            warnAndLog("targetTearDown: Failed to close <switch0.out>.",doPrint=False,exc=exc)
        return True

@decorate.debugWrap
def configTapAdaptor():
    tapAdaptor = getSetting('awsTapAdaptorName')

    def getMainAdaptor():
        for xAdaptor in psutil.net_if_addrs():
            if (xAdaptor not in ['lo', tapAdaptor]):
                return xAdaptor
        logAndExit(f"configTapAdaptor: Failed to find the main Eth adaptor.",exitCode=EXIT.Network)

    commands = {
        'create' : [
            ['ip', 'tuntap', 'add', 'mode', 'tap', 'dev', tapAdaptor, 'user', getpass.getuser()]
        ],
        'natSetup' : [
            ['sysctl', '-w', 'net.ipv6.conf.tap0.disable_ipv6=1'],
            ['sysctl', '-w', 'net.ipv4.ip_forward=1'],
            ['iptables', '-A', 'FORWARD', '-i', getMainAdaptor(), '-o', tapAdaptor, '-m', 'state',
                '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'],
            ['iptables', '-A', 'FORWARD', '-i', tapAdaptor, '-o', getMainAdaptor(), '-j', 'ACCEPT'],  
            ['iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', getMainAdaptor(), '-j', 'MASQUERADE']  
        ],
        'refresh' : [
            ['ip', 'addr', 'flush', 'dev', tapAdaptor]
        ],
        'config' : [
            ['ip','addr','add',f"{getSetting('awsIpHost')}/24",'dev',tapAdaptor],
            ['ifconfig', tapAdaptor, 'hw', 'ether', getSetting('awsTapAdaptorMacAddress')],
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
    if (fpga.getAddrOfAdaptor(tapAdaptor,'MAC',exitIfNoAddr=False) == 'NotAnAddress'):
        printAndLog (f"configTapAdaptor: <{tapAdaptor}> was never configured. Configuring...",doPrint=False)
        execSudoCommands(['create','config','natSetup'])
    else:
        # was created --> re-configure
        execSudoCommands(['refresh','config'])

    # Check configuration
    if (fpga.getAddrOfAdaptor(tapAdaptor,'IP') != getSetting('awsIpHost')):
        logAndExit(f"configTapAdaptor: The <{tapAdaptor}> IP does not match <{getSetting('awsIpHost')}>",exitCode=EXIT.Network)
    if (fpga.getAddrOfAdaptor(tapAdaptor,'MAC') != getSetting('awsTapAdaptorMacAddress')):
        logAndExit(f"configTapAdaptor: The <{tapAdaptor}> MAC address does not match <{getSetting('awsTapAdaptorMacAddress')}>",exitCode=EXIT.Network)

    if (isEqSetting('pvAWS','firesim')):
        # The adaptor needs to be DOWN for firesim
        execSudoCommands(['down'])

    printAndLog (f"aws.configTapAdaptor: <{tapAdaptor}> is properly configured.",doPrint=False)

@decorate.debugWrap
def programAFI():
    """ perform AFI Management Commands for f1.2xlarge """
    agfiId = 'agfi-009b6afeef4f64454'
    clearFpgas()
    flashFpgas(agfiId)

@decorate.debugWrap
def getTapAdaptorUp ():
    sudoShellCommand(['ip','link','set', 'dev', getSetting('awsTapAdaptorName'), 'up'])

@decorate.debugWrap
def setupKernelModules():
    if (isEqSetting('pvAWS','firesim')):
        #remove all modules to be safe
        kmodsToClean = ['xocl', 'xdma', 'edma', 'nbd']
        for kmod in kmodsToClean:
            sudoShellCommand(['rmmod', kmod],checkCall=False)
            _sendKmsg (f"FETT-firesim: Removing {kmod} if it exists.")

        #load our modules
        sudoShellCommand(['insmod', f"{getSetting('awsFiresimModPath')}/nbd.ko", 'nbds_max=128'])
        _sendKmsg (f"FETT-firesim: Installing nbd.ko.")
        sudoShellCommand(['insmod', f"{getSetting('awsFiresimModPath')}/xdma.ko", 'poll_mode=1'])
        _sendKmsg (f"FETT-firesim: Installing xdma.ko.")
    else:
        logAndExit(f"<setupKernelModules> not implemented for <{getSetting('pvAWS')}> PV.",exitCode=EXIT.Implementation)

@decorate.debugWrap
def _runCommandAndLog(command, stdout=None, stderr=None, shell=False, **kwargs):
    """ run and log a simple command, treating all exceptions as terminal errors """

    def logDetailsString():
        if stdout is None and stderr is None:
            return ""
        else:
            stdoutStr = f"{stdout.name} for stdout " if stdout is not None else ""
            stderrStr = f"{stderr.name} for stderr " if stderr is not None else ""
            joinStr = "and " if stdout is not None and stderr is not None else ""
            return "Check " + stdoutStr + joinStr + stderrStr + " for more details"
    if ((type(command) is str) and (not shell)): #if shell=True, do not split
        command = command.split()
    
    try:
        subprocess.run(command, stdout=stdout, stderr=stderr, shell=shell, **kwargs)
    except Exception as exc:
            logAndExit (f"<aws._runCommandAndLog>: Failed on <{command}>." + logDetailsString())

@decorate.debugWrap
def _sendKmsg(message):
    """send message to /dev/kmsg"""
    # TODO: replace all whitespace with underscores?
    sudoOut = ftOpenFile(os.path.join(getSetting('workDir'),'sudo.out'),'a')
    command = f"echo \"{message}\" | sudo tee /dev/kmsg"
    _runCommandAndLog(command, stdout=sudoOut, stderr=sudoOut,check=False,shell=True)
    sudoOut.close()

@decorate.debugWrap
@decorate.timeWrap
def _poll_command(command, trigger, maxTimeout=10):
    for i in range(maxTimeout):
        out = subprocess.getoutput(command)
        if trigger not in out:
            time.sleep(1)
        else:
            return
    logAndExit(f"<aws._poll_command>: command <{command}> timed out <{maxTimeout} attempts> on trigger <{trigger}>")

@decorate.debugWrap
def clearFpga(slotno):
    """clear FPGA in a given slot id and wait until finished """
    _sendKmsg(f"about to clear fpga {slotno}")
    _runCommandAndLog(f"sudo fpga-clear-local-image -S {slotno} -A")
    _sendKmsg(f"done clearing fpga {slotno}")

    # wait until the FPGA has been cleared
    _sendKmsg(f"checking for fpga slot {slotno}")
    _poll_command(f"sudo fpga-describe-local-image -S {slotno} -R -H", "cleared")
    _sendKmsg(f"done checking fpga slot {slotno}")

@decorate.debugWrap
def getNumFpgas():
    """return number of FPGAS"""
    try:
        out = subprocess.check_output("sudo fpga-describe-local-image-slots".split())
        out = out.decode('utf-8')
    except Exception as exc:
        logAndExit(f'<aws.getNumFpgas>: error getting fpga local slot description', exc=exc)
    lines = out.split('\n')[:-1]

    #check that the output is an AFIDEVICE
    regexPattern = r'(AFIDEVICE\s+\w\s+\w+\s+\w+\s+.*)'
    for l in lines:
        if not bool(re.match(regexPattern, l)):
            logAndExit(f'<aws.getNumFpgas>: unknown output for fpga-describe-local-image-slots <{l}>')
    numLines = len(lines)
    return numLines

@decorate.debugWrap
def clearFpgas():
    """ clear ALL FPGAs """
    numFpgas = getNumFpgas()
    printAndLog(f"<aws.clearFpgas>: Found {numFpgas} FPGA(s) to clear")
    for sn in range(numFpgas):
        clearFpga(sn)

@decorate.debugWrap
def flashFpga(agfi, slotno):
    """flash FPGA in a given slot with a given AGFI ID and wait until finished """
    _runCommandAndLog(f"sudo fpga-load-local-image -S {slotno} -I {agfi} -A")

    # wait until the FPGA has been flashed
    _poll_command(f"sudo fpga-describe-local-image -S {slotno} -R -H", "loaded")

@decorate.debugWrap
def flashFpgas(agfi):
    """
    NOTE: FireSim documentation came with a note. If an instance is chosen that has more than one FPGA, leaving one
    in a cleared state can cause XDMA to hang. Accordingly, it is advised to flash all the FPGAs in a slot with
    something. This method might need to be extended to flash all available slots with our AGFI
    """
    printAndLog(f"<aws.flashFpgas>: Flashing FPGAs with agfi: {agfi}.")
    numFpgas = getNumFpgas()
    printAndLog(f"<aws.flashFpgas>: Found {numFpgas} FPGA(s) to flash")
    for sn in range(numFpgas):
        flashFpga(agfi, sn)
