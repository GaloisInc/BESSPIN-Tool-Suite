#! /usr/bin/env python3
""" 
Main qemu class + misc qemu functions
"""

from fett.base.utils.misc import *
from fett.target.common import *
import psutil, socket

class qemuTarget (commonTarget):
    def __init__ (self, targetId=None):
        
        super().__init__(targetId=targetId)
        
        self.ipTarget = getSetting('qemuIpTarget',targetId=self.targetId)
        self.ipHost = getSetting('qemuIpHost',targetId=self.targetId)

        return

    @decorate.debugWrap
    @decorate.timeWrap
    def boot (self,endsWith="login:",timeoutDict={"boot":90}): #no need to use targetObj as we'll never boot in non-reboot mode
        self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),f'tty{self.targetSuffix}.out'),'ab') #has to be bytes, if we use a filter, interact() does not work (pexpect bug)
        timeout = self.parseBootTimeoutDict (timeoutDict)
        if (self.osImage in ['debian', 'FreeBSD']):

            qemuCommand  = f"qemu-system-riscv64 -nographic -machine virt -m 4G -kernel {getSetting('osImageElf',targetId=self.targetId)}"
            qemuCommand += f" -device virtio-net-device,netdev=usernet"
            qemuCommand += f" -netdev tap,id=usernet,ifname={getSetting('tapAdaptor',targetId=self.targetId)},script=no,downscript=no"
            if (self.osImage=='debian'):
                qemuCommand += " -append \"console=ttyS0\""
                # As mentioned in #799, FreeBSD does not seem to make use of this device by default.
                # As mentioned in #864, this device prevents FreeBSD from booting on <Debian 10 Buster, kernel 4.19> for some reason.
                # Ticket #333 is still open, and it covers this entropy/rng situation.
                qemuCommand += " -device virtio-rng-device"

            try:
                self.ttyProcess = pexpect.spawn(qemuCommand,logfile=self.fTtyOut,timeout=timeout)
                self.process = self.ttyProcess
                self.expectFromTarget(endsWith,"Booting",timeout=timeout,overrideShutdown=True)
            except Exception as exc:
                self.terminateAndExit(f"boot: Failed to spwan the qemu process.",overrideShutdown=True,exc=exc,exitCode=EXIT.Run)
        elif (self.osImage=='FreeRTOS'):
            qemuCommand = "qemu-system-riscv32 -nographic -machine sifive_e -kernel " + getSetting('osImageElf',targetId=self.targetId)
            try:
                self.process = pexpect.spawn(qemuCommand,timeout=timeout,logfile=self.fTtyOut)
            except Exception as exc:
                self.terminateAndExit("Error in {0}: Failed to spawn the qemu process.".format(self.filename),
                    overrideShutdown=True,exc=exc,exitCode=EXIT.Run)
            time.sleep(1)
            textBack,wasTimeout,idxReturn = self.expectFromTarget(endsWith,"Booting",timeout=timeout,exitOnError=False,overrideShutdown=True)
            if (idxReturn==1): #No "">>> End Of Testgen <<<", but qemu aborted without a timeout
                self.fTtyOut.write (b"\n<QEMU ABORTED>\n")
            else:
                self.fTtyOut.write (b"\n") #because the last expect does not include an end of line
            self.fTtyOut.flush()
            #Will terminate here as well because it is easier, and there is currently no other options -- might change
            self.sendToTarget ("\x01x")
        else:
            self.terminateAndExit(f"boot: <{self.osImage}> is not implemented on <{self.target}>.",overrideShutdown=True,exitCode=EXIT.Implementation)
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def activateEthernet (self): #no need to use targetObj as we'll never activate ethernet in non-reboot mode
        if (self.osImage=='debian'):
            self.runCommand ("echo \"auto eth0\" > /etc/network/interfaces")
            self.runCommand ("echo \"iface eth0 inet static\" >> /etc/network/interfaces")
            self.runCommand (f"echo \"address {self.ipTarget}/24\" >> /etc/network/interfaces")
            self.runCommand (f"echo \"post-up ip route add default via {self.ipHost}\" >> /etc/network/interfaces")
            self.runCommand ("ifup eth0")
        elif (self.osImage=='FreeBSD'):
            self.runCommand ("ifconfig vtnet0 up",erroneousContents="ifconfig:")
            self.runCommand (f"ifconfig vtnet0 {self.ipTarget}/24",erroneousContents="ifconfig:")
            self.runCommand(f"route add default {self.ipHost}")
        else:
            self.terminateAndExit(f"activateEthernet: not implemented for <{self.osImage}> on <{self.target}>.",exitCode=EXIT.Implementation)
        return

    @decorate.debugWrap
    def targetTearDown(self):
        if (self.process.isalive()):
            self.runCommand('\x01x',endsWith=pexpect.EOF)
            self.process.terminate()
        clearTapAdaptor(targetId=self.targetId)
        return

    def interact(self):
        printAndLog (f"Entering interactive mode. Root password: \'{self.rootPassword}\'. Press \"Ctrl + E\" to exit.")
        super().interact()
#--- END OF CLASS qemuTarget------------------------------

