#! /usr/bin/env python3
""" 
Main commonTarget class + misc common functions
"""

from fett.base.utils.misc import *

import os, sys, glob
import pexpect, subprocess, threading
import time, random, secrets, crypt
import string, re
import socket, errno, pty, termios
from collections import Iterable

from fett.apps.unix import database
from fett.apps.unix import webserver
from fett.apps.unix import voting
from fett.apps.freertos import freertos
from fett.apps.unix import ssh

class commonTarget():
    def __init__(self):

        self.process = None
        self.ttyProcess = None
        self.fTtyOut = None
        self.sshProcess = None
        self.fSshOut = None
        self.restartMode = False

        # all OSs settings
        self.portTarget = None
        self.portHost = None
        self.ipTarget = None
        self.ipHost = None

        # Unix settings
        self.inInteractMode = False
        self.stopShowingTime = None
        self.resendAttempts = 0
        self.limitResendAttempts = 5 if (isEqSetting('osImage','FreeBSD') and isEqSetting('target','qemu')) else 3

        # For ssh
        self.sshHostPort = None
        self.isSshConn = False
        self.sshRetries = 0
        self.sshLimitRetries = 3
        self.sshECDSAkeyWasUpdated = False

        self.onlySsh = isEqSetting('osImage','FreeBSD') and isEqSetting('target','fpga')

        self.isCurrentUserRoot = True #This will be the indicator of which user we are logged in as.
        self.rootPassword = 'ssithdefault' if (isEqSetting('osImage','FreeBSD')) else 'riscv'
        self.rootGroup = 'wheel' if (isEqSetting('osImage','FreeBSD')) else 'root'
        self.userPassword = "fett_2020"
        self.userName = (getSetting('userName') if
                         isEnabled("useCustomCredentials") else
                         "researcher")
        self.userCreated = False

        self.AttemptShutdownFailed = False
        self.keyboardInterruptTriggered = False
        self.terminateTargetStarted = False

        self.appModules = []

        return

    @decorate.debugWrap
    def shutdownAndExit (self,message,overwriteShutdown=False,overwriteConsole=False,exitCode=None,exc=None):
        if (self.stopShowingTime is not None): #turn off any time display
            try:
                self.stopShowingTime.set()
            except:
                pass
        errorAndLog(message,exc=exc)
        if (not overwriteShutdown):
            self.shutdown(overwriteConsole=overwriteConsole,isError=True)
        logAndExit("",exitCode=exitCode)

    @decorate.debugWrap
    @decorate.timeWrap
    def switchUser (self):
        if (not self.userCreated):
            self.shutdownAndExit ("switchUser: Unable to switch user when no user was created.",exitCode=EXIT.Dev_Bug)

        if (getSetting('osImage') in ['debian', 'FreeBSD']):
            if (not self.isSshConn):
                isPrevUserRoot = self.isCurrentUserRoot
                self.isCurrentUserRoot = not self.isCurrentUserRoot
                self.runCommand ("exit",endsWith="login:")

                if (isPrevUserRoot): #switch to the other user
                    loginName = self.userName
                    loginPassword = self.userPassword
                else: #switch to root
                    loginName = 'root'
                    loginPassword = self.rootPassword

                self.runCommand (loginName,endsWith="Password:")
                if (isEqSetting('osImage','FreeBSD')): #Work around the occasional login failures
                    maxLoginAttempts = 3
                    iAttempt = 0
                    loginSuccess = False
                    while ((not loginSuccess) and (iAttempt < maxLoginAttempts)):
                        #  will timeout on error, not return Login failed
                        retCommand = self.runCommand(loginPassword,
                                                     endsWith=[self.getDefaultEndWith(),"\r\nlogin:"],
                                                     timeout=60,
                                                     suppressErrors=True,
                                                     shutdownOnError=False,
                                                     issueInterrupt=False)
                        if retCommand[2]:
                            printAndLog("switchUser: Failed to login and received timeout. Trying again...",doPrint=False)
                            #  for some reason, needs to accept input to see the login failed string
                            self.runCommand(" ",endsWith=["Login incorrect"],timeout=20)
                            self.runCommand (loginName,endsWith="Password:")
                            time.sleep(3) #wait for the OS to be ready for the password (maybe this works)
                            iAttempt += 1
                            continue
                        if (retCommand[3] == 0):
                            loginSuccess = True
                        elif (retCommand[3] == 1): # try again
                            printAndLog("switchUser: Failed to login. Trying again...",doPrint=False)
                            self.runCommand (loginName,endsWith="Password:")
                            time.sleep(3) #wait for the OS to be ready for the password (maybe this works)
                            iAttempt += 1
                        else:
                            printAndLog(f"switchUser: Failed to login <iAttempt={iAttempt}>, and this part should never be executed!",doPrint=False)
                    if (not loginSuccess):
                        self.shutdownAndExit(f"switchUser: Failed to login ({maxLoginAttempts} times).",exitCode=EXIT.Run)
                else:
                    self.runCommand (loginPassword)

            else: #open and close sshConnections
                self.closeSshConn()
                self.isCurrentUserRoot = not self.isCurrentUserRoot
                if (not self.isCurrentUserRoot): #switch to the other user
                    sshSuccess = self.openSshConn(userName=self.userName)
                else: #switch to root
                    sshSuccess =  self.openSshConn(userName='root')
                if (not sshSuccess):
                    self.shutdownAndExit(f"switchUser: Failed to switch user.")
        elif (isEqSetting('osImage','buysbox')):
            if (self.isCurrentUserRoot): #switch to the other user
                self.runCommand ("su {0}".format(self.userName),endsWith="\$")
                self.runCommand ("cd ~",endsWith="\$")
            else: #switch to root
                self.runCommand ("exit",endsWith="~ #")
            self.isCurrentUserRoot = not self.isCurrentUserRoot #<This needs to be figured out for busybox in case the login itself fails
        else:
            self.shutdownAndExit(f"<switchUser> is not implemented on <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def shutdown (self,overwriteConsole=False,isError=False):
        if (isEqSetting('osImage','FreeRTOS')):
            timeout = 60
        elif (getSetting('osImage') in ['debian','busybox']):
            timeout = 45
        elif (isEqSetting('target', 'fpga')):
            timeout = 90
        elif (isEqSetting('osImage','FreeBSD') and isEqSetting('target', 'aws') and isEqSetting('pvAWS', 'connectal')):
            timeout = 150
        else:
            timeout = 45
        if (self.AttemptShutdownFailed):
            self.shutdownAndExit(f"shutdown: Unable to shutdown the {getSetting('target')} properly.",overwriteShutdown=True,exitCode=EXIT.Run)
        self.AttemptShutdownFailed = True #to avoid being trapped if the switching user failed and target is not responding
        if (isEnabled('openConsole') and (not overwriteConsole)):
            self.interact()
            if (self.userCreated):
                retCommand = self.terminateTarget(timeout=timeout,shutdownOnError=False)
                if ((not retCommand[0]) or retCommand[2]): #bad -- probably logged in as non-root user
                    self.isCurrentUserRoot = False
                    self.switchUser()
                    self.terminateTarget(timeout=timeout,shutdownOnError=True)
            else:
                self.terminateTarget(timeout=timeout,shutdownOnError=True)
        else:
            if (not self.isCurrentUserRoot):
                self.switchUser()
            self.terminateTarget(timeout=timeout,shutdownOnError=True)
        printAndLog (f"{getSetting('target')} shut down successfully!")
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def start (self,timeout=15):
        if (isEqSetting('osImage','debian')):
            printAndLog (f"start: Booting <{getSetting('osImage')}> on <{getSetting('target')}>. This might take a while...")
            if (isEqSetting('target','fpga')):
                if (isEqSetting('procFlavor','bluespec')):
                    timeout = 1150 if isEqSetting('elfLoader','JTAG') else 560
                elif (isEqSetting('procFlavor','chisel')):
                    timeout = 1050 if isEqSetting('elfLoader','JTAG') else 500
                else:
                    self.shutdownAndExit(f"start: Unrecognized processor flavor: <{getSetting('procFlavor')}>.",overwriteShutdown=False,exitCode=EXIT.Dev_Bug)
            elif (isEqSetting('target','qemu')):
                timeout = 120
            elif (isEqSetting('target', 'aws')):
                if isEqSetting('pvAWS', 'firesim'):
                    timeout = 240
                elif isEqSetting('pvAWS', 'connectal'):
                    timeout = 510
                else:
                    self.shutdownAndExit(f"start: Unrecognized AWS PV <{getSetting('pvAWS')}>.", overwriteShutdown=False, exitCode=EXIT.Dev_Bug)
            else:
                self.shutdownAndExit(f"start: Timeout is not recorded for target=<{getSetting('target')}>.",overwriteShutdown=False,exitCode=EXIT.Implementation)
            if (self.restartMode):
                timeout += 120 #takes longer to restart
            self.stopShowingTime = showElapsedTime (getSetting('trash'),estimatedTime=timeout,stdout=sys.stdout)
            self.boot(endsWith="login:",timeout=timeout)
            self.stopShowingTime.set()
            time.sleep (0.3) #to make it beautiful
            #logging in
            printAndLog (f"start: Logging in, activating ethernet, and setting system time...")
            self.runCommand ("root",endsWith="Password:")
            self.runCommand (self.rootPassword)
        elif (isEqSetting('osImage','busybox')):
            printAndLog (f"start: Booting <{getSetting('osImage')}> on <{getSetting('target')}>. This might take a while...")
            self.stopShowingTime = showElapsedTime (getSetting('trash'),estimatedTime=80,stdout=sys.stdout)
            self.boot(endsWith="Please press Enter to activate this console.",timeout=80)
            self.stopShowingTime.set()
            time.sleep (0.3) #to make it beautiful
            self.runCommand (" ",endsWith="/ #",timeout=10) #This is necessary
            self.runCommand("cd root",timeout=10)
            printAndLog (f"start: Logging in, activating ethernet, and setting system time...")
        elif (isEqSetting('osImage','FreeRTOS')):
            if (isEqSetting('binarySource','Michigan')):
                startMsg = 'INFO: Open database successfully'
            else:
                startMsg = '>>>Beginning of Fett<<<'
            self.boot (endsWith=startMsg,timeout=30)
        elif (isEqSetting('osImage','FreeBSD')):
            printAndLog (f"start: Booting <{getSetting('osImage')}> on <{getSetting('target')}>. This might take a while...")
            if (isEqSetting('target','fpga')):
                if (isEqSetting('procFlavor','bluespec')):
                    timeout = 1400 if isEqSetting('elfLoader','JTAG') else 700
                elif (isEqSetting('procFlavor','chisel')):
                    timeout = 1000 if isEqSetting('elfLoader','JTAG') else 540
                else:
                    self.shutdownAndExit(f"start: Unrecognized processor flavor: <{getSetting('procFlavor')}>.",overwriteShutdown=False,exitCode=EXIT.Dev_Bug)
            elif (isEqSetting('target','qemu')):
                timeout = 120
            elif (isEqSetting('target', 'aws')):
                timeout = 1000 if (isEqSetting('sourceVariant','temporal')) else 540
            else:
                self.shutdownAndExit(f"start: Timeout is not recorded for target=<{getSetting('target')}>.",overwriteShutdown=False,exitCode=EXIT.Implementation)
            if (self.restartMode):
                timeout += 120 #takes longer to restart
            self.stopShowingTime = showElapsedTime (getSetting('trash'),estimatedTime=timeout,stdout=sys.stdout)
            bootEndsWith = "login:"
            self.boot(endsWith=bootEndsWith, timeout=timeout)
            self.stopShowingTime.set()
            time.sleep (0.3) #to make it beautiful
            # set the temporary prompt
            if isEqSetting("binarySource", "SRI-Cambridge") or (isEqSetting("binarySource", "GFE") and isEqSetting('target', 'aws') and isEqSetting("pvAWS", "connectal")):
                tempPrompt = "~ #"
            else:
                tempPrompt = "\r\n#"
            # fpga freebsd would be already logged in if onlySsh
            if (isEqSetting('target','qemu')):
                self.runCommand("root",endsWith="\r\n#")
                self.runCommand (f"echo \"{self.rootPassword}\" | pw usermod root -h 0",erroneousContents="pw:",endsWith="\r\n#")
            elif (not self.onlySsh):
                if ((not isEqSetting("binarySource", "SRI-Cambridge")) or self.restartMode):
                    self.runCommand ("root",endsWith='Password:')
                    self.runCommand (self.rootPassword,endsWith=tempPrompt)
                else:
                    self.runCommand ("root",endsWith=tempPrompt)

            if not isEqSetting('target', 'aws'):
                self.runCommand("echo \"fettPrompt> \" > promptText.txt",endsWith=tempPrompt) #this is to avoid having the prompt in the set prompt command
                self.runCommand(f"echo \'set prompt = \"fettPrompt> \"\' > .cshrc",endsWith=tempPrompt)
                self.runCommand("set prompt = \"`cat promptText.txt`\"")
                self.runCommand("rm promptText.txt")

            printAndLog (f"start: Activating ethernet and setting system time...")
        else:
            self.shutdownAndExit (f"start: <{getSetting('osImage')}> is not implemented on <{getSetting('target')}>.",overwriteShutdown=True,exitCode=EXIT.Implementation)

        #up the ethernet adaptor and get the ip address
        self.activateEthernet()
        
        if (self.restartMode): #this only in aws/production mode -- skip the reset of start()
            if (isEqSetting('osImage','debian')): # timesync is not in the boot sequence of neither GFE nor MIT images
                ntpTimeout = 150 if isEqSetting('binarySource','MIT') else 60 # MIT needs some more time to be responsive
                self.runCommand("systemctl start systemd-timesyncd.service",timeout=ntpTimeout)
            printAndLog (f"start: {getSetting('osImage')} booted _again_ successfully!")
            return
        #fixing the time is important to avoid all time stamp warnings, and because it messes with Makefile.
        awsNtpServer = "169.254.169.123"
        if (isEqSetting('osImage','debian')):
            if isEqSetting('target', 'aws'):
                # Use AWS NTP server
                self.runCommand(f"echo 'NTP={awsNtpServer}' >> "
                                "/etc/systemd/timesyncd.conf")
            else:
                self.runCommand("echo \"nameserver 1.1.1.1\" > /etc/resolv.conf")
            self.runCommand("systemctl start systemd-timesyncd.service")

            if not self.hasHardwareRNG():
                #get the ssh up and running
                self.sendFile(getSetting('buildDir'),'addEntropyDebian.riscv')
                self.runCommand("chmod +x addEntropyDebian.riscv")
                self.ensureCrngIsUp () #check we have enough entropy for ssh

        elif (isEqSetting('osImage','FreeBSD')):
            if isEqSetting('target', 'aws'):
                # Delete default NTP pool
                self.runCommand('sed -i "" "/^pool/d" /etc/ntp.conf')
                # Add AWS NTP server
                self.runCommand(f"echo 'server {awsNtpServer} iburst' >> "
                                "/etc/ntp.conf")
            else:
                self.runCommand("echo \"nameserver 1.1.1.1\" > /etc/resolv.conf")

            # Add ntpd to rc.conf and start it
            self.runCommand("echo 'ntpd_enable=\"YES\"' >> /etc/rc.conf")
            self.runCommand("echo 'ntpd_sync_on_start=\"YES\"' >> /etc/rc.conf")
            self.runCommand("service ntpd start")

        # Instruct the kernel debugger to restart instead of debugging mode when the kernel panics
        if (isEqSetting("binarySource", "SRI-Cambridge") and isEqSetting('osImage','FreeBSD') and isEqSetting('target','aws')):
            self.runCommand("sysctl debug.debugger_on_panic=0")
            self.runCommand('echo "debug.debugger_on_panic=0" >> /etc/sysctl.conf')

        if getSetting('osImage') in ['debian', 'FreeBSD'] and not isEqSetting('binarySource', 'SRI-Cambridge'):
            printAndLog("start: setting motd...")
            motdPath = '/etc/motd.template' if isEqSetting('osImage', 'FreeBSD') else '/etc/motd'
            instanceType = f"{getSetting('binarySource')} / {getSetting('osImage')} / {getSetting('processor')}"
            self.runCommand(f"printf '\\nInstance type: {instanceType}\\n\\n' > {motdPath}")
            if isEqSetting('osImage', 'FreeBSD'):
                self.runCommand("service motd restart")

        printAndLog (f"start: {getSetting('osImage')} booted successfully!")
        return

    @decorate.debugWrap
    def interact(self):
        #This method gives the control back to the user
        if (self.inInteractMode):
            return #avoid recursive interact mode
        self.inInteractMode = True
        if (self.isSshConn): #only interact on the JTAG
            self.closeSshConn()
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
        try:
            self.process.interact(escape_character='\x05')
            #escaping interact closes the logFile, which will make any read/write fail inside pexpect logging
            self.fTtyOut = ftOpenFile(self.fTtyOut.name,self.fTtyOut.mode)
        except Exception as exc:
            errorAndLog(f"Failed to open interactive mode.",exc=exc)

    @decorate.debugWrap
    @decorate.timeWrap
    def changeRootPassword(self):
        printAndLog(f"Changing the root password...", doPrint=False)
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
        self.rootPassword = ''.join(secrets.choice(alphabet) for i in range(14))
        if isEqSetting('osImage', 'debian'):
            self.runCommand(f"passwd root", endsWith="New password:")
            self.runCommand(self.rootPassword, endsWith="Retype new password:")
            self.runCommand(self.rootPassword, expectedContents='password updated successfully')
        elif isEqSetting('osImage', 'FreeBSD'):
            userPasswordHash = sha512_crypt(self.rootPassword)
            command = (f"echo \'{userPasswordHash}\' | "
                       f"pw usermod root -H 0")
            self.runCommand(command, erroneousContents="pw:")
        else:
            self.shutdownAndExit(
                f"<update root password> is not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",
                exitCode=EXIT.Implementation)
        printAndLog(f"root password has been changed successfully!",doPrint=False)

    @decorate.debugWrap
    @decorate.timeWrap
    def enableRootUserAccess(self):
        """
        Enable passwordless `su` for users in the `wheel` group and add the
        user to `wheel`.
        """
        printAndLog("Enabling root user access...")
        if isEqSetting('osImage', 'debian'):
            self.runCommand('sed -i "s/# auth       sufficient pam_wheel.so trust/auth sufficient pam_wheel.so trust/" '
                            '/etc/pam.d/su')
            self.runCommand("groupadd wheel")
            self.runCommand(f"usermod -aG wheel {self.userName}")
        elif isEqSetting('osImage', 'FreeBSD'):
            self.runCommand('sed -i "" "s/auth\\t\\trequisite\\tpam_group.so/'
                            'auth\\t\\tsufficient\\tpam_group.so/" '
                            '/etc/pam.d/su')
            self.runCommand(f"pw group mod wheel -m {self.userName}")
        else:
            self.shutdownAndExit("<enableRootUserAccess> is not implemented "
                                 f"for <{getSetting('osImage')}>.",
                                 overwriteConsole=True,
                                 exitCode=EXIT.Implementation)

    @decorate.debugWrap
    @decorate.timeWrap
    def createUser (self):
        printAndLog (f"Creating a user...")
        if (isEqSetting('osImage','debian')):
            self.runCommand (f"useradd -m {self.userName}")
            self.runCommand (f"passwd {self.userName}",endsWith="New password:")
            self.runCommand (self.userPassword,endsWith="Retype new password:")
            self.runCommand (self.userPassword,expectedContents='password updated successfully')
            self.runCommand (f"usermod --shell /bin/bash {self.userName}")
            self.runCommand(f"echo \"PS1=\'\${{debian_chroot:+(\$debian_chroot)}}\\u@\\h:\\w\$ \'\" >> /home/{self.userName}/.bashrc")
        elif (isEqSetting('osImage','FreeBSD')):
            self.runCommand (f"echo \"{self.userName}::::::{self.userName}::sh:{self.userPassword}\" | adduser -f -",expectedContents=f"Successfully added ({self.userName}) to the user database.",timeout=90)
        elif (isEqSetting('osImage','busybox')):
            self.runCommand ("mkdir -p /home/{0}".format(self.userName))
            self.runCommand ("adduser {0}".format(self.userName),endsWith="New password:",expectedContents='Changing password')
            self.runCommand (self.userPassword,endsWith="Retype password:")
            self.runCommand (self.userPassword,expectedContents='changed by root')
        else:
            self.shutdownAndExit(f"<createUser> is not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",overwriteConsole=True,exitCode=EXIT.Implementation)
        self.userCreated = True

    @decorate.debugWrap
    @decorate.timeWrap
    def changeUserPassword(self):
        """
        Change the user's password hash to userPasswordHash from the
        configuration file.

        Precondition:  useCustomCredentials must be True in the configuration
        file
        Precondition:  User must have already been created
        """
        if not isEnabled("useCustomCredentials"):
            self.shutdownAndExit("<changeUserPassword> cannot be called if "
                                 "<useCustomCredentials> is False.",
                                 exitCode=EXIT.Dev_Bug)
        if not self.userCreated:
            self.shutdownAndExit("<changeUserPassword> cannot be called if "
                                 "user has not been created.",
                                 exitCode=EXIT.Dev_Bug)

        if not self.isCurrentUserRoot:
            self.switchUser()

        printAndLog(f"Changing user {self.userName}'s password")
        userPasswordHash = getSetting("userPasswordHash")
        if isEqSetting('osImage', 'debian'):
            command = f"usermod -p \'{userPasswordHash}\' {self.userName}"
            res = self.runCommand(command)
        elif isEqSetting('osImage', 'FreeBSD'):
            command = (f"echo \'{userPasswordHash}\' | "
                       f"pw usermod {self.userName} -H 0")
            self.runCommand(command, erroneousContents="pw:")
        else:
            self.shutdownAndExit("<createUser> is not implemented for "
                                 f"<{getSetting('osImage')}> on "
                                 f"<{getSetting('target')}>.",
                                 overwriteConsole=True,
                                 exitCode=EXIT.Implementation)


    @decorate.debugWrap
    def getDefaultEndWith (self):
        if (isEqSetting('osImage','debian')):
            if (self.isCurrentUserRoot):
                return ":~#"
            else:
                return ":~\$"
        elif (isEqSetting('osImage','FreeBSD')):
            if (self.isCurrentUserRoot):
                if isEqSetting('target', 'aws'):
                    return ":~ #"
                else:
                    return "fettPrompt>"
            else:
                return ":~ \$"
        elif (isEqSetting('osImage','busybox')):
            if (self.isCurrentUserRoot):
                return "~ #"
            else:
                return "\$"
        else:
            self.shutdownAndExit(f"<getDefaultEndWith> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation)

    @decorate.debugWrap
    def getAllEndsWith (self):
        if (isEqSetting('osImage','debian')):
            return [":~#", ":~\$"]
        elif (isEqSetting('osImage','FreeBSD')):
            if isEqSetting('target', 'aws'):
                return [":~ #", ":~ \$"]
            else:
                return ["fettPrompt>", ":~ \$"]
        elif (isEqSetting('osImage','busybox')):
            return ["~ #", "\$"]
        else:
            self.shutdownAndExit(f"<getAllEndsWith> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation)

    @decorate.debugWrap
    @decorate.timeWrap
    def runCommand (self,command,endsWith=None,expectedContents=None,
                    erroneousContents=None,shutdownOnError=True,timeout=60,
                    suppressErrors=False,tee=None,sendToNonUnix=False,issueInterrupt=True):
        """
        " runCommand: Sends `command` to the target, and wait for a reply.
        "   ARGUMENTS:
        "   ----------
        "   command: The string to send to target using `sendToTarget`. If FreeRTOS, we do nothing with it.
        "   endsWith: String/regex or list of strings/regex. The function returns when either is received from target.
        "   expectedContents: string or list of strings. If either is not found in the target's response --> error
        "   erroneousContents: string or list of strings. If either is found in the target's response --> error
        "   shutdownOnError: Boolean. Whether to return or shutdown in case of error (timeout or contents related error)
        "   timeout: how long to wait for endsWith before timing out.
        "   suppressErrors: Boolean. Whether to print the errors on screen, or just report it silently.
        "   tee: A file object to write the text output to. Has to be a valid file object to write. 
        "   sendToNonUnix: Boolean. If enabled, the command is sent to non-Unix targets as well.
        "   issueInterrupt: use keyboardInterrupt to resolve timeout recovery
        "   RETURNS:
        "   --------
        "   A list: [isSuccess  : "Boolean. True on no-errors.",
        "            textBack   : "A string containing all text returned back from the target after sending the command.",
        "            wasTimeout : "Boolean. True if timed-out waiting for endsWith.",
        "            idxEndsWith: The index of the endsWith received. If endsWith was a string, this would be 0. -1 on time-out.
        """
        if (isEnabled('isUnix') or sendToNonUnix):
            self.sendToTarget (command,shutdownOnError=shutdownOnError)
        if (endsWith is None):
            endsWith = self.getDefaultEndWith()
        textBack, wasTimeout, idxEndsWith = self.expectFromTarget (endsWith,command,shutdownOnError=shutdownOnError,timeout=timeout,issueInterrupt=issueInterrupt)
        logging.debug(f"runCommand: After expectFromTarget: <command={command}>, <endsWith={endsWith}>")
        logging.debug(f"wasTimeout={wasTimeout}, idxEndsWith={idxEndsWith}")
        logging.debug(f"textBack:\n{textBack}")
        isSuccess = not wasTimeout
        if (expectedContents is not None):
            if (isinstance(expectedContents,str)): #only one string
                expectedContents = [expectedContents]
            for content in expectedContents:
                if (content not in textBack):
                    isSuccess = False
                    errorAndLog (f"runCommand: Missing <{content}> while executing <{command}>.",doPrint=not suppressErrors)
                    break #One error per command is enough
        if (erroneousContents is not None):
            if (isinstance(erroneousContents,str)): #only one string
                erroneousContents = [erroneousContents]
            for content in erroneousContents:
                if (content in textBack):
                    isSuccess = False
                    errorAndLog (f"runCommand: Encountered <{content}> while executing <{command}>.",doPrint=not suppressErrors)
                    break #One error per command is enough
        if (tee):
            try:
                tee.write(textBack)
            except Exception as exc:
                isSuccess = False
                try:
                    fName = tee.name
                except:
                    fName = 'UNKNOWN_FILE'
                errorAndLog (f"runCommand: Failed to tee the output to <{fName}> while executing <{command}>.",doPrint=not suppressErrors,exc=exc)
        if (shutdownOnError and not isSuccess):
            self.shutdownAndExit(f"runCommand: fatal error.",exitCode=EXIT.Run)
        return [isSuccess, textBack, wasTimeout, idxEndsWith] #the 3rd argument is "timed-out"

    # Send a between host and target.
    # xFile      : file to send
    # pathToFile : directory containing xFile on host
    # targetPathToFile : directory containing xFile on target
    # toTarget   : direction of send.
    #                True[default] = send from host to target
    #                False         = send from target to host. Requires an SSH connection.
    @decorate.debugWrap
    @decorate.timeWrap
    def sendFile (self,pathToFile,xFile,targetPathToFile=None,toTarget=True,forceScp=False,timeout=30,shutdownOnError=True): #send File to target
        if (not isEnabled('isUnix')):
            self.shutdownAndExit(f"<sendFile> is not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",exitCode=EXIT.Implementation)

        def returnFalse (message='',noRetries=False,exc=None,fileToClose=None):
            self.keyboardInterrupt ()
            if (exc):
                logging.error(traceback.format_exc())
            if ((not noRetries) and (self.resendAttempts < self.limitResendAttempts-1)):
                logging.error(message)
                errorAndLog (f"sendFile: Failed to send <{pathToFile}/{xFile}> to target. Trying again...")
                self.resendAttempts += 1
                return self.sendFile (pathToFile,xFile,targetPathToFile=targetPathToFile,toTarget=toTarget,timeout=timeout,shutdownOnError=shutdownOnError,forceScp=forceScp)
            elif (shutdownOnError):
                self.shutdownAndExit (message + f"\nsendFile: Failed to send <{pathToFile}/{xFile}> to target.",exitCode=EXIT.Run)
            else:
                logging.error(message)
                errorAndLog (f"sendFile: Failed to send <{pathToFile}/{xFile}> to target.")
            return False

        if ( (self.ipTarget is None) or (self.portTarget is None) or (self.portHost is None) ):
            return returnFalse ("Ethernet not properly activated. <sendFile> can not execute.",noRetries=True)

        def checksumHost(f):
            #find the sha256sum of the file
            shaSumTX = str(subprocess.check_output (f"sha256sum {f} | awk '{{ print $1 }}'",stderr=subprocess.STDOUT,shell=True),'utf-8').strip()
            logging.debug(f"Output from <sha256sum>:\n{shaSumTX}")
            return shaSumTX

        def checksumTarget(f):
            shaSumRX = None
            if (isEqSetting('osImage','debian')):
                retShaRX = self.runCommand(f"sha256sum {f}")[1]
            elif (isEqSetting('osImage','FreeBSD')):
                retShaRX = self.runCommand(f"sha256 {f}",timeout=120)[1]
                retShaRX += self.runCommand(" ")[1]
            logging.debug(f"retShaRX:\n{retShaRX}")
            for line in retShaRX.splitlines():
                if (isEqSetting('osImage','debian')):
                    shaMatch = re.match(rf"^(?P<shaSum>[0-9a-f]+)\s+ {f}\s*$",line)
                elif (isEqSetting('osImage','FreeBSD')):
                    shaMatch = re.match(rf"^SHA256 \({f}\) = (?P<shaSum>[0-9a-f]+)$",line)
                if (shaMatch is not None):
                    shaSumRX = shaMatch.group('shaSum')
                    break
            if (shaSumRX is None):
                raise
            return shaSumRX

        # The path to the file on the target
        currentUser = 'root' if self.isCurrentUserRoot else self.userName
        user_path   = 'root' if self.isCurrentUserRoot else 'home/' + self.userName
        targetPathRoot  = f"/{user_path}" if targetPathToFile is None else targetPathToFile
        targetPath      = os.path.join(targetPathRoot,xFile)
        # The path to the file on the host
        hostPath        = os.path.join(pathToFile,xFile)

        try:
            f = hostPath if toTarget else targetPath
            shaSumTX = checksumHost(f) if toTarget else checksumTarget(f)
        except Exception as exc:
            return returnFalse (f"Failed to obtain the checksum of <{f}>.",noRetries=True,exc=exc)


        if (getSetting('osImage') in ['debian', 'FreeBSD'] and (forceScp or self.isSshConn)): #send through SSH
            portPart = '' if (not self.sshHostPort) else f" -P {self.sshHostPort}"

            # if sending TO target, then "scp host target" otherwise flipped
            scpTargetPath = f"{currentUser}@{self.ipTarget}:{targetPath}"
            scpArgs       = f"{hostPath} {scpTargetPath}" if toTarget else f"{scpTargetPath} {hostPath}"
            scpCommand    = f"scp{portPart} {scpArgs}"

            passwordPrompt = [f"Password for {currentUser}@[\w-]+\:",f"{currentUser}@[\w\-\.]+\'s password\:","\)\?"]
            scpOutFile = ftOpenFile(os.path.join(getSetting('workDir'),'scp.out'),'a')

            if (not self.sshECDSAkeyWasUpdated):
                self.clearHostKey()
            try:
                scpProcess = pexpect.spawn(scpCommand,encoding='utf-8',logfile=scpOutFile,timeout=15)
            except Exception as exc:
                return returnFalse (f"Failed to spawn an scp process for sendFile.",exc=exc)
            if not self.hasHardwareRNG():
                self.genStdinEntropy(endsWith=self.getAllEndsWith()) #get some entropy going on
            try:
                retExpect = scpProcess.expect(passwordPrompt + ["\)\?"],timeout=30)
            except Exception as exc:
                return returnFalse (f"Unexpected outcome from the scp command.",exc=exc)
            try:
                if (retExpect == 2): #needs a yes
                    scpProcess.sendline("yes")
                    retExpect = scpProcess.expect(passwordPrompt,timeout=15)
                if (retExpect in [0,1]): #password prompt
                    pwd = self.rootPassword if self.isCurrentUserRoot else self.userPassword
                    scpProcess.sendline(pwd)
                else:
                    return returnFalse (f"Failed to authenticate the scp process.")
            except Exception as exc:
                return returnFalse (f"Unexpected error while using the scp command [sending password].",exc=exc)
            try:
                scpProcess.expect(pexpect.EOF,timeout=timeout)
            except Exception as exc:
                return returnFalse (f"Unexpected error while using scp command [waiting for termination].",exc=exc)
            scpOutFile.close()
            time.sleep(5)
            self.keyboardInterrupt (shutdownOnError=True)

        else: #send the file through netcat
            if not toTarget:
                return returnFalse("sendFile: sending a file FROM the target requires an SSH connection",
                                   noRetries=True)

            if (isEqSetting('osImage','debian')):
                listenOnTarget = threading.Thread(target=self.runCommand, kwargs=dict(command=f"nc -lp {self.portTarget} > {targetPath}",timeout=timeout,shutdownOnError=False))
            elif (isEqSetting('osImage','FreeBSD')):
                listenOnTarget = threading.Thread(target=self.runCommand, kwargs=dict(command=f"nc -I 1024 -l {self.portTarget} > {targetPath}",timeout=timeout,shutdownOnError=False))
            listenOnTarget.daemon = True
            getSetting('trash').throwThread(listenOnTarget,f"nc listening for <{xFile}> on Target")
            sendFromHost = threading.Thread(target=subprocess.call, kwargs=dict(args=f"nc -w 1 {self.ipTarget} {self.portHost} <{hostPath}",shell=True))
            sendFromHost.daemon = True
            getSetting('trash').throwThread(sendFromHost,f"nc sending <{pathToFile}/{xFile}> from host")
            listenOnTarget.start()
            time.sleep(1)
            sendFromHost.start()
            listenOnTarget.join(timeout=timeout+5) #arbitrarily set timeout
            #check sending
            if (sendFromHost.is_alive()):
                logging.warning(f"sendFile: Netcat sending from host is still hanging while sending <{xFile}> to target.\n")
            if (listenOnTarget.is_alive() or (not self.doesFileExist(xFile,timeout=timeout,shutdownOnError=False))):
                return returnFalse()

        #obtaining the checksum
        try:
            f = targetPath if not toTarget else hostPath
            shaSumRX = checksumTarget(targetPath) if toTarget else checksumHost(hostPath)
        except Exception as exc:
            return returnFalse (f"Failed to obtain the checksum of <{f}>.",noRetries=True,exc=exc)

        if (shaSumRX != shaSumTX):
            return returnFalse(f"sendFile: Checksum from <{xFile}> on target does not match.")
        self.resendAttempts = 0 #reset
        return True

    @decorate.debugWrap
    def doesFileExist (self,xFile,pathToFile='.',timeout=15,shutdownOnError=True):
        return self.runCommand(f"ls {pathToFile}/{xFile}",suppressErrors=True,expectedContents=xFile,erroneousContents=['ls:', 'cannot access', 'No such file or directory'],timeout=timeout,shutdownOnError=shutdownOnError)[0]

    @decorate.debugWrap
    def sendTar(self,timeout=30): #send tarball to target
        printAndLog ("sendTar: Sending files...")
        #---send the archive
        if (getSetting('binarySource') in ['GFE', 'SRI-Cambridge']) and isEqSetting('osImage', 'FreeBSD'):
            self.switchUser() #this is assuming it was on root
            self.sendFile (getSetting('buildDir'),getSetting('tarballName'),timeout=timeout,forceScp=True)
            self.switchUser()
            self.runCommand(f"mv /home/{self.userName}/{getSetting('tarballName')} /root/")
        else:
            self.sendFile (getSetting('buildDir'),getSetting('tarballName'),timeout=timeout)
        #---untar
        if (isEqSetting('osImage','debian')):
            self.runCommand(f"tar xvf {getSetting('tarballName')} --warning=no-timestamp",erroneousContents=['gzip:','Error','tar:'],timeout=timeout)
        elif (isEqSetting('osImage','FreeBSD')):
            self.runCommand(f"tar xvf {getSetting('tarballName')} -m",erroneousContents=['gzip:','Error','tar:'],timeout=timeout)
        self.runCommand(f"rm {getSetting('tarballName')}",timeout=timeout) #to save space
        printAndLog ("sendTar: Sending successful!")

    @decorate.debugWrap
    @decorate.timeWrap
    def runApp (self,sendFiles=False,timeout=60): #executes the app
        printAndLog ("runApp: Starting the application stack...")
        if (sendFiles):
            #send any needed files to target
            self.sendTar(timeout=timeout)

        # assign modules
        if (isEqSetting('osImage','FreeRTOS')):
            self.appModules = [freertos]
        elif (getSetting('osImage') in ['debian', 'FreeBSD']):
            self.appModules = [ssh, webserver, database, voting]
            if (isEqSetting('binarySource','MIT')): #Disable nginx
                self.appModules.remove(webserver)
                self.appModules.remove(voting) #hosted by the webserver
        else:
            self.shutdownAndExit(f"<runApp> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation)

        # The appLog will be the file object flying around for logging into app.out
        appLog = ftOpenFile(os.path.join(getSetting('workDir'),'app.out'), 'a')
        appLog.write('-'*20 + "<FETT-APPS-OUT>" + '-'*20 + '\n\n')
        setSetting("appLog",appLog)

        if isEqSetting('binarySource', 'SRI-Cambridge'):
            setSetting('sqliteBin','/fett/bin/sqlite3')
        else:
            setSetting('sqliteBin','/usr/bin/sqlite')

        # Install
        for appModule in self.appModules:
            appModule.install(self)
            appLog.flush()

        # Test    
        for appModule in self.appModules:
            appModule.deploymentTest(self)
            appLog.flush()

        appLog.close()
        logging.info (f"runApp: The application stack is deployed successfully!\n")
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def collectLogs (self):
        if (getSetting('osImage') not in ['debian', 'FreeBSD']):
            printAndLog(f"No logs to be collected from <{getSetting('osImage')}>.",doPrint=False)
            return
        
        # Collect all logs into one directory
        logsPathName = 'logsFromTarget'
        logsPathOnTarget = f'/root/{logsPathName}'
        self.runCommand(f"mkdir {logsPathName}")

        # Apps logs
        for appModule in self.appModules:
            if hasattr(appModule, "dumpLogs"):
                appModule.dumpLogs(self, logsPathOnTarget)
                printAndLog (f"collectLogs: Collected <{appModule.__name__.split('.')[-1]}> logs.")
            else:
                printAndLog (f"collectLogs: nothing to do for module <{appModule.__name__.split('.')[-1]}>.",doPrint=False)

        # syslogs
        self.runCommand (f"cp /var/log/* {logsPathOnTarget}") #On debian, this returns `cp: ommitted directories`
        self.runCommand(f"dmesg > {os.path.join(logsPathOnTarget,'dmesg.txt')}")
        printAndLog (f"collectLogs: Collected syslogs.")
        
        # Create the tarball
        logsTarball = 'logsFromTarget.tar'
        self.runCommand(f"tar cvf {logsTarball} {logsPathName}",erroneousContents=['gzip:','Error','tar:'])
        self.runCommand(f"mv {logsTarball} /home/{self.userName}/{logsTarball}")
        self.runCommand(f"chown {self.userName}:{self.userName} /home/{self.userName}/{logsTarball}",erroneousContents=['chown:'])

        # Maybe the researcher has changed the password for some reason
        self.userPassword = 'newPassword'
        salt     = crypt.mksalt()
        newHash = crypt.crypt(self.userPassword, salt)
        if isEqSetting('osImage', 'debian'):
            self.runCommand(f"usermod -p \'{newHash}\' {self.userName}")
        elif isEqSetting('osImage', 'FreeBSD'):
            self.runCommand (f"echo \'{newHash}\' | pw usermod {self.userName} -H 0",erroneousContents="pw:")

        # send the tarball to the artifacts directory using non-root SCP
        self.switchUser () #login as user
        artifactPath = getSetting('extraArtifactsPath')
        if(self.sendFile(
            artifactPath, logsTarball,       
            targetPathToFile=f'/home/{self.userName}',
            forceScp=True, toTarget=False, shutdownOnError=False
        )):
            printAndLog(f"collectLogs: Received logs from target.")
            # untar the tarball to be more friendly
            tarballPathOnHost = os.path.join(artifactPath,logsTarball)
            shellCommand (['tar','xvf',tarballPathOnHost,'-C',artifactPath]) #check is True not to delete it by mistake
            shellCommand (['rm',tarballPathOnHost])
        else:
            errorAndLog(f"collectLogs: Failed to receive logs from target.")
        self.switchUser () #back to root

        return

    @decorate.debugWrap
    def keyboardInterrupt (self,shutdownOnError=True,timeout=15,retryCount=3):
        if (self.terminateTargetStarted):
            return ''
        if (self.keyboardInterruptTriggered): #to break any infinite loop
            self.shutdownAndExit("keyboardInterrupt: interrupting is not resolving properly",overwriteShutdown=True,overwriteConsole=True,exitCode=EXIT.Run)
        else:
            self.keyboardInterruptTriggered = True
        if (not isEnabled('isUnix')):
            self.shutdownAndExit(f"<keyboardInterrupt> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation)
        doTimeout = True
        retryIdx = 0
        while doTimeout and retryIdx < retryCount:
            if retryIdx > 0:
                warnAndLog(f"keyboardInterrupt: keyboard interrupt failed! Trying again ({retryIdx}/{retryCount})...") 
            retCommand = self.runCommand("\x03",shutdownOnError=False,timeout=timeout,issueInterrupt=False)
            textBack = retCommand[1]
            doTimeout = retCommand[2]
            retryIdx += 1
        if ((not retCommand[0]) or (retCommand[2])):
            textBack += self.runCommand(" ",shutdownOnError=shutdownOnError,timeout=timeout)[1]
        #See if the order is correct
        if (self.process):
            for i in range(retryIdx + 1):
                readAfter = self.readFromTarget(readAfter=True)
                if (self.getDefaultEndWith() in readAfter):
                    try:
                        self.process.expect(self.getDefaultEndWith(),timeout=timeout)
                    except Exception as exc:
                        warnAndLog(f"keyboardInterrupt: The <prompt> was in process.after, but could not pexpect.expect it. Will continue anyway.",doPrint=False,exc=exc)
                    textBack += readAfter
        self.keyboardInterruptTriggered = False #Safe to be called again
        return textBack

    @decorate.debugWrap
    def ensureCrngIsUp (self):
        if (not isEqSetting('osImage','debian')):
            self.shutdownAndExit(f"<ensureCrngIsUp> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation)

        isCrngUp = False
        for iAttempt in range(5):
            retCommand = self.runCommand("dmesg | grep random",expectedContents="crng init done",suppressErrors=True,shutdownOnError=False,timeout=30)
            isCrngUp = retCommand[0]
            retText = retCommand[1]
            if (isCrngUp):
                logging.info(f"ensureCrngIsUp: CRNG is properly initialized.\n")
                break
            retText += self.runCommand("./addEntropyDebian.riscv",erroneousContents=["bash:","<INVALID>"])[1]
            if ("crng init done" in retText):
                isCrngUp = True
                logging.info(f"ensureCrngIsUp: CRNG is properly initialized.\n")
                break

        if (not isCrngUp):
            self.shutdownAndExit(f"ensureCrngIsUp: CRNG was not initialized.",exitCode=EXIT.Run)

    @decorate.debugWrap
    def checkFallToTty (self,fnName):
        if ((not self.process) and self.isSshConn):
            warnAndLog(f"{fnName}: called with sshConnection, but connection is unreachable. Falling back to main tty.",doPrint=False)
            self.killSshConn()
        if (not self.process): #Note that this condition cannot be merged with the above one, because killSshConn updates self.process
            self.shutdownAndExit(f"{fnName}: Failed to communicate with target.",overwriteShutdown=True,exitCode=EXIT.Run)
        logging.debug(f"{fnName}: isSshConn = {self.isSshConn}")
        return

    @decorate.debugWrap
    def readFromTarget (self,endsWith=None,readAfter=False):
        self.checkFallToTty ("readFromTarget")
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

    @decorate.debugWrap
    def sendToTarget (self,command,shutdownOnError=True):
        self.checkFallToTty ("sendToTarget")
        try:
            self.process.sendline(command)
        except Exception as exc:
            if (shutdownOnError):
                self.shutdownAndExit(f"sendToTarget: Failed to send <{command}> to {getSetting('target')}.",exc=exc,exitCode=EXIT.Run)
            else:
                warnAndLog (f"sendToTarget: Failed to send <{command}> to {getSetting('target')}.",exc=exc,doPrint=False)
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def expectFromTarget (self,endsWith,command,shutdownOnError=True,timeout=15,overwriteShutdown=False,issueInterrupt=True):
        def warningThread(msg, waitingTime, stopEvent):
            """thread will wait on an event, and display warning if not set by waiting time"""
            dt = 0.1
            dt = waitingTime / 10.0 if dt > waitingTime else dt
            ct  = 0.0
            while ct < waitingTime:
                time.sleep(dt)
                if stopEvent.is_set():
                    return
                ct += dt
            warnAndLog(msg)

        # prepare thread to give warning message if the expect is near timing out
        stopEvent = threading.Event()
        warningTime = 0.8 * timeout
        warningMsg = threading.Thread(target=warningThread, args=(f"expectFromTarget: command <{command}> is near timeout ({timeout} s)", warningTime, stopEvent))
        warningMsg.daemon = True
        getSetting('trash').throwThread(warningMsg, "warning message for expectFromTarget")
        warningMsg.start()
        self.checkFallToTty ("expectFromTarget")
        logging.debug(f"expectFromTarget: <command={command}>, <endsWith={endsWith}>")
        textBack = ''
        try:
            retExpect = self.process.expect(endsWith,timeout=timeout)
            if ( (endsWith == pexpect.EOF) or isinstance(endsWith,str)): #only one string or EOF
                textBack += self.readFromTarget(endsWith=endsWith)
            else: #It is a list
                textBack += self.readFromTarget(endsWith=endsWith[retExpect])
        except pexpect.TIMEOUT:
            if (shutdownOnError):
                self.shutdownAndExit(f"expectFromTarget: {getSetting('target').capitalize()} timed out <{timeout} seconds> while executing <{command}>.",exitCode=EXIT.Run,overwriteShutdown=overwriteShutdown)
            elif (not isEqSetting('osImage','FreeRTOS')):
                warnAndLog(f"expectFromTarget: <TIMEOUT>: {timeout} seconds while executing <{command}>.",doPrint=False)
                textBack += self.keyboardInterrupt (shutdownOnError=True) if issueInterrupt else ""
            return [textBack, True, -1]
        except Exception as exc:
            self.shutdownAndExit(f"expectFromTarget: Unexpected output from target while executing {command}.",exc=exc,exitCode=EXIT.Run,overwriteShutdown=overwriteShutdown)
        # tell warning message thread that the expect is finished
        stopEvent.set()
        if (isinstance(endsWith,str)): #only one string
            textBack += endsWith
        elif ((endsWith not in [pexpect.EOF, pexpect.TIMEOUT]) and isinstance(endsWith[retExpect],str)): #list
            textBack += endsWith[retExpect]
        return [textBack, False, retExpect]

    @decorate.debugWrap
    @decorate.timeWrap
    def terminateTarget (self,timeout=15,shutdownOnError=True):
        self.terminateTargetStarted = True
        if (isEqSetting('osImage','debian')):
            if (self.isSshConn): #only shutdown on tty
                self.closeSshConn()
            shutdownString = "Power down" if (isEqSetting('binarySource','MIT')) else "Power off"
            isSuccess, textBack, isTimeout, dumpIdx = self.runCommand("shutdown -h now",endsWith=[shutdownString,pexpect.EOF],suppressErrors=True,timeout=timeout,shutdownOnError=shutdownOnError)
        elif (isEqSetting('osImage','busybox')):
            isSuccess, textBack, isTimeout, dumpIdx = self.runCommand("poweroff",endsWith="Power off",timeout=timeout,suppressErrors=True,shutdownOnError=shutdownOnError)
        elif (isEqSetting('osImage','FreeBSD') and (self.onlySsh)):
            dumpSuccess, textBack, isTimeout, dumpIdx = self.runCommand("shutdown -h now",endsWith=[self.getDefaultEndWith(),pexpect.EOF],timeout=60,suppressErrors=True,shutdownOnError=False)
            isSuccess = self.closeSshConn()
        elif (isEqSetting('osImage','FreeBSD')):
            if (self.isSshConn): #only shutdown on tty
                self.closeSshConn()
            if (isEqSetting('binarySource','SRI-Cambridge')):
                isSuccess, textBack, isTimeout, dumpIdx = self.runCommand("shutdown -h now",endsWith='System shutdown time has arrived',timeout=timeout,shutdownOnError=shutdownOnError)
            else:
                isSuccess, textBack, isTimeout, dumpIdx = self.runCommand("shutdown -h now",endsWith='Please press any key to reboot.',timeout=timeout,suppressErrors=True,shutdownOnError=shutdownOnError)
                if (("Power off" not in textBack) and (isSuccess and (not isTimeout))):
                    isSuccess, textBack_2, isTimeout, dumpIdx = self.runCommand(" ",endsWith=["Power off",pexpect.EOF],timeout=timeout,suppressErrors=True,shutdownOnError=shutdownOnError)
                    textBack = textBack + textBack_2
        elif (isEqSetting('osImage','FreeRTOS')):
            isSuccess, textBack, isTimeout, dumpIdx = [freertos.terminateAppStack(self), '', False, 0] #send STOP to OTA
        elif (not isEqSetting('osImage','FreeRTOS')):
            self.shutdownAndExit(f"terminateTarget: not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",exitCode=EXIT.Implementation)
        if ((isSuccess and (not isTimeout)) or shutdownOnError):
            isSuccess &= self.targetTearDown() #should be called before closing ttyOut because it is used in firesim
        try:
            self.fTtyOut.close()
        except Exception as exc:
            warnAndLog("terminateTarget: Failed to close the tty.out file.",doPrint=False,exc=exc)
        return [isSuccess, textBack, isTimeout, dumpIdx]

    @decorate.debugWrap
    def clearHostKey (self):
        ipUpdateECDSA = self.ipTarget if (not self.sshHostPort) else f"[{self.ipTarget}]:{self.sshHostPort}"
        self.fSshOut = ftOpenFile(os.path.join(getSetting('workDir'),'ssh.out'),'ab')
        try:
            subprocess.check_call (['ssh-keygen', '-R', ipUpdateECDSA],stdout=self.fSshOut,stderr=self.fSshOut)
        except Exception as exc:
            warnAndLog(f"openSshConn: Failed to clear the target's ECDSA key. Will continue anyway.",doPrint=False)
        self.sshECDSAkeyWasUpdated = True
        self.fSshOut.close()

    @decorate.debugWrap
    @decorate.timeWrap
    def openSshConn (self,userName='root',endsWith=None,timeout=60):
        def returnFail (message,exc=None):
            self.killSshConn()
            warnAndLog (message,doPrint=False,exc=exc)
            extraMsg = ' Trying again...' if (self.sshRetries < self.sshLimitRetries-1) else ''
            warnAndLog(f"openSshConn: Failed to open an SSH connection for <{userName}>.{extraMsg}")
            self.sshRetries += 1
            return self.openSshConn (userName=userName, timeout=timeout)

        if (getSetting('osImage') not in ['FreeBSD','debian']):
            self.shutdownAndExit(f"<openSshConn> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)

        if (self.sshRetries >= self.sshLimitRetries): #to protect it from excessive attempts
            return False

        portPart = '' if (not self.sshHostPort) else f" -p {self.sshHostPort}"
        sshCommand = f"ssh{portPart} {userName}@{self.ipTarget}"
        sshPassword = self.rootPassword  if (userName=='root') else self.userPassword
        #Need to clear the ECDSA key first in case it is not the first time
        if (not self.sshECDSAkeyWasUpdated):
            self.clearHostKey()

        self.killSshConn()
        self.fSshOut = ftOpenFile(os.path.join(getSetting('workDir'),'ssh.out'),'ab')
        try:
            self.sshProcess = pexpect.spawn(sshCommand,logfile=self.fSshOut,timeout=timeout)
        except Exception as exc:
            return returnFail(f"openSshConn: Failed to spawn an Ssh connection.",exc=exc)

        if (not self.onlySsh and not self.hasHardwareRNG()):
            self.genStdinEntropy(endsWith=self.getAllEndsWith())

        self.isSshConn = True
        self.process = self.sshProcess
        passwordPrompt = [f"Password for {userName}@[\w\-\.]+\:", f"{userName}@[\w\-\.]+\'s password\:"]
        blockedIpResponse = ["Connection closed by remote host", "Connection reset by peer"]
        retExpect = self.expectFromTarget(passwordPrompt + blockedIpResponse + ['\)\?',pexpect.EOF],"openSshConn",timeout=timeout,shutdownOnError=False)
        if (retExpect[2]==5): #Failed
            return returnFail(f"openSshConn: Failed to spawn the ssh process.")
        elif (retExpect[1]): #Failed
            return returnFail(f"openSshConn: Spawning the ssh process timed out.")
        elif (retExpect[2]==4): # asking for yes/no for new host
            self.runCommand("yes",endsWith=passwordPrompt,timeout=timeout,shutdownOnError=False)
        elif (retExpect[2] in [2,3]): #the ip was blocked
            return returnFail(f"openSshConn: Unexpected <{blockedIpResponse}> when spawning the ssh process.")
        self.runCommand(sshPassword,endsWith=endsWith,timeout=timeout,shutdownOnError=False)
        self.sshRetries = 0 #reset the retries
        return True

    @decorate.debugWrap
    def killSshConn (self): #Only for FreeBSD and Debian
        if (self.sshProcess is not None):
            try:
                self.sshProcess.terminate(force=True)
                self.sshProcess = None
            except:
                warnAndLog(f"killSshConn: Failed to terminate the sshProcess.\n",doPrint=False)
        self.isSshConn = False
        self.process = self.ttyProcess

    @decorate.debugWrap
    def closeSshConn (self, timeout=60):
        if (getSetting('osImage') not in ['FreeBSD','debian']):
            self.shutdownAndExit(f"<closeSshConn> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)
        if (self.isSshConn and (self.sshProcess is not None)):
            self.runCommand("exit",endsWith=pexpect.EOF,suppressErrors=True,timeout=timeout,shutdownOnError=False)
        try:
            self.fSshOut.close()
        except Exception as exc:
            warnAndLog("closeSshConn: Failed to close the ssh.out file.",doPrint=False)
        self.killSshConn()
        return True

    @decorate.debugWrap
    def pingTarget (self):
        #pinging the target to check everything is ok
        pingOut = ftOpenFile(os.path.join(getSetting('workDir'),'ping.out'),'a')
        pingAttempts = 3
        wasPingSuccessful = False
        for iPing in range(pingAttempts):
            try:
                subprocess.check_call(['ping', '-c', '1', '-W', '5', self.ipTarget],stdout=pingOut,stderr=pingOut)
                wasPingSuccessful = True
                break
            except Exception as exc:
                if (iPing < pingAttempts - 1):
                    errorAndLog (f"Failed to ping the target at IP address <{self.ipTarget}>. Trying again...",doPrint=False,exc=exc)
                    time.sleep(15)
                else:
                    self.shutdownAndExit(f"Failed to ping the target at IP address <{self.ipTarget}>.",exc=exc,exitCode=EXIT.Network)
        pingOut.close()
        printAndLog (f"IP address is set to be <{self.ipTarget}>. Pinging successfull!")
        return

    @decorate.debugWrap
    def genStdinEntropy (self,endsWith=None):
        lenText = 240 # Please do not use a larger string. there might be a UART buffer issue on firesim, should be resolved soon
        alphabet = string.ascii_letters + string.digits + ' '
        randText = ''.join(random.choice(alphabet) for i in range(lenText))
        self.runCommand(f"echo \"{randText}\"",endsWith=endsWith,timeout=60,shutdownOnError=False)

    def hasHardwareRNG (self):
        return isEqSetting('target','aws') and (getSetting('pvAWS') in ['firesim', 'connectal'])

# END OF CLASS commonTarget

def checkPort (portNum, host=''):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as iSock:
        try:
            iSock.bind((host, portNum))
        except OSError as error:
            if (error.errno is not errno.EADDRINUSE):
                logging.error (f"checkPort: Encountered OS Error #{error} while checking port #{portNum}.")
            else:
                return False
        except:
            logging.error (f"checkPort: Encountered a non recognized error while checking port #{portNum}.")
    return True

def showElapsedTime (trash,estimatedTime=60,stdout=sys.stdout):

    def showTime(stopThread):
        startTime = time.time()
        minutesEst, secondsEst = divmod(estimatedTime, 60)
        estimatedPrefix = "Estimated ~{:0>2}:{:0>2} ".format(int(minutesEst),int(secondsEst))
        if (isEqSetting('fettEntrypoint','devHost')):
            showTimePrefix = f"{estimatedPrefix}----- Elapsed: "
        else:
            stdout.write(f"{estimatedPrefix}\n")
        while (not stopThread.is_set()):
            minutes, seconds = divmod(time.time() - startTime, 60)
            if (isEqSetting('fettEntrypoint','devHost')):
                stdout.write(showTimePrefix + "{:0>2}:{:0>2}\r".format(int(minutes),int(seconds)))
                stdout.flush ()
            time.sleep(0.25)
        if (isEqSetting('fettEntrypoint','devHost')):
            stdout.write(' ' * (len(showTimePrefix)+5) + '\r')
        completedMsg = "Estimated ~{:0>2}:{:0>2} ----- Completed in {:0>2}:{:0>2}\n".format(int(minutesEst),int(secondsEst),int(minutes),int(seconds))
        stdout.write(completedMsg)
        stdout.flush()
        logging.info(completedMsg)

    stopTimeTrack = threading.Event()
    runTimeTrack = threading.Thread(target=showTime, kwargs=dict(stopThread=stopTimeTrack))
    runTimeTrack.daemon = True
    trash.throwThread(runTimeTrack,"Showing time thread")
    stopTimeTrack.clear()
    runTimeTrack.start()
    return stopTimeTrack

def charByCharEncoding (inBytes):
    if (not isinstance(inBytes, Iterable)):
        return ''
    textBack = ''
    for xByte in inBytes:
        try:
            xChar = chr(xByte)
        except UnicodeDecodeError:
            xChar = '<!>'
        textBack += xChar
    return textBack

