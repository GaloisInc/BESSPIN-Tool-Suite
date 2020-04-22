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
    def readFromTarget (self,endsWith=None,readAfter=False):
        if (not hasattr(self, 'process')):
            return ''
        if (self.process is not None):
            try:
                if (readAfter):
                    fetchedBytes = self.process.after
                else: #default
                    fetchedBytes = self.process.before
                try:
                    if (fetchedBytes == pexpect.TIMEOUT):
                        textBack = '\n<TIMEOUT>\n'
                    elif (fetchedBytes == pexpect.EOF):
                        textBack = '\n<EOF>\n'
                    else:
                        textBack = str(fetchedBytes,'utf-8')
                except UnicodeDecodeError:
                    textBack = charByCharEncoding(fetchedBytes)
                    warnAndLog ("Unrecognized character while reading from target.",doPrint=False)
            except Exception as exc:
                warnAndLog ("Failed to read from target.",doPrint=False,exc=exc)
                return ''
            logging.debug(f"readFromTarget: <endsWith={endsWith}>")
            logging.debug(f"textBack:\n{textBack}{endsWith}")
            return textBack
        else:
            return ''

    @decorate.debugWrap
    @decorate.timeWrap
    def boot (self,endsWith="login:",timeout=90): #no need to use targetObj as we'll never boot in non-reboot mode
        if (getSetting('osImage') in ['debian', 'FreeBSD']):
            #Find open ports to use. Searching from qemuNtkPortRangeStart-qemuNtkPortRangeEnd.
            #To avoid assigning a port to the target while it is still booting, will use even number for target and odd for host
            rangeStart = getSetting('qemuNtkPortRangeStart')
            rangeEnd = getSetting('qemuNtkPortRangeEnd')
            if (rangeStart >= rangeEnd-1):
                self.shutdownAndExit(f"boot: The port range {rangeStart}-{rangeEnd} is too small. Please choose a wider range.",exitCode=EXIT.Configuration)
            if (rangeStart%2):
                rangeStart += 1
            for iPort in range(rangeStart,rangeEnd,2):
                if (checkPort (iPort) and checkPort(iPort+1)):
                    self.portTarget = iPort
                    self.portHost = iPort+1
                    break
            if ((self.portTarget is None) or (self.portHost is None)):
                self.shutdownAndExit(f"boot: Could not find open ports in the range {rangeStart}-{rangeEnd}. Please choose another range.",exitCode=EXIT.Network)
            #checking ssh port
            if (self.sshHostPort in [self.portTarget, self.portHost]):
                self.shutdownAndExit(f"boot: The sshHostPort<{self.sshHostPort}> is the same as the chosen default tcp ports:<{self.portTarget} and {self.portHost}>.",exitCode=EXIT.Configuration)
            
            printAndLog(f"Qemu will use the network ports <target:{self.portTarget}>, <hostTcp:{self.portHost}>, and <hostSsh:{self.sshHostPort}>.")

            qemuCommand = f"qemu-system-riscv64 -nographic -machine virt -m 2G -kernel {getSetting('osImageElf')} -append \"console=ttyS0\"" 
            qemuCommand += f" -device virtio-net-device,netdev=usernet -netdev user,id=usernet,hostfwd=tcp:{self.ipTarget}:{self.portHost}-:{self.portTarget},hostfwd=tcp:{self.ipTarget}:{self.sshHostPort}-:22"

            targetOutFile = ftOpenFile(os.path.join(getSetting('workDir'),'target.out'),'ab') #has to be bytes, if we use a filter, interact() does not work (pexpect bug)
            try:
                self.process = pexpect.spawn(qemuCommand,logfile=targetOutFile,timeout=timeout)
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

    @decorate.debugWrap
    def sendToTarget (self,command,shutdownOnError=True):
        try:
            self.process.sendline(command)
        except Exception as exc:
            if (shutdownOnError):
                self.shutdownAndExit(f"sendToTarget: Failed to send <{command}> to qemu.",exc=exc,exitCode=EXIT.Run)
            else:
                warnAndLog (f"sendToTarget: Failed to send <{command}> to qemu.",exc=exc,doPrint=False)
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def expectFromTarget (self,endsWith,command,shutdownOnError=True,timeout=15,uartRetriesOnBSD=False,expectExact=False):
        if (not hasattr(self, 'process')):
            return ['', True, -1]
        textBack = ''
        try:
            if (expectExact):
                retExpect = self.process.expect_exact(endsWith,timeout=timeout)
            else:
                retExpect = self.process.expect(endsWith,timeout=timeout)
            if ( (endsWith == pexpect.EOF) or isinstance(endsWith,str)): #only one string or EOF
                textBack += self.readFromTarget(endsWith=endsWith)
            else: #It is a list
                textBack += self.readFromTarget(endsWith=endsWith[retExpect])
        except pexpect.TIMEOUT:
            if (shutdownOnError):
                self.shutdownAndExit(f"expectFromTarget: Qemu timed out <{timeout} seconds> while executing <{command}>.",exitCode=EXIT.Run)
            elif (not isEqSetting('osImage','FreeRTOS')):
                warnAndLog(f"expectFromTarget: <TIMEOUT>: {timeout} seconds while executing <{command}>.",doPrint=False)
                textBack += self.keyboardInterrupt (shutdownOnError=True)
            return [textBack, True, -1]
        except Exception as exc:
            self.shutdownAndExit(f"expectFromTarget: Unexpected output from target while executing {command}.",exc=exc,exitCode=EXIT.Run)
        if (endsWith == pexpect.EOF):
            endsWith = ''
        elif (isinstance(endsWith,str)): #only one string
            textBack += endsWith
        else:
            textBack += endsWith[retExpect]
        return [textBack, False, retExpect]

    @decorate.debugWrap
    def interact (self): #no need to use targetObj as we'll never activate ethernet in non-reboot mode
        #This method gives the control back to the user
        if (self.inInteractMode):
            return #avoid recursive interact mode
        self.inInteractMode = True
        printAndLog (f"Entering interactive mode. Press \"Ctrl + E\" to exit.")
        if (self.userName is not None):
            printAndLog (f"Note that there is another user. User name: \'{self.userName}\'. Password: \'{self.userPassword}\'.")
            printAndLog ("Now the shell is logged in as: \'{0}\'.".format('root' if self.isCurrentUserRoot else self.userName))
        try:
            self.process.interact(escape_character='\x05')
        except Exception as exc:
            errorAndLog(f"Failed to open interactive mode.",exc=exc)

    @decorate.debugWrap
    @decorate.timeWrap
    def terminateTarget (self,timeout=15,shutdownOnError=True):
        if (isEqSetting('osImage','debian')):
            return self.runCommand("shutdown -h now",endsWith=pexpect.EOF,timeout=timeout,shutdownOnError=shutdownOnError)
        elif (isEqSetting('osImage','FreeBSD')):
            retCommand = self.runCommand("shutdown -h now",endsWith='Please press any key to reboot.',timeout=timeout,shutdownOnError=shutdownOnError)
            if ((not retCommand[0]) or retCommand[2]): 
                return retCommand
            return self.runCommand(" ",endsWith=pexpect.EOF,timeout=timeout,shutdownOnError=shutdownOnError)
        else:
            self.shutdownAndExit(f"terminateTarget: not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",exitCode=EXIT.Implementation)
        targetOutFile.close()
        return

#--- END OF CLASS qemuTarget------------------------------