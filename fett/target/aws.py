import pexpect
from fett.target.common import *
from subprocess import getoutput

class firesimTarget(commonTarget):
    def __init__(self):
        super().__init__()
        self.gfeOutPath = os.path.join(getSetting('workDir'),'gfe.out')
        self.screens = {'fsim0': None,
                        'switch0': None,
                        'bootcheck': None}
        self.rootPassword = 'firesim'

    @decorate.debugWrap
    def interact(self):
        pass

    def quitAllScreens(self):
        screens = getScreenSessions()
        for s in screens:
            quitScreenSession(s)

    @decorate.debugWrap
    @decorate.timeWrap
    def boot(self,endsWith="login:",timeout=90):
        """ process
        1. ensure/install kernel modules
        2. check the network config -- tap interface and NAT
        3. clear the FPGA slot and load AFI
        4. detach screens
        5. start switch
        6. start bootcheck
        7. start fsim0
        """
        self.quitAllScreens()
        simPath = getSetting("awsFiresimSimPath")

        # TODO: ELEW using a shell setup - ew
        # run_sim.sh was modded by adding -d to screen Firesim-f1, so we can
        # attach a process separately
        runSimCommand = os.path.join(simPath, "run_sim.sh")
        imageFile = os.path.join(simPath, "linux-uniform0-br-base.img")
        dwarfFile = os.path.join(simPath, "linux-uniform0-br-base-bin-dwarf")
        elfFile = getSetting("osImageElf")
        owd = os.getcwd()
        os.chdir(simPath)
        output = getoutput(f"{runSimCommand} {imageFile} {dwarfFile} {elfFile}")
        os.chdir(owd)

        print(output)
        fsimSession = getScreenSessionName("fsim0")
        printAndLog(f"<target.boot> found {fsimSession} session to use as process")
        self.screens['fsim0'] = pexpect.spawn(f"screen -r {fsimSession}")
        self.process = self.screens['fsim0']

        time.sleep(1)
        self.expectFromTarget(endsWith, "Booting", timeout=timeout)

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
        return True

def getScreenSessions():
    """get all screen sessions currently available"""
    listCommand = "screen -ls"
    return [l.split()[0] for l in getoutput(listCommand).split('\n') if "\t" in l or ".".join(l.split(".")[1:]).split("\t")[0]]

def getScreenSessionName(name):
    """ given session name, find the session currently available (permissive function)"""
    for s in getScreenSessions():
        if name in s:
            return s
    return None

def quitScreenSession(name):
    """ quit session, if it's available (permissive function)"""
    sname = getScreenSessionName(name)
    if sname is not None:
        printAndLog(f"quitScreenSession: found {sname} to quit")
        quitCommand = f"screen -X -S {sname} quit"
        output = getoutput(quitCommand)
        # TODO: ELEW sanity check this?
