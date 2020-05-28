import pexpect
from fett.target.common import *
from fett.target import fpga
from subprocess import getoutput

class firesimTarget(commonTarget):
    def __init__(self):

        super().__init__()

        self.switch0Proc = None

        self.fswitchOut = None
        self.switch0timing = ['6405', '10', '200'] # dictated by cloudGFE

        self.rootPassword = 'firesim'

    @decorate.debugWrap
    def interact(self):
        pass

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
            self.expectFromTarget(endsWith,"Booting",timeout=timeout)
        except Exception as exc:
            self.shutdownAndExit(f"boot: Failed to spawn the firesim process.",overwriteShutdown=True,exc=exc,exitCode=EXIT.Run)

        # The tap needs to be turned up AFTER booting
        getTapAdaptorUp ()

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
    commands = {
        'config' : [
            ['ip', 'addr', 'flush', 'dev', getSetting('awsTapAdaptorName')],
            ['ip','addr','add',f"{getSetting('awsIpHost')}/24",'dev',getSetting('awsTapAdaptorName')],
            ['ifconfig', getSetting('awsTapAdaptorName'), 'hw', 'ether', getSetting('awsTapAdaptorMacAddress')],
        ],
        'down' : [
            ['ip','link','set', getSetting('awsTapAdaptorName'), 'down'],
        ]
    }
    # First, configure
    for command in commands['config']:
        sudoShellCommand(command)
        time.sleep(1)

    # second, check configuration
    if (fpga.getAddrOfAdaptor(getSetting('awsTapAdaptorName'),'IP') != getSetting('awsIpHost')):
        logAndExit(f"configTapAdaptor: The <{getSetting('awsTapAdaptorName')}> IP does not match <{getSetting('awsIpHost')}>",exitCode=EXIT.Network)
    if (fpga.getAddrOfAdaptor(getSetting('awsTapAdaptorName'),'MAC') != getSetting('awsTapAdaptorMacAddress')):
        logAndExit(f"configTapAdaptor: The <{getSetting('awsTapAdaptorName')}> MAC address does not match <{getSetting('awsTapAdaptorMacAddress')}>",exitCode=EXIT.Network)

    # Third, take the adaptor DOWN for firesim
    for command in commands['down']:
        sudoShellCommand(command)
        time.sleep(1)

    printAndLog (f"aws.configTapAdaptor: <{getSetting('awsTapAdaptorName')}> is properly configured.",doPrint=False)

@decorate.debugWrap
def programAFI():
    warnAndLog("programAFI: This is to be properly implemented.")
    commands = [
        ['fpga-clear-local-image', '-S', '0'],
        ['fpga-load-local-image', '-S', '0', '-I', 'agfi-009b6afeef4f64454']
    ]

    for command in commands:
        sudoShellCommand(command)
        time.sleep(1)

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
def _sendKmsg(message):
    """send message to /dev/kmsg"""
    command = f"echo \"{message}\" | sudo tee /dev/kmsg"
    sudoOut = ftOpenFile(os.path.join(getSetting('workDir'),'sudo.out'),'a')
    try:
        subprocess.run(command,stdout=sudoOut,stderr=sudoOut,check=False,shell=True)
    except Exception as exc:
        logAndExit (f"sudo: Failed to send a message to </dev/kmsg>. Check <sudo.out> for more details.",exc=exc,exitCode=EXIT.Run)
    sudoOut.close()   


