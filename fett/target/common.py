#! /usr/bin/env python3
""" 
Main commonTarget class + misc common functions
"""

from fett.base.utils.misc import *

import os, sys, glob, getpass
import pexpect, subprocess, threading
import time, random
import string, re
import socket, errno, pty, termios
from collections import Iterable

class commonTarget():
    def __init__(self):
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

        # For sshWhenPossible
        self.isSshConn = False
        self.sshProcess = None
        self.sshRetries = 0
        self.sshLimitRetries = 3
        self.sshECDSAkeyWasUpdated = False
        # TODO: fix this. Configurations that can only use SSH and no UART
        self.onlySsh = isEqSetting('osImage','FreeBSD') and (not isEqSetting('target','fpga'))

        self.isCurrentUserRoot = True #This will be the indicator of which user we are logged in as.
        # TODO: These passwords need to be different per run
        self.rootPassword = 'ssithdefault' if (isEqSetting('osImage','FreeBSD')) else 'riscv'
        self.rootGroup = 'wheel' if (isEqSetting('osImage','FreeBSD')) else 'root'
        self.userPassword = 'fett_2020'
        self.userName = 'researcher'

        self.userName = None
        self.userPassword = None
        self.AttemptShutdownFailed = False

        return

    @decorate.debugWrap
    def shutdownAndExit (self,message,overwriteShutdown=False,overwriteConsole=False,exitCode=None,exc=None):
        if (self.stopShowingTime is not None): #turn off any time display
            try:
                self.stopShowingTime.set()
            except:
                pass
        errorAndLog(message)
        if ((not overwriteShutdown) and (not isEqSetting('osImage','FreeRTOS'))):
            self.shutdown(overwriteConsole=overwriteConsole,isError=True)
        logAndExit("",exc=exc,exitCode=exitCode)

    @decorate.debugWrap
    @decorate.timeWrap
    def switchUser (self):
        if (self.userName is None) or (self.userPassword is None):
            self.shutdownAndExit ("switchUser: Unable to switch user when no user was created.",exitCode=EXIT.Dev_Bug)

        if (getSetting('osImage') in ['debian', 'FreeBSD']):
            if (not self.targetObj.isSshConn):
                isPrevUserRoot = self.isCurrentUserRoot
                self.isCurrentUserRoot = not self.isCurrentUserRoot
                self.runCommand ("exit",endsWith="login:")
                if (isPrevUserRoot): #switch to the other user
                    self.runCommand (self.userName,endsWith="Password:")
                    self.runCommand (self.userPassword)
                else: #switch to root
                    self.runCommand ("root",endsWith="Password:")
                    self.runCommand (self.rootPassword)
            else: #open and close sshConnections
                self.closeSshConn()
                self.isCurrentUserRoot = not self.isCurrentUserRoot
                if (not self.isCurrentUserRoot): #switch to the other user
                    sshSuccess = self.openSshConn(userName=self.userName)
                else: #switch to root
                    sshSuccess =  self.openSshConn(userName='root')
                if (not sshSuccess):
                    self.shutdownAndExit(f"switchUser: Failed to switch user.")
        else:
            self.shutdownAndExit(f"<switchUser> is not implemented on <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def shutdown (self,overwriteConsole=False,isError=False):
        if (isEqSetting('osImage','FreeRTOS')):
            return
        if (isEqSetting('osImage','debian')):
            timeout = 20
        else:
            timeout = 90 if isEqSetting('target','fpga') else 40
        if (self.AttemptShutdownFailed):
            self.shutdownAndExit(f"shutdown: Unable to shutdown the {getSetting('target')} properly.",overwriteShutdown=True,exitCode=EXIT.Run)
        self.AttemptShutdownFailed = True #to avoid being trapped if the switching user failed and target is not responding
        if (isEnabled('openConsole') and (not overwriteConsole)):
            self.interact()
            if (self.userName is not None):
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
    def start (self,timeout=15,createUser=False):
        if (isEqSetting('osImage','debian')):
            printAndLog (f"start: Booting <{getSetting('osImage')}> on <{getSetting('target')}>. This might take a while...")
            if (isEqSetting('target','fpga')):
                if (isEqSetting('procFlavor','bluespec')):
                    timeout = 1150 if isEqSetting('elfLoader','JTAG') else 560
                elif (isEqSetting('procFlavor','chisel')):
                    timeout = 800 if isEqSetting('elfLoader','JTAG') else 360
                else:
                    self.shutdownAndExit(f"start: Unrecognized processor flavor: <{getSetting('procFlavor')}>.",overwriteShutdown=False,exitCode=EXIT.Dev_Bug)
            elif (isEqSetting('target','qemu')):
                timeout = 120
            else:
                self.shutdownAndExit(f"start: Timeout is not recorded for target=<{getSetting('target')}>.",overwriteShutdown=False,exitCode=EXIT.Implementation)
            self.stopShowingTime = showElapsedTime (getSetting('trash'),estimatedTime=timeout,stdout=self.stdout)
            self.boot(endsWith="login:",timeout=timeout)    
            self.stopShowingTime.set() 
            time.sleep (0.3) #to make it beautiful
            #logging in
            printAndLog (f"start: Logging in, activating ethernet, and setting system time...")
            self.runCommand ("root",endsWith="Password:")
            self.runCommand ("riscv")
        elif (isEqSetting('osImage','FreeRTOS')):
            #self.boot (endsWith=">>>Beginning of Testgen<<<",timeout=timeout)
            endsWith = [">>>End of Fett<<<"]
            self.boot (endsWith=endsWith,timeout=timeout)
            logging.info (f"start: {getSetting('osImage')} executed successfully!\n")
        elif (isEqSetting('osImage','FreeBSD')):
            printAndLog (f"start: Booting <{getSetting('osImage')}> on <{getSetting('target')}>. This might take a while...")
            if (isEqSetting('target','fpga')):
                if (isEqSetting('procFlavor','bluespec')):
                    timeout = 1400 if isEqSetting('elfLoader','JTAG') else 700
                elif (isEqSetting('procFlavor','chisel')):
                    timeout = 1000 if isEqSetting('elfLoader','JTAG') else 370
                else:
                    self.shutdownAndExit(f"start: Unrecognized processor flavor: <{getSetting('procFlavor')}>.",overwriteShutdown=False,exitCode=EXIT.Dev_Bug)
            elif (isEqSetting('target','qemu')):
                timeout = 60
            else:
                self.shutdownAndExit(f"start: Timeout is not recorded for target=<{getSetting('target')}>.",overwriteShutdown=False,exitCode=EXIT.Implementation)
            self.stopShowingTime = showElapsedTime (getSetting('trash'),estimatedTime=timeout,stdout=self.stdout)
            bootEndsWith = "login:"
            self.boot(endsWith=bootEndsWith, timeout=timeout)
            self.stopShowingTime.set()
            time.sleep (0.3) #to make it beautiful

            tempEndsWith = '#' if (isEqSetting('target','fpga')) else "\r\n#"
                
            # fpga freebsd would be already logged in
            if (isEqSetting('target','qemu')):
                self.runCommand("root",endsWith=tempEndsWith)
                self.runCommand (f"echo \"{self.rootPassword}\" | pw usermod root -h 0",erroneousContents="pw:",endsWith=tempEndsWith)

            self.runCommand("echo \"testgenPrompt> \" > promptText.txt",endsWith=tempEndsWith) #this is to avoid having the prompt in the set prompt command
            self.runCommand(f"echo \'set prompt = \"testgenPrompt> \"\' > .cshrc",endsWith=tempEndsWith)
            self.runCommand("set prompt = \"`cat promptText.txt`\"")
           
            printAndLog (f"start: Activating ethernet and setting system time...")
        else:
            self.shutdownAndExit (f"start: <{getSetting('osImage')}> is not implemented on <{getSetting('target')}>.",overwriteShutdown=True,exitCode=EXIT.Implementation)

        if (isEqSetting('osImage','debian') or isEqSetting('osImage','FreeBSD')):
            self.activateEthernet() #up the ethernet adaptor and get the ip address

            #fixing the time is important to avoid all time stamp warnings, and because it messes with Makefile.
            #Adding 5 minutes to avoid being in the past
            if (isEqSetting('osImage','debian')):
                self.runCommand (f"date -s '@{int(time.time()) + 300}'",expectedContents='UTC')
            elif (isEqSetting('osImage','FreeBSD')):
                self.runCommand (f"date -f \"%s\" {int(time.time()) + 300}",expectedContents='UTC')
            if (createUser): #Create another user
                self.createUser()
                                
            printAndLog (f"start: {getSetting('osImage')} booted successfully!")
        return

    @decorate.debugWrap
    @decorate.timeWrap
    def createUser (self):
        printAndLog (f"Creating a user...")
        if (isEqSetting('osImage','debian')):
            self.runCommand ("useradd -m {0}".format(self.userName))
            self.runCommand ("passwd {0}".format(self.userName),endsWith="New password:")
            self.runCommand (self.userPassword,endsWith="Retype new password:")
            self.runCommand (self.userPassword,expectedContents='password updated successfully')
            self.runCommand ("usermod --shell /bin/bash {0}".format(self.userName))
        elif (isEqSetting('osImage','FreeBSD')):
            self.runCommand (f"echo \"{self.userName}::::::{self.userName}::sh:{self.userPassword}\" | adduser -f -",expectedContents=f"Successfully added ({self.userName}) to the user database.",timeout=90)
        else:
            self.shutdownAndExit(f"<createUser> is not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",overwriteConsole=True,exitCode=EXIT.Implementation)

    @decorate.debugWrap
    @decorate.timeWrap
    def runCommand (self,command,endsWith=None,expectedContents=None,erroneousContents=None,shutdownOnError=True,timeout=60,suppressErrors=False,uartRetriesOnBSD=True,expectExact=False):
        #expected contents: any one of them not found, gives error [one string or list]
        #erroneous contensts: any one of them gives error [one string or list]
        if (isEnabled('isUnix')):
            self.sendToTarget (command,shutdownOnError=shutdownOnError)
        if (endsWith is None):
            if (isEqSetting('osImage','debian')):
                if (self.isCurrentUserRoot):
                    endsWith = ":~#"
                elif (isEqSetting('target','qemu')):
                    endsWith = ":~\$"
                elif (isEqSetting('target','fpga')):
                    if (self.targetObj.isSshConn):
                        expectExact = True
                        endsWith = '[00m:[01;34m~[00m$'
                    else:
                        endsWith = ":~$"
                else:
                    self.shutdownAndExit(f"<runCommand> is not implemented on <{getSetting('target')}>.",exitCode=EXIT.Implementation) 
            elif (isEqSetting('osImage','FreeBSD')):
                if (isEqSetting('target','fpga')):
                    if (self.targetObj.isSshConn): #pexpect uses regex
                        endsWith = "testgenPrompt>" if (self.isCurrentUserRoot) else ":~ \$"
                    else:
                        endsWith = "testgenPrompt>" if (self.isCurrentUserRoot) else ":~ $"
                elif (isEqSetting('target','qemu')):
                    endsWith = "testgenPrompt>" if (self.isCurrentUserRoot) else ":~ \$"
                else:
                    self.shutdownAndExit(f"<runCommand> is not implemented on <{getSetting('target')}>.",exitCode=EXIT.Implementation) 
            else:
                self.shutdownAndExit(f"<runCommand> is not implemented on <{getSetting('target')}>.",exitCode=EXIT.Implementation) 
        textBack, wasTimeout, idxEndsWith = self.expectFromTarget (endsWith,command,shutdownOnError=shutdownOnError,timeout=timeout,uartRetriesOnBSD=uartRetriesOnBSD,expectExact=expectExact)
        logging.debug(f"runCommand: After expectFromTarget: <command={command}>, <endsWith={endsWith}>")
        logging.debug(f"wasTimeout={wasTimeout}, idxEndsWith={idxEndsWith}")
        logging.debug(f"textBack:\n{textBack}")
        isSuccess = not wasTimeout
        if (expectedContents is not None):
            if (isinstance(expectedContents,str)): #only one string
                if (expectedContents not in textBack):
                    isSuccess = False
                    errorAndLog (f"runCommand: Missing <{expectedContents}> while executing <{command}>.",doPrint=not suppressErrors)
            else: #It is a list
                for content in expectedContents:
                    if (content not in textBack):
                        isSuccess = False
                        errorAndLog (f"runCommand: Missing <{content}> while executing <{command}>.",doPrint=not suppressErrors)
                        break #One error per command is enough
        if (erroneousContents is not None):
            if (isinstance(erroneousContents,str)): #only one string               
                if (erroneousContents in textBack):
                    isSuccess = False
                    errorAndLog (f"runCommand: Encountered <{erroneousContents}> while executing <{command}>.",doPrint=not suppressErrors)
            else:
                for content in erroneousContents:
                    if (content in textBack):
                        isSuccess = False
                        errorAndLog (f"runCommand: Encountered <{content}> while executing <{command}>.",doPrint=not suppressErrors)
                        break #One error per command is enough
        if (shutdownOnError and not isSuccess):
            try:
                self.sendToTarget('\x03\r\n')
            except:
                pass
            self.shutdownAndExit(f"runCommand: fatal error.",exitCode=EXIT.Run)
        return [isSuccess, textBack, wasTimeout, idxEndsWith] #the 3rd argument is "timed-out"

    @decorate.debugWrap
    @decorate.timeWrap
    def sendFile (self,pathToFile,xFile,timeout=30,shutdownOnError=True): #send File to target
        if (not isEnabled('isUnix')):
            self.shutdownAndExit(f"<sendFile> is not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",exitCode=EXIT.Implementation)

        def returnFalse (message='',noRetries=False,exc=None,fileToClose=None):
            try:
                self.keyboardInterrupt (shutdownOnError=False)
            except:
                pass
            if (exc):
                logging.error(traceback.format_exc())
            if ((not noRetries) and (self.resendAttempts < self.limitResendAttempts-1)):
                logging.error(message)
                errorAndLog ("sendFile: Failed to send <{1}/{2}> to target. Trying again...".format(pathToFile,xFile))
                self.resendAttempts += 1
                return self.sendFile (pathToFile,xFile,timeout=timeout,shutdownOnError=shutdownOnError)
            elif (shutdownOnError):
                self.shutdownAndExit (message + f"\nsendFile: Failed to send <{pathToFile}/{xFile}> to target.",exitCode=EXIT.Run)
            else:
                logging.error(message)
                errorAndLog ("sendFile: Failed to send <{1}/{2}> to target.".format(pathToFile,xFile))
            return False

        if ( (self.ipTarget is None) or (self.portTarget is None) or (self.portHost is None) ):
            return returnFalse ("Ethernet not properly activated. <sendFile> can not execute.",noRetries=True)

        #find the sha256sum of the file
        try:
            shaSumTX = str(subprocess.check_output (f"sha256sum {pathToFile}/{xFile} | awk '{{ print $1 }}'",stderr=subprocess.STDOUT,shell=True),'utf-8').strip()
            logging.debug(f"Output from <sha256sum>:\n{shaSumTX}")
        except Exception as exc:
            return returnFalse ("Failed to obtain the checksum of <{1}/{2}>.".format(pathToFile,xFile),noRetries=True,exc=exc)

        if (isEqSetting('osImage','FreeBSD') and (self.targetObj.isSshConn)): #send through SSH
            scpCommand = f"scp {pathToFile}/{xFile} root@{self.ipTarget}:/root/"
            scpOutFile = ftOpenFile(os.path.join(getSetting('workDir','scp.out')),'a')
            try:
                scpProcess = pexpect.spawn(scpCommand,encoding='utf-8',logfile=scpOutFile,timeout=timeout)
            except Exception as exc:
                return returnFalse (f"Failed to spawn an scp process for sendFile.",exc=exc)
            try:
                retExpect = scpProcess.expect([f"Password for root@[\w-]+\:","\)\?"],timeout=timeout)
            except Exception as exc:
                return returnFalse (f"Unexpected outcome from the scp command.",exc=exc)
            try:
                if (retExpect == 1): #needs a yes
                    scpProcess.sendline("yes")
                    retExpect = scpProcess.expect(f"Password for root@[\w-]+\:",timeout=timeout)
                if (retExpect == 0):
                    scpProcess.sendline(self.rootPassword)
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
            if (isEqSetting('osImage','debian')): 
                listenOnTarget = threading.Thread(target=self.runCommand, kwargs=dict(command=f"nc -lp {self.portTarget} > {xFile}",timeout=timeout,shutdownOnError=False))
            elif (isEqSetting('osImage','FreeBSD')):
                listenOnTarget = threading.Thread(target=self.runCommand, kwargs=dict(command=f"nc -I 1024 -l {self.portTarget} > {xFile}",timeout=timeout,shutdownOnError=False,uartRetriesOnBSD=False))             
            listenOnTarget.daemon = True
            getSetting('trash').throwThread(listenOnTarget,"nc listening for <{0}> on Target".format(xFile))
            sendFromHost = threading.Thread(target=subprocess.call, kwargs=dict(args=f"nc -w 1 {self.ipTarget} {self.portHost} <{pathToFile}/{xFile}",shell=True))
            sendFromHost.daemon = True
            getSetting('trash').throwThread(sendFromHost,"nc sending <{0}/{1}> from host".format(pathToFile,xFile))
            listenOnTarget.start()
            time.sleep(1)
            sendFromHost.start()
            listenOnTarget.join(timeout=timeout+5) #arbitrarily set timeout
            #check sending
            if (sendFromHost.is_alive()):
                logging.warning("sendFile: Netcat sending from host is still hanging while sending <{1}> to target.\n".format(xFile))
            if (listenOnTarget.is_alive() or (not self.doesFileExist(xFile,timeout=timeout,shutdownOnError=False))):
                return returnFalse()

        #obtaining the checksum
        try:
            if (isEqSetting('osImage','debian')):
                shaSumRX = self.runCommand(f"sha256sum {xFile}")[1].split()[2]
            elif (isEqSetting('osImage','FreeBSD')):
                shaSumRX = None
                retShaRX = self.runCommand(f"sha256 {xFile}",timeout=90)[1]
                retShaRX += self.runCommand(" ")[1]
                for line in retShaRX.splitlines():
                    shaMatch = re.match(rf"^SHA256 \({xFile}\) = (?P<shaSum>[0-9a-f]+)$",line)
                    if (shaMatch is not None):
                        shaSumRX = shaMatch.group('shaSum')
                        break
                if (shaSumRX is None):
                    raise
        except Exception as exc:
            return returnFalse ("sendFile: Failed to obtain the checksum of <{1}> from target.".format(xFile),exc=exc)
        
        if (shaSumRX != shaSumTX):
            return returnFalse("sendFile: Checksum from <{1}> on target does not match.".format(xFile),exc=exc)
        self.resendAttempts = 0 #reset
        return True

    @decorate.debugWrap
    def doesFileExist (self,xFile,pathToFile='.',timeout=15,shutdownOnError=True):
        return self.runCommand(f"ls {pathToFile}/{xFile}",expectedContents=xFile,erroneousContents=['ls:', 'cannot access', 'No such file or directory'],timeout=timeout,shutdownOnError=shutdownOnError)[0]

    @decorate.debugWrap
    def sendTar(self,timeout=15): #send filesToSend.tar.gz to target
        printAndLog ("sendTar: Sending files...")
        #---send the archive
        self.sendFile (getSetting('buildDir'),"filesToSend.tar.gz",timeout=timeout)
        #---untar
        if (isEqSetting('osImage','debian')):
            self.runCommand("tar xvf filesToSend.tar.gz --warning=no-timestamp",erroneousContents=['gzip:','Error','tar:'],timeout=timeout)
        elif (isEqSetting('osImage','FreeBSD')):
            self.runCommand("tar xvf filesToSend.tar.gz -m",erroneousContents=['gzip:','Error','tar:'],timeout=timeout)
        self.runCommand("rm filesToSend.tar.gz",timeout=timeout) #to save space
        printAndLog ("sendTar: Sending successful!")

    @decorate.debugWrap
    @decorate.timeWrap
    def runApp (self,methodToExecute=None,timeout=30): #executes the app
        if (isEqSetting('osImage','FreeRTOS')):
            if (self.interactWithFreeRTOS):
                fLog = open("{0}/execFreeRTOS.log".format(self.testsDir), "a")
                getSetting('trash').throwFile(fLog)
                if ((methodToExecute is not None) and hasattr(self,methodToExecute)):
                    outLog = getattr(self,methodToExecute)(self.testsPars['TEST_NAME'] + ".riscv")
                else:
                    self.shutdownAndExit (f"runApp: Invalid methodToExecute: <{methodToExecute}>. Exitting...")
                fLog.write (outLog)
                fLog.close()
                logging.info ("runApp: {1} executed successfully!\n".format(getSetting('osImage')))
        elif (isEqSetting('osImage','debian') or isEqSetting('osImage','FreeBSD')):
            if (isEqSetting('osImage','FreeBSD') and isEqSetting('target','fpga')):
                timeout *= 4
                if (isEqSetting('procFlavor','bluespec')):
                    timeout *= 2
            #send tests to target
            self.sendTests(timeout=timeout)

            #---compile tests if needed
            if (doCompile):
                self.compileTests(timeout=timeout)

            #----move pam/limits files if there are any + *.riscv and *.sh
            listOfFiles =  self.runCommand("ls",erroneousContents=["ls:", "-bash:"])[1]
            if ("pam_" in listOfFiles):
                self.runCommand(f"chown root:{self.rootGroup} pam*",erroneousContents=['Operation not permitted', 'No such file or directory', 'chown:'])
                self.runCommand("mv pam* /etc/pam.d/",erroneousContents=['cannot stat', 'No such file or directory', 'mv:'])
            if ("limits_" in listOfFiles):
                self.runCommand(f"chown root:{self.rootGroup} limits*",erroneousContents=['Operation not permitted', 'No such file or directory', 'chown:'])
                self.runCommand("mv limits* /etc/security/",erroneousContents=['cannot stat', 'No such file or directory', 'mv:'])
            if (".riscv" in listOfFiles):
                self.runCommand("chmod +x *.riscv",erroneousContents=['cannot access', 'No such file or directory', 'Operation not permitted', 'chmod:'])
            
            if (isEqSetting('osImage','debian') and ('crngOnDebian' in self.settings) and self.settings['crngOnDebian']): #check crng is up
                self.ensureCrngIsUp ()
                if (self.settings['processor'] == 'bluespec_p3'): #execute debian on bluespec_p3 on SSH
                    self.runCommand (" ")
                    time.sleep(30)
                    self.openSshConn()

            printAndLog ("Running app...")
            #Only executable tests .riscv and .sh files
            for srcTest in sorted(os.listdir(self.testsDir)):
                exeTest = ''
                if (srcTest.endswith(".c") and (srcTest != 'addEntropyDebian.c')):
                    exeTest = srcTest.split('.')[0] + ".riscv"
                elif (srcTest.endswith(".sh") and not (self.settings['useCustomCompiling'] and (os.path.basename(self.settings['pathToCustomExecutable'])==srcTest))):
                    exeTest = srcTest
                else:
                    continue
                
                sys.stdout.write("Executing <{0}> \r".format(exeTest))
                sys.stdout.flush()
                if (methodToExecute is not None):
                    if (hasattr(self,methodToExecute)):
                        outLog = getattr(self,methodToExecute)(exeTest)
                    else:
                        self.reportAndExit (f"Error in {self.filename}: Invalid methodToExecute: <{methodToExecute}>. Exitting...")
                else:
                    outLog = self.runCommand("./{0}".format(exeTest),erroneousContents="-bash:",shutdownOnError=False,timeout=timeout)[1]
                fLog = open("{0}/{1}.log".format(self.testsDir,exeTest.split('.')[0]), "w")
                getSetting('trash').throwFile(fLog)
                fLog.write (outLog)
                if ((methodToExecute is None) and (self.settings['useCustomScoring'])): #will need the gdb output here
                    gdbOut = self.getGdbOutput()
                    fLog.write(gdbOut)
                fLog.close()
            
            sys.stdout.write(' ' * 80 + '\r')
            sys.stdout.flush()

            if (not executeOnRoot): #return to root
                self.switchUser()

            if (isEqSetting('osImage','debian') and ('crngOnDebian' in self.settings) and self.settings['crngOnDebian'] and (self.settings['processor'] == 'bluespec_p3')): #check crng is up
                self.closeSshConn()

            printAndLog ("runApp: Run successful!")
        else:
            self.reportAndExit("Error in {0}: <executeDir> is not implemented for <{1}> on <{2}>.".format(self.filename,getSetting('osImage'),self.backend))
        return

    @decorate.debugWrap
    def getGdbOutput (self):
        gdbOut = ''
        if (os.path.isfile(self.gdbOutPath)):
            try:
                fGdb = open(self.gdbOutPath, "r")
                getSetting('trash').throwFile(fGdb)
                gdbOut = "\n~~~GDB LOGGING~~~\n" + fGdb.read() + "\n~~~~~~~~~~~~~~~~~\n"
                fGdb.close()
                os.remove(self.gdbOutPath) #clear the file for next test
            except:
                warnAndLog (f"Failed to obtain the GDB output.")
        return gdbOut

    @decorate.debugWrap
    def keyboardInterrupt (self,shutdownOnError=True):
        if (not isEnabled('isUnix')):
            self.shutdownAndExit(f"<keyboardInterrupt> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation)
        retCommand = self.runCommand("\x03",shutdownOnError=False,uartRetriesOnBSD=False,timeout=15)
        textBack = retCommand[1]
        if ((not retCommand[0]) or (retCommand[2])):
            textBack += self.runCommand(" ",shutdownOnError=shutdownOnError,uartRetriesOnBSD=False,timeout=15)[1]
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


# END OF CLASS commonTarget

def parseIpAddr (retIpAddr):
    #This should only be used on host as per the new static configuration
    #For now, the code uses the second interface because it is always the main one
    #Alternative more robust way: parse /etc/network/interfaces for macAddress and match it
    relevantLine = retIpAddr.splitlines()[1]
    ipFormatMatch = re.match (r'(?P<interface>\w+)\s+UP\s+(?P<ipAddress>(\d{1,3}\.){3}\d{1,3})\/\d{1,3} .*$', relevantLine)
    if (ipFormatMatch is not None):
        ipAddr = ipFormatMatch.group('ipAddress')
        if ((ipAddr == 0) or (ipAddr == '0.0.0.0')):
            exit()
        return ipAddr
    else:
        exit ()

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
        prefix = "Estimated ~{:0>2}:{:0>2} ----- Elapsed: ".format(int(minutesEst),int(secondsEst))
        while (not stopThread.is_set()):
            minutes, seconds = divmod(time.time() - startTime, 60)
            stdout.write(prefix + "{:0>2}:{:0>2}\r".format(int(minutes),int(seconds)))
            stdout.flush ()
            time.sleep(0.25)
        stdout.write(' ' * (len(prefix)+5) + '\r')
        stdout.write("Estimated ~{:0>2}:{:0>2} ----- Completed in {:0>2}:{:0>2}\n".format(int(minutesEst),int(secondsEst),int(minutes),int(seconds)))
        stdout.flush()


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


