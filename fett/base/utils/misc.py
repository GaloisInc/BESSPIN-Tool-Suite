#! /usr/bin/env python3
"""
Misc required functions for fett.py
"""

import logging, enum, traceback, atexit
import os, shutil, glob, subprocess, pathlib
import tarfile, sys, json, re, getpass, time
import crypt
import zstandard

from fett.base.utils import decorate
from fett.base.utils import aws

# private; not available using import *
_settings = dict()

# hardcoded URLs -- needed for emergency reporting
_settings['awsProdSqsQueueTX'] = 'https://sqs.us-west-2.amazonaws.com/065510690417/master-fettportal-InstanceStatusQueue-1H71N09IEKG3F.fifo'
_settings['awsProdSqsQueueRX'] = 'https://sqs.us-west-2.amazonaws.com/065510690417/master-fettportal-PortalToInstanceTerminationQueue-CND4M2WJAWOK' 
_settings['awsProdS3Bucket'] = 'master-ssith-fett-target-researcher-artifacts'

_settings['awsDevSqsQueueTX'] = 'https://sqs.us-west-2.amazonaws.com/363527286999/develop-fettportal-InstanceStatusQueue-1DQ91T9W5DFZ1.fifo'
_settings['awsDevSqsQueueRX'] = 'https://sqs.us-west-2.amazonaws.com/363527286999/develop-fettportal-PortalToInstanceTerminationQueue-1YKQ0ZBH4B50' 
_settings['awsDevS3Bucket'] = 'develop-ssith-fett-target-researcher-artifacts'

class EXIT (enum.Enum):
    Success = 0
    Unspecified = enum.auto()
    Nothing_to_do = enum.auto()
    Configuration = enum.auto()
    Files_and_paths = enum.auto()
    Environment = enum.auto()
    Implementation = enum.auto()
    Dev_Bug = enum.auto()
    Run = enum.auto()
    Network = enum.auto()
    Interrupted = enum.auto()
    AWS = enum.auto()

    def __str__ (self): #to replace '_' by ' ' when printing
        return f"{self.name.replace('_',' ')}"

def exitFett (exitCode):
    def inExit_logAndExit (message,exc=None):
        if (exc): #empty message
            message += f"\n{formatExc(exc)}."
     
        errorAndLog (f"inExit: {message}")
        exitCode = EXIT.AWS
        errorAndLog(f"End of FETT! [Exit code {exitCode.value}:{exitCode}]")
        exit(exitCode.value)

    def inExit_GetSetting (setting):
        try:
            return _settings[setting]
        except:
            return 'UNKNOWN'

    def inExit_sudoShellCommand (argsList, check=True, **kwargs):
        try:
            shellOut = open(os.path.join(inExit_GetSetting('workDir'),'shell.out'),'a')
        except Exception as exc:
            inExit_logAndExit (f"Failed to open <{os.path.join(inExit_GetSetting('workDir'),'shell.out')}> to append.",exc=exc)

        command = ['sudo'] + argsList
        shellOut.write(f"\n\n{command}\n")
        shellOut.flush()
        try:
            subprocess.run(command, stdout=shellOut, stderr=shellOut, check=check, **kwargs)
        except Exception as exc:
            inExit_logAndExit (f"shell: Failed to <{command}>. Check <shell.out> for more details.",exc=exc)
        shellOut.close()

    if (not isinstance(exitCode,EXIT)):
        exitCode = EXIT.Unspecified
    
    # notify portal if in production mode -- cannot rely on getSetting because it calls logAndExit
    if (inExit_GetSetting('mode') == 'production'):
        if (exitCode != EXIT.Success): # ERRONEOUS STATE!! -- emergency upload
            collectRemoteLogging (inExit_logAndExit,inExit_GetSetting,inExit_sudoShellCommand) #Maybe we have some remote logs
            tarballPath = tarArtifacts (inExit_logAndExit,inExit_GetSetting)
            aws.uploadToS3(inExit_GetSetting(f'{inExit_GetSetting("fettEntrypoint")}S3Bucket'), inExit_logAndExit, 
                            tarballPath, 'fett-target/production/artifacts/')
            printAndLog(f"Artifacts tarball uploaded to S3.")

        jobStatus = 'success' if (exitCode == EXIT.Success) else 'failure'
        aws.sendSQS(inExit_GetSetting(f'{inExit_GetSetting("fettEntrypoint")}SqsQueueTX'), inExit_logAndExit, jobStatus, 
                    inExit_GetSetting('prodJobId'), f"{inExit_GetSetting('prodJobId')}-TERM",
                    reason='fett-target-production-termination',
                    hostIp=aws.getInstanceIp(inExit_logAndExit),
                    fpgaIp=inExit_GetSetting('productionTargetIp')
                    )
        printAndLog("Sent termination message to the SQS queue.")       

    printAndLog(f"End of FETT! [Exit code {exitCode.value}:{exitCode}]")
    exit(exitCode.value)

