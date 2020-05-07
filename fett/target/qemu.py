#! /usr/bin/env python3
""" 
Main qemu class + misc qemu functions
"""

from fett.base.utils.misc import *
from fett.target.common import *

class qemuTarget (commonTarget):
    def __init__ (self):
        
        super().__init__()
        self.sshHostPort = getSetting('qemuSshHostPort')
        self.ipTarget = getSetting('qemuIpTarget')
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def allocPortRange(self):
        """
        Must ONLY be called on debian or freebsd
        """
        #Find open ports to use. Searching from qemuNtkPortRangeStart-qemuNtkPortRangeEnd.
        #To avoid assigning a port to the target while it is still booting, will use even number for target and odd for host
        rangeStart = getSetting('qemuNtkPortRangeStart')
        rangeEnd = getSetting('qemuNtkPortRangeEnd')
        if (rangeStart >= rangeEnd-1):
            self.shutdownAndExit(f"allocPortRange: The port range {rangeStart}-{rangeEnd} is too small. Please choose a wider range.",exitCode=EXIT.Configuration)
        if (rangeStart%2):
            rangeStart += 1
        for iPort in range(rangeStart,rangeEnd,2):
            if (checkPort (iPort) and checkPort(iPort+1)):
                self.portTarget = iPort
                self.portHost = iPort+1
                break
        if ((self.portTarget is None) or (self.portHost is None)):
            self.shutdownAndExit(f"allocPortRange: Could not find open ports in the range {rangeStart}-{rangeEnd}. Please choose another range.",exitCode=EXIT.Network)
        #checking ssh port
        if (self.sshHostPort in [self.portTarget, self.portHost]):
            self.shutdownAndExit(f"allocPortRange: The sshHostPort<{self.sshHostPort}> is the same as the chosen default tcp ports:<{self.portTarget} and {self.portHost}>.",exitCode=EXIT.Configuration)
        return (rangeStart, rangeEnd)

    @decorate.debugWrap
    @decorate.timeWrap
    def boot (self,endsWith="login:",timeout=90): #no need to use targetObj as we'll never boot in non-reboot mode
        if (getSetting('osImage') in ['debian', 'FreeBSD']):
            rangeStart, rangeEnd = self.allocPortRange()
            printAndLog(f"Qemu will use the network ports <target:{self.portTarget}>, <hostTcp:{self.portHost}>, and <hostSsh:{self.sshHostPort}>.")

            qemuCommand = f"qemu-system-riscv64 -nographic -machine virt -m 2G -kernel {getSetting('osImageElf')} -append \"console=ttyS0\"" 
            qemuCommand += f" -device virtio-net-device,netdev=usernet -netdev user,id=usernet,hostfwd=tcp:{self.ipTarget}:{self.portHost}-:{self.portTarget},hostfwd=tcp:{self.ipTarget}:{self.sshHostPort}-:22"

            self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),'tty.out'),'ab') #has to be bytes, if we use a filter, interact() does not work (pexpect bug)
            try:
                self.ttyProcess = pexpect.spawn(qemuCommand,logfile=self.fTtyOut,timeout=timeout)
                self.process = self.ttyProcess
                self.expectFromTarget(endsWith,"Booting",timeout=timeout)
            except Exception as exc:
                self.shutdownAndExit(f"boot: Failed to spwan the qemy process.",overwriteShutdown=True,exc=exc,exitCode=EXIT.Run)
        else:
            self.shutdownAndExit(f"boot: <{getSetting('osImage')}> is not implemented on <{getSetting('target')}>.",overwriteShutdown=True,exitCode=EXIT.Implementation)
        
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def activateEthernet (self): #no need to use targetObj as we'll never activate ethernet in non-reboot mode
        if (isEqSetting('osImage','debian')):
            self.runCommand ("echo \"auto eth0\" > /etc/network/interfaces")
            self.runCommand ("echo \"iface eth0 inet dhcp\" >> /etc/network/interfaces")
            self.runCommand ("ifup eth0",expectedContents=['Created duid', 'DHCPDISCOVER', 'DHCPOFFER', 'DHCPREQUEST', 'DHCPACK'])
            if ((self.portTarget is None) or (self.portHost is None)):
                self.shutdownAndExit(f"activateEthernet: Network ports were not assigned properly.",exitCode=EXIT.Dev_Bug)
        elif (isEqSetting('osImage','FreeBSD')):
            self.runCommand ("echo \'ifconfig_vtnet0=\"DHCP\"\' >> /etc/rc.conf",erroneousContents="Unmatched")
            self.runCommand ("ifconfig vtnet0 up",erroneousContents="ifconfig:")
            self.runCommand("dhclient vtnet0", expectedContents=["DHCPACK", "bound to"])
        else:
            self.shutdownAndExit(f"activateEthernet: not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",exitCode=EXIT.Implementation)
        return

    def targetTearDown(self):
        return True


    @decorate.debugWrap
    def interact (self):
        #This method gives the control back to the user
        if (self.inInteractMode):
            return #avoid recursive interact mode
        self.inInteractMode = True
        if (self.isSshConn): #only interact on the JTAG
            self.closeSshConn()
        printAndLog (f"Entering interactive mode. Press \"Ctrl + E\" to exit.")
        if (self.userCreated):
            printAndLog (f"Note that there is another user. User name: \'{self.userName}\'. Password: \'{self.userPassword}\'.")
            printAndLog ("Now the shell is logged in as: \'{0}\'.".format('root' if self.isCurrentUserRoot else self.userName))
        try:
            self.process.interact(escape_character='\x05')
            #escaping interact closes the logFile, which will make any read/write fail inside pexpect logging
            self.fTtyOut = ftOpenFile(self.fTtyOut.name,self.fTtyOut.mode)
        except Exception as exc:
            errorAndLog(f"Failed to open interactive mode.",exc=exc)

#--- END OF CLASS qemuTarget------------------------------