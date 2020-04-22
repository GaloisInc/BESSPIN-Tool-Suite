#! /usr/bin/env python3
""" 
Main commonTarget class + misc common functions
"""

from fett.base.utils.misc import *

import os, sys, glob
import pexpect, subprocess, threading
import time, random
import string, re
import socket, errno, pty, termios
from collections import Iterable

from fett.apps.database.run import runApp as runDatabase
from fett.apps.webserver.run import runApp as runWebserver
from fett.apps.https.run import runApp as runHttps
from fett.apps.ota.run import runApp as runOta

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
            self.stopShowingTime = showElapsedTime (getSetting('trash'),estimatedTime=timeout,stdout=sys.stdout)
            self.boot(endsWith="login:",timeout=timeout)    
            self.stopShowingTime.set() 
            time.sleep (0.3) #to make it beautiful
            #logging in
            printAndLog (f"start: Logging in, activating ethernet, and setting system time...")
            self.runCommand ("root",endsWith="Password:")
            self.runCommand (self.rootPassword)
            self.sendFile(getSetting('buildDir'),'addEntropyDebian.riscv')
            self.runCommand("chmod +x addEntropyDebian.riscv")
            self.ensureCrngIsUp () #check we have enough entropy for ssh
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
            self.stopShowingTime = showElapsedTime (getSetting('trash'),estimatedTime=timeout,stdout=sys.stdout)
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
            self.runCommand (f"useradd -m {self.userName}")
            self.runCommand (f"passwd {self.userName}",endsWith="New password:")
            self.runCommand (self.userPassword,endsWith="Retype new password:")
            self.runCommand (self.userPassword,expectedContents='password updated successfully')
            self.runCommand (f"usermod --shell /bin/bash {self.userName}")
        elif (isEqSetting('osImage','FreeBSD')):
            self.runCommand (f"echo \"{self.userName}::::::{self.userName}::sh:{self.userPassword}\" | adduser -f -",expectedContents=f"Successfully added ({self.userName}) to the user database.",timeout=90)
        else:
            self.shutdownAndExit(f"<createUser> is not implemented for <{getSetting('osImage')}> on <{getSetting('target')}>.",overwriteConsole=True,exitCode=EXIT.Implementation)

    @decorate.debugWrap
    def getDefaultEndWith (self):
        if (isEqSetting('osImage','debian')):
            if (self.isCurrentUserRoot):
                return ":~#"
            elif (isEqSetting('target','qemu')):
                return ":~\$"
            elif (isEqSetting('target','fpga')):
                if (self.targetObj.isSshConn):
                    expectExact = True
                    return '[00m:[01;34m~[00m$'
                else:
                    return ":~$"
            else:
                self.shutdownAndExit(f"<getDefaultEndWith> is not implemented on <{getSetting('target')}>.",exitCode=EXIT.Implementation) 
        elif (isEqSetting('osImage','FreeBSD')):
            if (isEqSetting('target','fpga')):
                if (self.targetObj.isSshConn): #pexpect uses regex
                    return "testgenPrompt>" if (self.isCurrentUserRoot) else ":~ \$"
                else:
                    return "testgenPrompt>" if (self.isCurrentUserRoot) else ":~ $"
            elif (isEqSetting('target','qemu')):
                return "testgenPrompt>" if (self.isCurrentUserRoot) else ":~ \$"
            else:
                self.shutdownAndExit(f"<getDefaultEndWith> is not implemented on <{getSetting('target')}>.",exitCode=EXIT.Implementation) 
        else:
            self.shutdownAndExit(f"<getDefaultEndWith> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation) 

    @decorate.debugWrap
    @decorate.timeWrap
    def runCommand (self,command,endsWith=None,expectedContents=None,erroneousContents=None,shutdownOnError=True,timeout=60,suppressErrors=False,uartRetriesOnBSD=True,expectExact=False):
        #expected contents: any one of them not found, gives error [one string or list]
        #erroneous contensts: any one of them gives error [one string or list]
        if (isEnabled('isUnix')):
            self.sendToTarget (command,shutdownOnError=shutdownOnError)
        if (endsWith is None):
            endsWith = self.getDefaultEndWith()
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
                errorAndLog (f"sendFile: Failed to send <{pathToFile}/{xFile}> to target. Trying again...")
                self.resendAttempts += 1
                return self.sendFile (pathToFile,xFile,timeout=timeout,shutdownOnError=shutdownOnError)
            elif (shutdownOnError):
                self.shutdownAndExit (message + f"\nsendFile: Failed to send <{pathToFile}/{xFile}> to target.",exitCode=EXIT.Run)
            else:
                logging.error(message)
                errorAndLog (f"sendFile: Failed to send <{pathToFile}/{xFile}> to target.")
            return False

        if ( (self.ipTarget is None) or (self.portTarget is None) or (self.portHost is None) ):
            return returnFalse ("Ethernet not properly activated. <sendFile> can not execute.",noRetries=True)

        #find the sha256sum of the file
        try:
            shaSumTX = str(subprocess.check_output (f"sha256sum {pathToFile}/{xFile} | awk '{{ print $1 }}'",stderr=subprocess.STDOUT,shell=True),'utf-8').strip()
            logging.debug(f"Output from <sha256sum>:\n{shaSumTX}")
        except Exception as exc:
            return returnFalse (f"Failed to obtain the checksum of <{pathToFile}/{xFile}>.",noRetries=True,exc=exc)

        if (isEqSetting('osImage','FreeBSD') and (self.targetObj.isSshConn)): #send through SSH
            scpCommand = f"scp {pathToFile}/{xFile} root@{self.ipTarget}:/root/"
            scpOutFile = ftOpenFile(os.path.join(getSetting('workDir'),'scp.out'),'a')
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
            getSetting('trash').throwThread(listenOnTarget,f"nc listening for <{xFile}> on Target")
            sendFromHost = threading.Thread(target=subprocess.call, kwargs=dict(args=f"nc -w 1 {self.ipTarget} {self.portHost} <{pathToFile}/{xFile}",shell=True))
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
            shaSumRX = None
            if (isEqSetting('osImage','debian')):
                retShaRX = self.runCommand(f"sha256sum {xFile}")[1]
            elif (isEqSetting('osImage','FreeBSD')):
                retShaRX = self.runCommand(f"sha256 {xFile}",timeout=90)[1]
                retShaRX += self.runCommand(" ")[1]
            logging.debug(f"retShaRX:\n{retShaRX}")
            for line in retShaRX.splitlines():
                if (isEqSetting('osImage','debian')):
                    shaMatch = re.match(rf"^(?P<shaSum>[0-9a-f]+)\s+ {xFile}\s*$",line)
                elif (isEqSetting('osImage','FreeBSD')):
                    shaMatch = re.match(rf"^SHA256 \({xFile}\) = (?P<shaSum>[0-9a-f]+)$",line)
                if (shaMatch is not None):
                    shaSumRX = shaMatch.group('shaSum')
                    break
            if (shaSumRX is None):
                raise
        except Exception as exc:
            return returnFalse (f"sendFile: Failed to obtain the checksum of <{xFile}> from target.",exc=exc)
        
        if (shaSumRX != shaSumTX):
            return returnFalse(f"sendFile: Checksum from <{xFile}> on target does not match.")
        self.resendAttempts = 0 #reset
        return True

    @decorate.debugWrap
    def doesFileExist (self,xFile,pathToFile='.',timeout=15,shutdownOnError=True):
        return self.runCommand(f"ls {pathToFile}/{xFile}",suppressErrors=True,expectedContents=xFile,erroneousContents=['ls:', 'cannot access', 'No such file or directory'],timeout=timeout,shutdownOnError=shutdownOnError)[0]

    @decorate.debugWrap
    def sendTar(self,timeout=15): #send filesToSend.tar.gz to target
        printAndLog ("sendTar: Sending files...")
        #---send the archive
        self.sendFile (getSetting('buildDir'),getSetting('tarballName'),timeout=timeout)
        #---untar
        if (isEqSetting('osImage','debian')):
            self.runCommand("tar xvf filesToSend.tar.gz --warning=no-timestamp",erroneousContents=['gzip:','Error','tar:'],timeout=timeout)
        elif (isEqSetting('osImage','FreeBSD')):
            self.runCommand("tar xvf filesToSend.tar.gz -m",erroneousContents=['gzip:','Error','tar:'],timeout=timeout)
        self.runCommand("rm filesToSend.tar.gz",timeout=timeout) #to save space
        printAndLog ("sendTar: Sending successful!")

    @decorate.debugWrap
    @decorate.timeWrap
    def runApp (self,sendFiles=False,timeout=30): #executes the app
        printAndLog ("Running app...")
        if (sendFiles):
            #send any needed files to target
            self.sendTar(timeout=timeout)

        if (isEnabled('https')):
            outLog = runHttps()
        elif (isEnabled('ota')):
            outLog = runOta()
        elif (isEnabled('webserver')):
            outLog = runWebserver()
        elif (isEnabled('database')):
            outLog = runDatabase()

        fLog = ftOpenFile(os.path.join(getSetting('workDir'),'app.out'), 'a')
        fLog.write (outLog)
        fLog.close()
        logging.info (f"runApp: app executed successfully!\n")
        return

    @decorate.debugWrap
    def keyboardInterrupt (self,shutdownOnError=True):
        if (not isEnabled('isUnix')):
            self.shutdownAndExit(f"<keyboardInterrupt> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Implementation)
        retCommand = self.runCommand("\x03",shutdownOnError=False,uartRetriesOnBSD=False,timeout=15)
        textBack = retCommand[1]
        if ((not retCommand[0]) or (retCommand[2])):
            textBack += self.runCommand(" ",shutdownOnError=shutdownOnError,uartRetriesOnBSD=False,timeout=15)[1]
        #See if the order is correct
        if (self.process):
            readAfter = self.readFromTarget(readAfter=True)
            if (self.getDefaultEndWith() in readAfter):
                self.process.expect(":~#",timeout=timeout)
                textBack += readAfter
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