def exitOnInterrupt (xSig,xFrame):
    exitFett(EXIT.Interrupted)

def formatExc (exc):
    """ format the exception for printing """
    try:
        return f"<{exc.__class__.__name__}>: {exc}"
    except:
        return '<Non-recognized Exception>'

def printAndLog (message,doPrint=True,tee=None):
    if (doPrint):
        print("(Info)~  " + message)
    if (tee):
        try:
            tee.write(message + '\n')
        except Exception as exc:
            try:
                fName = tee.name
            except:
                fName = 'UNKNOWN_FILE'
            errorAndLog(f"printAndLog: Failed to tee the output to <{fName}>.",doPrint=False,exc=exc)
    logging.info(message)

def warnAndLog (message,doPrint=True,exc=None):
    if (doPrint):
        print("(Warning)~  " + message)
    logging.warning(message)
    if (exc):
        logging.warning(traceback.format_exc())
    
def errorAndLog (message,doPrint=True,exc=None):
    if (doPrint):
        print("(Error)~  " + message)
    logging.error(message)
    if (exc):
        logging.error(traceback.format_exc())

@decorate.debugWrap
def logAndExit (message,exc=None,exitCode=EXIT.Unspecified):
    if (message or exc):
        if (not message): #empty message
            message = f"{formatExc(exc)}."
        elif (exc):
            message += f"\n{formatExc(exc)}."
        errorAndLog(message,exc=exc)
    exitFett (exitCode)

def setSetting (setting, val):
    try:
        _settings[setting] = val
    except Exception as exc:
        logAndExit (f"Failed to set setting <{setting}> to <{val}>.",exc=exc,exitCode=EXIT.Dev_Bug)

def getSetting (setting, default=None):
    try:
        return _settings[setting]
    except Exception as exc:
        if default is not None:
            return default
        logAndExit (f"getSetting: Failed to obtain the value of <{setting}>.",exc=exc,exitCode=EXIT.Dev_Bug)

def getSettingDict (setting,hierarchy):
    xSetting = getSetting(setting)
    if (isinstance(hierarchy,str)):
        hierarchy = [hierarchy]
    for item in hierarchy:
        try:
            xSetting = xSetting[item]
        except Exception as exc:
            hierarchyPretty = ''.join([f"[{x}]" for x in hierarchy])
            logAndExit (f"getSetting: Failed to obtain the value of <{setting}{hierarchyPretty}>.",exc=exc,exitCode=EXIT.Dev_Bug)
    return xSetting

def isEnabled(setting):
    val = getSetting(setting)
    if (isinstance(val,bool)):
        return val
    else:
        logAndExit (f"isEnabled: The value of <{setting}> is not boolean: <{val}>.",exitCode=EXIT.Dev_Bug)

def isEqSetting (setting,val):
    return (getSetting(setting) == val)

def doesSettingExist (setting):
    return (setting in _settings)

def dumpSettings ():
    logging.debug(f"settings = {_settings}")

