#! /usr/bin/env python3
""" 
Main qemu class + misc qemu functions
"""

from fett.base.utils.misc import *
from fett.target.common import *
import psutil, socket

class qemuTarget (commonTarget):
    def __init__ (self):
        
        super().__init__()
        
        self.ipTarget = getSetting('qemuIpTarget')
        self.ipHost = getSetting('qemuIpHost')
        self.portTarget = getSetting('qemuPortTarget')
        self.portHost = getSetting('qemuPortHost')

        # Important for the Web Server
        self.httpPortTarget  = getSetting('HTTPPortTarget')
        self.httpsPortTarget = getSetting('HTTPSPortTarget')
        self.votingHttpPortTarget  = getSetting('VotingHTTPPortTarget')
        self.votingHttpsPortTarget = getSetting('VotingHTTPSPortTarget')

        return

    @decorate.debugWrap
    @decorate.timeWrap
    def boot (self,endsWith="login:",timeoutDict={"boot":90}): #no need to use targetObj as we'll never boot in non-reboot mode
        self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),'tty.out'),'ab') #has to be bytes, if we use a filter, interact() does not work (pexpect bug)
        timeout = self.parseBootTimeoutDict (timeoutDict)
        if (getSetting('osImage') in ['debian', 'FreeBSD']):

            qemuCommand  = f"qemu-system-riscv64 -nographic -machine virt -m 4G -kernel {getSetting('osImageElf')} -append \"console=ttyS0\""
            qemuCommand += f" -device virtio-net-device,netdev=usernet"
            qemuCommand += f" -netdev tap,id=usernet,ifname={getSetting('tapAdaptor')}"

            try:
                self.ttyProcess = pexpect.spawn(qemuCommand,logfile=self.fTtyOut,timeout=timeout)
                self.process = self.ttyProcess
                self.expectFromTarget(endsWith,"Booting",timeout=timeout)
            except Exception as exc:
                self.shutdownAndExit(f"boot: Failed to spwan the qemy process.",overwriteShutdown=True,exc=exc,exitCode=EXIT.Run)
        elif (isEqSetting('osImage', 'FreeRTOS')):
            qemuCommand = "qemu-system-riscv32 -nographic -machine sifive_e -kernel " + getSetting('osImageElf')
            try:
                self.process = pexpect.spawn(qemuCommand,timeout=timeout,logfile=self.fTtyOut)
            except:
                self.shutdownAndExit("Error in {0}: Failed to spawn the qemu process.".format(self.filename),overwriteShutdown=True)
            time.sleep(1)
            textBack,wasTimeout,idxReturn = self.expectFromTarget(endsWith,"Booting",timeout=timeout,shutdownOnError=False)
            if (idxReturn==1): #No "">>> End Of Testgen <<<", but qemu aborted without a timeout
                self.fTtyOut.write (b"\n<QEMU ABORTED>\n")
            else:
                self.fTtyOut.write (b"\n") #because the last expect does not include an end of line
            self.fTtyOut.flush()
            #Will terminate here as well because it is easier, and there is currently no other options -- might change
            self.sendToTarget ("\x01x")
        else:
            self.shutdownAndExit(f"boot: <{getSetting('osImage')}> is not implemented on <{getSetting('target')}>.",overwriteShutdown=True,exitCode=EXIT.Implementation)
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def activateEthernet (self): #no need to use targetObj as we'll never activate ethernet in non-reboot mode
        if (isEqSetting('osImage','debian')):
            self.runCommand ("echo \"auto eth0\" > /etc/network/interfaces")
            self.runCommand ("echo \"iface eth0 inet static\" >> /etc/network/interfaces")
            self.runCommand (f"echo \"address {self.ipTarget}/24\" >> /etc/network/interfaces")
            self.runCommand (f"echo \"post-up ip route add default via {self.ipHost}\" >> /etc/network/interfaces")
            self.runCommand ("ifup eth0")
        elif (isEqSetting('osImage','FreeBSD')):
            self.runCommand ("ifconfig vtnet0 up",erroneousContents="ifconfig:")
            self.runCommand (f"ifconfig vtnet0 {self.ipTarget}/24",erroneousContents="ifconfig:")
            self.runCommand(f"route add default {self.ipHost}")
        else:
            self.shutdownAndExit(f"activateEthernet: not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",exitCode=EXIT.Implementation)
        return

    def targetTearDown(self):
        if (self.process.isalive()):
            self.runCommand('\x01x',endsWith=pexpect.EOF)
            self.process.terminate()
        clearTapAdaptor ()
        return True

    def interact(self):
        printAndLog (f"Entering interactive mode. Root password: \'{self.rootPassword}\'. Press \"Ctrl + E\" to exit.")
        super().interact()
#--- END OF CLASS qemuTarget------------------------------

@decorate.debugWrap
@decorate.timeWrap
def configTapAdaptor():
    #Choose a unique tapAdaptorName -- no need to search for leftovers, when the machine is reset, all of them get deleted
    tapAdaptor = f"tap{str(time.time()).replace('.','')[3:15]}" #Has to be less than 16 characters for Debian
    setSetting('tapAdaptor',tapAdaptor)

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
    setSetting('qemuIpHost','.'.join(chosenIpItems))
    chosenIpItems[3] = '2'
    setSetting('qemuIpTarget','.'.join(chosenIpItems))

    commands = [
        ['ip', 'tuntap', 'add', 'mode', 'tap', 'dev', tapAdaptor, 'user', getpass.getuser()],
        ['ip', 'addr', 'add', f"{getSetting('qemuIpHost')}/24", 'dev', tapAdaptor],
        ['ip','link','set', tapAdaptor, 'up']
    ]
    for command in commands:
        sudoShellCommand(command)
        time.sleep(1)

    printAndLog (f"qemu.configTapAdaptor: <{tapAdaptor}> is properly configured.",doPrint=False)

@decorate.debugWrap
@decorate.timeWrap
def clearTapAdaptor ():
    sudoShellCommand(['ip', 'tuntap', 'del', 'mode', 'tap', 'dev', getSetting('tapAdaptor')])


    

