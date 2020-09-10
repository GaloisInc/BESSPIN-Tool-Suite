#! /usr/bin/env python3
""" 
Main qemu class + misc qemu functions
"""

from fett.base.utils.misc import *
from fett.target.common import *

class qemuTarget (commonTarget):
    def __init__ (self):
        
        super().__init__()
        
        self.ipTarget = getSetting('qemuIpTarget')

        return

    @decorate.debugWrap
    @decorate.timeWrap
    def assignNtkPorts(self):
        """
        Must ONLY be called on debian or freebsd
        """
        #Find open ports to use. Searching from qemuNtkPortRangeStart-qemuNtkPortRangeEnd.
        #To avoid assigning a port to the target while it is still booting, will use even number for target and odd for host
        rangeStart = getSetting('qemuNtkPortRangeStart')
        rangeEnd = getSetting('qemuNtkPortRangeEnd')
        if (rangeStart >= rangeEnd-1):
            self.shutdownAndExit(f"assignNtkPorts: The port range {rangeStart}-{rangeEnd} is too small. Please choose a wider range.",exitCode=EXIT.Configuration)
        if (rangeStart%2):
            rangeStart += 1
        for iPort in range(rangeStart,rangeEnd,2):
            if (checkPort (iPort) and checkPort(iPort+1)):
                self.portTarget = iPort
                self.portHost = iPort+1
                break
        if ((self.portTarget is None) or (self.portHost is None)):
            self.shutdownAndExit(f"assignNtkPorts: Could not find open ports in the range {rangeStart}-{rangeEnd}. Please choose another range.",exitCode=EXIT.Network)
        printAndLog(f"assignNtkPorts: portTarget={self.portTarget}, portHost={self.portHost}",doPrint=False)
        
        #find more ports for ssh and http
        additionalPorts = []
        nPorts = 5
        for xPort in range(self.portHost+1,rangeEnd):
            if (checkPort(xPort)):
                additionalPorts.append(xPort)
                if (len(additionalPorts) == nPorts):
                    break
        if (len(additionalPorts) != nPorts):
            self.shutdownAndExit(f"assignNtkPorts: Could not find enough open ports in the range {rangeStart}-{rangeEnd}. Please choose another range.",exitCode=EXIT.Network)
        printAndLog(f"assignNtkPorts: The app ports are: {','.join(str(xPort) for xPort in additionalPorts)}.",doPrint=False)
        self.sshHostPort           = additionalPorts[0]
        self.httpPortTarget        = additionalPorts[1]
        self.httpsPortTarget       = additionalPorts[2]
        self.votingHttpPortTarget  = additionalPorts[3]
        self.votingHttpsPortTarget = additionalPorts[4]

        return

    @decorate.debugWrap
    @decorate.timeWrap
    def boot (self,endsWith="login:",timeout=90): #no need to use targetObj as we'll never boot in non-reboot mode
        self.fTtyOut = ftOpenFile(os.path.join(getSetting('workDir'),'tty.out'),'ab') #has to be bytes, if we use a filter, interact() does not work (pexpect bug)
        if (getSetting('osImage') in ['debian', 'FreeBSD']):
            self.assignNtkPorts()
            ports = [("target", self.portTarget),
                     ("hostTcp", self.portHost),
                     ("hostSsh", self.sshHostPort),
                     ("hostHTTP", self.httpPortTarget),
                     ("hostHTTPS", self.httpsPortTarget),
                     ("votingHTTP", self.votingHttpPortTarget),
                     ("votingHTTPS", self.votingHttpsPortTarget)]
            portUsage = ", ".join([f"<{name}:{port}>" for name,port in ports])
            printAndLog(f"Qemu will use the network ports {portUsage}.")

            hostFwdPairs = [
                (self.portHost, self.portTarget),
                (self.sshHostPort, 22),
                (self.httpPortTarget, getSetting('HTTPPortTarget')),
                (self.httpsPortTarget, getSetting('HTTPSPortTarget')),
                (self.votingHttpPortTarget, getSetting('VotingHTTPPortTarget')),
                (self.votingHttpsPortTarget, getSetting('VotingHTTPSPortTarget')),
            ]

            hostFwdString = ",".join([f"hostfwd=tcp:{self.ipTarget}:{portHost}-:{portTarget}" for portHost,portTarget in hostFwdPairs])

            qemuCommand  = f"qemu-system-riscv64 -nographic -machine virt -m 4G -kernel {getSetting('osImageElf')} -append \"console=ttyS0\""
            qemuCommand += f" -device virtio-net-device,netdev=usernet"
            qemuCommand += f" -netdev user,id=usernet,{hostFwdString}"

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

    def interact(self):
        printAndLog (f"Entering interactive mode. Root password: \'{self.rootPassword}\'. Press \"Ctrl + E\" to exit.")
        super().interact()
#--- END OF CLASS qemuTarget------------------------------