def mkdir(dirPath, addToSettings=None):
    try:
        os.mkdir(dirPath)
        logging.debug(f"Created directory <{dirPath}>.")
    except Exception as exc:
        logAndExit (f"Failed to create <{dirPath}>.",exitCode=EXIT.Files_and_paths,exc=exc)
    if (addToSettings):
        setSetting(addToSettings,dirPath)

@decorate.debugWrap
def tar (tarFileName, filesList=[]):
    """
    Create a tar archive of the files in filesList.
    filesList is a list of either:
      (1) file names, to be copied to the tar archive as-is
      (2) (dest name, file name) pairs, i.e. 'file name' will be copied to the
          archive as 'dest name'. Useful for copying files from deeply nested
          trees
    """
    try:
        tarFile = tarfile.open(name=tarFileName, mode="a:")
    except Exception as e:
        logAndExit (f"tar: error creating {tarFileName}", exc=e, exitCode=EXIT.Files_and_paths)
    for f in filesList:
        arcname = None
        if type(f) == tuple:
            arcname = f[0]
            f       = f[1]
        try:
            tarFile.add(f, arcname=arcname)
        except Exception as e:
            logAndExit (f"tar: error adding {f} to {tarFileName}", exc=e, exitCode=EXIT.Files_and_paths)
    try:
        tarFile.close()
    except Exception as e:
            logAndExit (f"tar: error closing {tarFileName}", exc=e, exitCode=EXIT.Files_and_paths)

@decorate.debugWrap
def cp (src,dest,pattern=None):
    if ((not src) or (not dest)):
        if (not src):
            logAndExit (f"cp: source cannot be of NoneType.",exitCode=EXIT.Dev_Bug)
        else:
            logAndExit (f"cp: destination cannot be of NoneType.",exitCode=EXIT.Dev_Bug)
    
    if (pattern):
        if (not os.path.isdir(src)):
            logAndExit (f"cp: pattern has to have a valid source dir <{src}>.",exitCode=EXIT.Files_and_paths)
        if (not os.path.isdir(dest)):
            logAndExit (f"cp: pattern has to have a valid destination dir <{dest}>.",exitCode=EXIT.Files_and_paths)
        try:
            listFiles = glob.glob(os.path.join(src, pattern))
        except Exception as exc:
            logAndExit (f"Failed to list <{src}/{pattern}>.",exc=exc,exitCode=EXIT.Files_and_paths)
        for xFile in listFiles:
            if (os.path.isfile(xFile)):
                try:
                    shutil.copy2(xFile,dest)
                except Exception as exc:
                    logAndExit (f"Failed to copy <{xFile}> to <{dest}>.",exc=exc,exitCode=EXIT.Files_and_paths)
    else:
        if (not os.path.isfile(src)):
            logAndExit (f"cp: <{src}> is not a valid file.",exitCode=EXIT.Files_and_paths)
        try:
            shutil.copy2(src,dest)
        except Exception as exc:
            logAndExit (f"Failed to copy <{src}> to <{dest}>.",exc=exc,exitCode=EXIT.Files_and_paths)

@decorate.debugWrap
def renameFile (src,dest):
    if ((not src) or (not dest)):
        logAndExit(f"renameFile: source or destination cannot be of NoneType", exitCode=EXIT.Dev_Bug)

    if (not os.path.isfile(src)):
        logAndExit (f"renameFile: <{src}> is not a valid file.",exitCode=EXIT.Files_and_paths)

    try:
        os.rename(src,dest)
    except Exception as exc:
        logAndExit (f"Failed to rename <{src}> to <{dest}>.",exc=exc,exitCode=EXIT.Files_and_paths)

