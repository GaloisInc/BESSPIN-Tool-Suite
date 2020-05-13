#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute FreeRTOS app
"""

from fett.base.utils.misc import *  
import tftpy

@decorate.debugWrap
@decorate.timeWrap
def deploy(target):
    return ''

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    return deploymentTest(target)

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    # target is a fett target object
    outLog = ''
    # Wait till TFTP server is up
    outLog += rtosRunCommand(target,"tftpServerReady",endsWith='<TFTP-SERVER-READY>',timeout=30)[1]
    # Creating a client - this does not throw an exception as it does not connect. It is jsust an initialization.
    clientTftp = tftpy.TftpClient(target.ipTarget, getSetting('TFTPPortTarget')) 
    # uploading the index.html file
    fileName = 'index.html'
    fileSigned = os.path.join(getSetting('repoDir'),'fett','apps','freertos','resources',fileName)
    try:
        clientTftp.upload(fileName, fileSigned, timeout=10)
    except Exception as exc:
        target.shutdownAndExit(f"clientTftp: Failed to upload <{fileSigned}> to the server.",exc=exc,exitCode=EXIT.Run)
    """
    # downloading a file
    fileName = "fileToReceive.html"
    fileToReceive = os.path.join(getSetting('workDir'),fileName)
    try:
        clientTftp.download(filename, output, packethook=None, timeout=10)
    except Exception as exc:
        target.shutdownAndExit(f"clientTftp: Failed to download <{fileToReceive}> from the server.",exc=exc,exitCode=EXIT.Run)
    """
    
    # Run to completion
    outLog += rtosRunCommand(target,"runFreeRTOSapps",endOfApp=True,timeout=getSetting('appTimeout'))[1]
    return outLog

def rtosRunCommand (target,command,endsWith=[],expectedContents=None,erroneousContents=[],shutdownOnError=True,timeout=60,suppressErrors=False,expectExact=False,endOfApp=False):
    if isinstance(endsWith,str):
        endsWith = [endsWith]
    elif (not isinstance(endsWith,list)):
        target.shutdownAndExit(f"rtosRunCommand: <endsWith> has to be list or str.",exitCode=EXIT.Dev_Bug)

    if (isinstance(erroneousContents,str)):
        erroneousContents = [erroneousContents]
    elif (not isinstance(erroneousContents,list)):
        target.shutdownAndExit(f"rtosRunCommand: <erroneousContents> has to be list or str.",exitCode=EXIT.Dev_Bug)

    retCommand = target.runCommand(command,endsWith=[">>>End of Fett<<<"] + endsWith,
        expectedContents=expectedContents,erroneousContents=erroneousContents + ['(Error)','EXIT: exiting FETT with code <1>'],shutdownOnError=shutdownOnError,
        timeout=timeout,suppressErrors=suppressErrors,expectExact=expectExact)

    if ((retCommand[3] == 0) and (not endOfApp)): #FETT exited prematurely
        target.shutdownAndExit(f"rtosRunCommand: FreeRTOS finished prematurely.",exitCode=EXIT.Run)

    return retCommand