@decorate.debugWrap
@decorate.timeWrap
def findMainAdaptorInfo ():
    if doesSettingExist('mainAdaptorName'):
        return getSetting('mainAdaptorName')
    #blindly find an adaptor connected to internet (hopefully -- maybe needs to be more sophisticated if needed)
    for xAdaptor in psutil.net_if_addrs():
        if ((xAdaptor != 'lo') and (not xAdaptor.startswith('docker')) and (not xAdaptor.startswith('tap'))):
            setSetting('mainAdaptorName',xAdaptor)
            return xAdaptor
    
    logAndExit(f"findMainAdaptorInfo: Failed to blindly find an adaptor connected to internet.",exitCode=EXIT.Network)


@decorate.debugWrap
@decorate.timeWrap
def configTapAdaptor(targetId=None):
    if (isEqSetting('mode','cyberPhys')):
        getSetting('networkLock').acquire()

    #Check the ipv4 forwarding
    try:
        ipForward = int(subprocess.getoutput('sudo sysctl net.ipv4.ip_forward').split()[-1])
    except Exception as exc:
        logAndExit ("Failed to find the values of 'net.ipv4.ip_forward'.",exc=exc,exitCode=EXIT.Run)
    if (ipForward != 1):
        sudoShellCommand(['sysctl', '-w', 'net.ipv4.ip_forward=1'])

    mainAdaptorName = findMainAdaptorInfo()

    #Check the postrouting nat rule
    try:
        natTables = subprocess.getoutput('sudo iptables -t nat -S').splitlines()
        isNatRule = (f"-A POSTROUTING -o {mainAdaptorName} -j MASQUERADE" in natTables)
    except Exception as exc:
        logAndExit ("Failed to find out whether the main adaptor nat was set up.",exc=exc,exitCode=EXIT.Run)
    if (not isNatRule):
        sudoShellCommand(['iptables','-t', 'nat','-A','POSTROUTING',
            '-o',mainAdaptorName,'-j','MASQUERADE'])

    #Choose a unique tapAdaptorName -- no need to search for leftovers, when the machine is reset, all of them get deleted
    tapAdaptor = f"tap{str(time.time()).replace('.','')[3:15]}" #Has to be less than 16 characters for Debian
    if (targetId is not None):
        if (targetId > 99): # Someone is hopeful
            logAndExit("configTapAdaptor: Tap adaptor name should be <16 chars on Debian. target ID > 99!.",exitCode=EXIT.Dev_Bug)
        tapAdaptor = tapAdaptor.replace('tap',f't{targetId:02}') #To guarantee uniqueness in case we were extermely unlucky
    setSetting('tapAdaptor',tapAdaptor,targetId=targetId)

    #Find a non-used IP in the range "172.16"
    chosenIpItems = "172.16.x.1".split('.')
    existingIPs = []
    for adaptor in psutil.net_if_addrs():
        for addr in psutil.net_if_addrs()[adaptor]:
            if (addr.family == socket.AF_INET):
                ipAddr = addr.address.split('.')
                if ((ipAddr[0]==chosenIpItems[0]) and (ipAddr[1]==chosenIpItems[1])): #matches 172.16
                    existingIPs.append(int(ipAddr[2]))
    try:
        minValidDigit = min(set(range(256))-set(existingIPs))
    except Exception as exc:
        logAndExit ("Failed to find a valid IP. Please consider deleting some lefotvers tap adaptors.",exc=exc,exitCode=EXIT.Network)

    chosenIpItems[2] = str(minValidDigit)
    setSetting('qemuIpHost','.'.join(chosenIpItems),targetId=targetId)
    chosenIpItems[3] = '2'
    setSetting('qemuIpTarget','.'.join(chosenIpItems),targetId=targetId)
    targetInfo = f"<target{targetId}>" if (targetId) else ''
    printAndLog(f"configTapAdaptor{targetInfo}: The adaptor is <{tapAdaptor}>, and the target IP is <{getSetting('qemuIpTarget',targetId=targetId)}>.")

    commands = [
        ['ip', 'tuntap', 'add', 'mode', 'tap', 'dev', tapAdaptor, 'user', getpass.getuser()],
        ['ip', 'addr', 'add', f"{getSetting('qemuIpHost',targetId=targetId)}/24", 'dev', tapAdaptor],
        ['ip','link','set', tapAdaptor, 'up'],
        ['iptables', '-A', 'FORWARD', '-i', mainAdaptorName,'-o', tapAdaptor,
                    '-m', 'state', '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'],
        ['iptables', '-A', 'FORWARD', '-i', tapAdaptor,'-o', mainAdaptorName,
                    '-j', 'ACCEPT']
    ]
    for command in commands:
        sudoShellCommand(command)
        time.sleep(1)

    printAndLog (f"qemu.configTapAdaptor: <{tapAdaptor}> is properly configured.",doPrint=(targetId is None))

    if (isEqSetting('mode','cyberPhys')):
        getSetting('networkLock').release()

@decorate.debugWrap
@decorate.timeWrap
def clearTapAdaptor (targetId=None):
    if (isEqSetting('mode','cyberPhys')):
        getSetting('networkLock').acquire()

    sudoShellCommand(['ip', 'tuntap', 'del', 'mode', 'tap', 'dev', getSetting('tapAdaptor',targetId=targetId)])

    if (isEqSetting('mode','cyberPhys')):
        getSetting('networkLock').release()


    