@decorate.debugWrap
def copyDir(src,dest,renameDest=False,copyContents=False):
    if ((not src) or (not dest)):
        logAndExit(f"copyDir: source or destination cannot be of NoneType", exitCode=EXIT.Dev_Bug)
    if (not os.path.isdir(src)):
        logAndExit(f"copyDir: invalid source dir <{src}>.",exitCode=EXIT.Files_and_paths)

    if ((not renameDest) and (not os.path.isdir(dest))):
        logAndExit(f"copyDir: invalid destination dir <{dest}>.",exitCode=EXIT.Files_and_paths)
    if(renameDest and copyContents): #that doesn't make sense
        logAndExit(f"copyDir: Cannot call with both renameDest and copyContents.", exitCode=EXIT.Dev_Bug)

    if (copyContents):
        #first, copy files
        cp(src,dest,pattern='*')
        #second, copy dirs -- no need to check walk as we check it's dir, and if it's empty, listDirs will = []
        recursiveContents = [listDirs for dirName,listDirs,listFiles in os.walk(src)]
        listDirs = recursiveContents[0]
        for xDir in listDirs:
            copyDir(os.path.join(src,xDir),dest)
    else:
        try:
            shutil.copytree(src, os.path.join(dest,os.path.basename(os.path.normpath(src))))
        except Exception as exc:
            logAndExit (f"Failed to copy directory <{src}> to <{dest}>.",exc=exc,exitCode=EXIT.Files_and_paths)

def touch(filepath, mode=0o666, permissive=True):
    try:
        pathlib.Path(filepath).touch(mode=mode, exist_ok=permissive)
    except FileExistsError as exc:
        logAndExit(f"touch: Failed touching file {filepath}! File already exists", exc=exc, exitCode=EXIT.Files_and_paths)
    except FileNotFoundError as exc:
        logAndExit(f"touch: filepath {filepath} is not a valid path", exc=exc, exitCode=EXIT.Files_and_paths)
    except Exception as exc:
        logAndExit(f"touch: Error touching file {filepath}", exc=exc)

def safeLoadJsonFile (jsonFile):
    try:
        fJson = ftOpenFile(jsonFile, 'r')
        jsonData = json.load(fJson)
        fJson.close()
    except Exception as exc:
        logAndExit(f"Failed to load json file <{jsonFile}>.",exc=exc,exitCode=EXIT.Files_and_paths)
    return jsonData

@decorate.debugWrap
def make (argsList,dirPath):
    if ((not dirPath) or (argsList is None)):
        logAndExit (f"make: <dirPath={dirPath}> or <argsList={argsList}> cannot be empty/None.",exitCode=EXIT.Dev_Bug)
    # open a file for stdout/stderr
    outMake = ftOpenFile(os.path.join(getSetting('buildDir'),'make.out'),'a')

    argsList = ['make','-C',dirPath] + argsList
    logging.info(f"Executing <{' '.join(argsList)}>. Command output is appended to <{outMake.name}>.")
    try:
        subprocess.check_call(argsList, stdout=outMake, stderr=outMake)
    except Exception as exc:
        outMake.close()
        logAndExit (f"Failed to <{' '.join(argsList)}>.",exc=exc,exitCode=EXIT.Run)

    outMake.close()

class redirectPrintToFile:
    def __init__(self,outFilePath):
        self.outFile = ftOpenFile(outFilePath,'a')

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = self.outFile

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout
        self.outFile.close()

class trashCanObj (object):
    def __init__ (self):
        self.threadsTrash = []
        self.filesTrash = []

    def throwThread (self,thread,tag):
        self.threadsTrash.append((tag,thread))

    def throwFile (self,xFile):
        self.filesTrash.append(xFile)

    def listThreadsInTrash (self):
        return self.threadsTrash

    def listFilesInTrash (self):
        return self.filesTrash

def exitPeacefully (trashCan):
    #close the opened files
    for xFile in trashCan.listFilesInTrash():
        try:
            if (not xFile.closed):
                logging.warning (f"Atexit: File <{xFile.name}> was left open. Closing it...")
            xFile.close()
        except Exception as exc:
            logging.warning (f"Atexit: attempted to check on cleanly closing <{xFile.name}>, but something went wrong.\n{formatExc(exc)}.")

    #close any hanging threads
    for (tag,thread) in trashCan.listThreadsInTrash():
        if ((thread is not None) and (thread.is_alive())): #oops it's alive
            logging.warning (f"Atexit: Thread <{tag}> was still alive at exit. It is unsafely killed.")

@decorate.debugWrap
def ftOpenFile (filePath,mode,exitOnFileError=True):
    if ('w' in mode):
        modeName = 'write'
    elif ('a' in mode):
        modeName = 'append'
    elif ('r' in mode):
        modeName = 'read'
    else:
        logAndExit (f"openFile: Unrecognized requested mode=<{mode}>.",exitCode=EXIT.Dev_Bug)

    try:
        xFile = open(filePath,mode)
        getSetting('trash').throwFile(xFile)
        return xFile
    except Exception as exc:
        errMsg = f"Failed to open <{filePath}> to {modeName}."
        if (exitOnFileError):
            logAndExit (errMsg,exc=exc,exitCode=EXIT.Files_and_paths)
        else:
            errorAndLog(f"{errMsg} Will continue anyway.",doPrint=False,exc=exc)
            return None    

@decorate.debugWrap
def ftReadLines (filePath,exitOnFileError=True):
    xFile = ftOpenFile (filePath,'r',exitOnFileError=exitOnFileError)
    if ((not xFile) and (not exitOnFileError)):
        return []
    try:
        lines = xFile.read().splitlines()
        xFile.close()
        return lines
    except Exception as exc:
        logAndExit (f"Failed to read lines from <{filePath}>.",exc=exc,exitCode=EXIT.Files_and_paths)

@decorate.debugWrap    
def matchExprInLines (expr,lines,returnIndex=False):
    if (not lines):
        return (None, False) if returnIndex else None
    for index, line in enumerate(lines):
        xMatch = re.match(expr,line)
        if (xMatch is not None):
            return (xMatch, index) if returnIndex else xMatch
    return (None, False) if returnIndex else None

@decorate.debugWrap    
def curlRequest(url, extra=[], http2=False, method="GET", rawOutput=False, timeout=60):
    # Need --insecure because of self signed certs
    options = [
        "--insecure",
        "--http2" if http2 else "--http1.1",
        "-L",
        "-s",
        "-X", method,
        '-m', str(timeout)
    ] + extra
    if not rawOutput:
        options.append("-I")
    try:
        p = subprocess.run (['curl'] + options + [url], capture_output=True, check=True)
        out = p.stdout.decode('utf-8')
    except Exception as exc:
        errorAndLog (f"Failed to run <curl {' '.join(options)} {url}>\n", exc=exc, doPrint=False)
        out = None
    return out

@decorate.debugWrap
def sudoShellCommand (argsList, sudoPromptPrefix=None, check=True, timeout=30, **kwargs):
    if (sudoPromptPrefix):
        try:
            sudoPrompt = sudoPromptPrefix + f" [sudo] password for {getpass.getuser()}: "
        except Exception as exc:
            logAndExit (f"sudo: Failed to format the sudo prompt with <{sudoPromptPrefix}>.",exc=exc,exitCode=EXIT.Dev_Bug)
        promptArgs = ['-p', sudoPrompt]
    else: #no prompt
        promptArgs = []

    command = ['sudo'] + promptArgs + argsList
    shellCommand (command, check=check, timeout=timeout, **kwargs)

@decorate.debugWrap
def shellCommand (argsList, check=True, timeout=30, **kwargs):
    shellOut = ftOpenFile(os.path.join(getSetting('workDir'),'shell.out'),'a')
    shellOut.write(f"\n\n{argsList}\n")
    shellOut.flush()
    try:
        subprocess.run(argsList, stdout=shellOut, stderr=shellOut, timeout=timeout, check=check, **kwargs)
    except Exception as exc:
        logAndExit (f"shell: Failed to <{argsList}>. Check <shell.out> for more details.",exc=exc,exitCode=EXIT.Run)
    shellOut.close()

""" the tarArtifacts function can be executed from within exitFett -- should not use other functions to avoid recursion """
@decorate.debugWrap
def tarArtifacts (logAndExitFunc,getSettingFunc):
    artifactsPath = f"production-{getSettingFunc('prodJobId')}"

    if (os.path.isdir(artifactsPath)): # already exists, add the date
        artifactsPath += f"-{int(time.time())}"

    try:
        os.mkdir(artifactsPath)
    except Exception as exc:
        logAndExitFunc (message=f"Failed to create <{artifactsPath}>.",exc=exc)

    workDir = getSettingFunc('workDir')
    logFile = getSettingFunc('logFile')
    outFiles = glob.glob(os.path.join(workDir,'*.out'))
    configFile = getSettingFunc('configFile')

    # Tool's main artifacts
    listArtifacts = [configFile, logFile] +  outFiles

    for xArtifact in listArtifacts:
        try:
            shutil.copy2(xArtifact,artifactsPath)
        except Exception as exc:
            logAndExitFunc (message=f"Failed to copy <{xArtifact}> to <{artifactsPath}>.",exc=exc)

    # Extra artifacts
    extraArtifactsPath = getSettingFunc('extraArtifactsPath')
    if (extraArtifactsPath != 'UNKNOWN'): #The tool didn't fail to deploy
        try:
            shutil.copytree(extraArtifactsPath,os.path.join(artifactsPath,os.path.basename(extraArtifactsPath)))
        except Exception as exc:
            logAndExitFunc (message=f"Failed to copy <{extraArtifactsPath}> to <{artifactsPath}>.",exc=exc)

    tarFileName = f"{artifactsPath}.tar.gz"
    try:
        xFile = tarfile.open(name=tarFileName, mode="w:gz")
        xFile.add(artifactsPath, arcname=None)
        xFile.close()
    except Exception as exc:
        logAndExitFunc (message=f"tar: error creating {tarFileName}", exc=exc)

    printAndLog(f"tarArtifacts: Created <{tarFileName}> including all artifacts.")
    return tarFileName

@decorate.debugWrap
def setAdaptorUpDown (adaptorName, direction):
    sudoShellCommand(['ip','link','set', 'dev', adaptorName, direction])

@decorate.debugWrap
def zstdDecompress(inputFilePath, outputFilePath):
    """decompress a zstd file to an outputFilePath"""
    try:
        with open(pathlib.Path(inputFilePath), 'rb') as cfp:
            decomp = zstandard.ZstdDecompressor()
            with open(outputFilePath, 'wb') as destination:
                decomp.copy_stream(cfp, destination)
    except FileNotFoundError as exc:
        logAndExit(f"zstdDecompress: input file {inputFilePath} does not exist <{exc}>", exc=exc, exitCode=EXIT.Files_and_paths)
    except Exception as exc:
        logAndExit(f"zstdDecompress: error decompressing file {inputFilePath} <{exc}>", exc=exc, exitCode=EXIT.Run)

@decorate.debugWrap
def collectRemoteLogging (logAndExitFunc,getSettingFunc,sudoShellCommandFunc):
    printAndLog ("Fetching remote logs if there are any.")
    ipTarget = getSettingFunc(f"{getSettingFunc('target')}IpTarget")
    # cp the directory for non-fresh instances
    rsyslogsPath = os.path.join(getSettingFunc('extraArtifactsPath'),f"rsyslogs_{ipTarget}")
    sudoShellCommandFunc(['cp','-r',f'/var/log/{ipTarget}',rsyslogsPath],check=False)
    sudoShellCommandFunc(['chown','-R',f'{getpass.getuser()}:{getpass.getuser()}',rsyslogsPath],check=False) 

@decorate.debugWrap
def sha512_crypt(password, salt=None, rounds=None):
    """matches mkpasswd -m sha-512"""
    if salt is None:
        salt = crypt.mksalt(crypt.METHOD_SHA512, rounds=rounds)
    return crypt.crypt(password, salt)
