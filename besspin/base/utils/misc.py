#! /usr/bin/env python3
"""
Misc required functions for besspin.py
"""

import logging, enum, traceback, atexit
import os, shutil, glob, subprocess, pathlib
import tarfile, sys, json, re, getpass, time, configparser
import crypt, hashlib
import zstandard

from besspin.base.utils import decorate
from besspin.base.utils import aws

# private; not available using import *
_settings = dict()

# hardcoded URLs -- needed for emergency reporting
_settings['awsProdSqsQueueTX'] = 'https://sqs.us-west-2.amazonaws.com/065510690417/master-fettportal-InstanceStatusQueue-1H71N09IEKG3F.fifo'
_settings['awsProdS3Bucket'] = 'master-ssith-fett-target-researcher-artifacts'

_settings['awsDevSqsQueueTX'] = 'https://sqs.us-west-2.amazonaws.com/363527286999/develop-fettportal-InstanceStatusQueue-1DQ91T9W5DFZ1.fifo'
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

def exitBesspin (exitCode, preSetup=False):
    def inExit_logAndExit (message,exc=None):
        if (exc): #empty message
            message += f"\n{formatExc(exc)}."
     
        errorAndLog (f"inExit: {message}")
        exitCode = EXIT.AWS
        errorAndLog(f"End of BESSPIN! [Exit code {exitCode.value}:{exitCode}]")
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
    if (inExit_GetSetting('mode') == 'fettProduction'):
        if (exitCode != EXIT.Success): # ERRONEOUS STATE!! -- emergency upload
            collectRemoteLogging (inExit_logAndExit,inExit_GetSetting,inExit_sudoShellCommand) #Maybe we have some remote logs
            tarballPath = tarArtifacts (inExit_logAndExit,inExit_GetSetting)
            aws.uploadToS3(inExit_GetSetting(f'{inExit_GetSetting("besspinEntrypoint")}S3Bucket'), inExit_logAndExit, 
                            tarballPath, 'besspin/production/artifacts/')
            printAndLog(f"Artifacts tarball uploaded to S3.")

        jobStatus = 'success' if (exitCode == EXIT.Success) else 'failure'
        aws.sendSQS(inExit_GetSetting(f'{inExit_GetSetting("besspinEntrypoint")}SqsQueueTX'), inExit_logAndExit, jobStatus, 
                    inExit_GetSetting('prodJobId'), f"{inExit_GetSetting('prodJobId')}-TERM",
                    reason='besspin-production-termination',
                    hostIp=aws.getInstanceIp(inExit_logAndExit),
                    fpgaIp=inExit_GetSetting('remoteTargetIp')
                    )
        printAndLog("Sent termination message to the SQS queue.")

    exitMsg = f"End of BESSPIN! [Exit code {exitCode.value}:{exitCode}]"
    if (preSetup): 
        print(exitMsg)
    else: #Default, but should not use these until the trash and the logging setup is complete
        exitPeacefully(getSetting('trash'))
        printAndLog(exitMsg)
        
    os._exit(exitCode.value)

def exitOnInterrupt (xSig,xFrame):
    exitBesspin(EXIT.Interrupted)

def formatExc (exc):
    """ format the exception for printing """
    try:
        return f"<{exc.__class__.__name__}>: {exc}"
    except:
        return '<Non-recognized Exception>'

def printAndLog (message,doPrint=True,tee=None):
    if (doPrint):
        print("(Info)~  " + message, flush=True)
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
        print("(Warning)~  " + message, flush=True)
    logging.warning(message)
    if (exc):
        logging.warning(traceback.format_exc())
    
def errorAndLog (message,doPrint=True,exc=None):
    if (doPrint):
        print("(Error)~  " + message, flush=True)
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
    exitBesspin (exitCode)

@decorate.debugWrap
def setSetting (setting, val, targetId=None):
    if (targetId is not None):
        return setSettingDict(targetId,setting,val)
    try:
        _settings[setting] = val
    except Exception as exc:
        logAndExit (f"Failed to set setting <{setting}> to <{val}>.",exc=exc,exitCode=EXIT.Dev_Bug)

@decorate.debugWrap
def getSetting (setting, default=None, targetId=None):
    if (targetId is not None):
        return getSettingDict(targetId,setting,default=default)
    try:
        return _settings[setting]
    except Exception as exc:
        if default is not None:
            return default
        logAndExit (f"getSetting: Failed to obtain the value of <{setting}>.",exc=exc,exitCode=EXIT.Dev_Bug)

@decorate.debugWrap
def getSettingDict (setting, hierarchy, default=None, targetId=None):
    if (targetId is not None):
        if (isinstance(hierarchy,str)):
            return getSettingDict(targetId,[setting,hierarchy],default=default)
        else:
            return getSettingDict(targetId,[setting]+hierarchy,default=default)
    xSetting = getSetting(setting)
    if (isinstance(hierarchy,str)):
        hierarchy = [hierarchy]
    for item in hierarchy:
        try:
            xSetting = xSetting[item]
        except Exception as exc:
            if default is not None:
                return default
            hierarchyPretty = ''.join([f"[{x}]" for x in hierarchy])
            logAndExit (f"getSetting: Failed to obtain the value of <[{setting}]{hierarchyPretty}>.",exc=exc,exitCode=EXIT.Dev_Bug)
    return xSetting

@decorate.debugWrap
def setSettingDict (setting, hierarchy, val, targetId=None):
    if (targetId is not None):
        if (isinstance(hierarchy,str)):
            setSettingDict(targetId,[setting,hierarchy],val)
        else:
            setSettingDict(targetId,[setting]+hierarchy,val)

    if (isinstance(hierarchy,str)): #convert to list
        hierarchy = [hierarchy] 

    newDict = val
    while (hierarchy): 
        # recursively create a dict bottom-up
        # Note that it has to be fetched/updated per level not to lose any data
        key = hierarchy.pop()
        newDict = {key : newDict}

        if (doesSettingExistDict(setting, hierarchy)):
            oldDict = getSettingDict(setting, hierarchy)
            oldDict.update(newDict)
            setSettingDict(setting, hierarchy, oldDict)
        else: #it's a new setting
            setSettingDict(setting, hierarchy, newDict) #This can be called with an empty hierarchy, then it will just return

@decorate.debugWrap
def isEnabled(setting, targetId=None, default=None):
    val = getSetting(setting, targetId=targetId, default=default)
    if (isinstance(val,bool)):
        return val
    else:
        logAndExit (f"isEnabled: The value of <{setting}> is not boolean: <{val}>.",exitCode=EXIT.Dev_Bug)

@decorate.debugWrap
def isEnabledDict(setting, hierarchy, targetId=None, default=None):
    val = getSettingDict(setting, hierarchy, targetId=targetId, default=default)
    if isinstance(val, bool):
        return val
    else:
        logAndExit(f"isEnabledDict: The value of <{setting}[{hierarchy}]> is "
                   f"not boolean: <{val}>",
                   exitCode=EXIT.Dev_Bug)

@decorate.debugWrap
def isEqSetting (setting, val, targetId=None):
    return (getSetting(setting, targetId=targetId) == val)

@decorate.debugWrap
def isEqSettingDict(setting, hierarchy, val, targetId=None):
    return (getSettingDict(setting, hierarchy, targetId=targetId) == val)

@decorate.debugWrap
def doesSettingExist (setting, targetId=None):
    if (targetId is not None):
        return doesSettingExistDict(targetId, setting)
    else:
        return (setting in _settings)

@decorate.debugWrap
def doesSettingExistDict(setting, hierarchy, targetId=None):
    if (targetId is not None):
        if (isinstance(hierarchy,str)):
            return doesSettingExistDict(targetId,[setting,hierarchy])
        else:
            return doesSettingExistDict(targetId,[setting]+hierarchy)
    xSetting = getSetting(setting)
    if isinstance(hierarchy, str):
        hierarchy = [hierarchy]
    for item in hierarchy:
        if item in xSetting:
            xSetting = xSetting[item]
        else:
            return False
    return True

def dumpSettings ():
    logging.debug(f"settings = {_settings}")

def mkdir(dirPath, addToSettings=None, exitIfExists=True):
    try:
        os.mkdir(dirPath)
        logging.debug(f"Created directory <{dirPath}>.")
    except FileExistsError as exc:
        if exitIfExists:
            logAndExit(f"<{dirPath}> already exists.",
                       exitCode=EXIT.Files_and_paths,
                       exc=exc)
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
        if (not renameDest):
            dest = os.path.join(dest,os.path.basename(os.path.normpath(src)))
        try:
            shutil.copytree(src, dest)
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

def safeLoadJsonFile (jsonFile, emptyIfNoFile=False):
    fJson = ftOpenFile(jsonFile, 'r', exitOnFileError=(not emptyIfNoFile))
    try:
        jsonData = json.load(fJson)
        fJson.close()
    except Exception as exc:
        if (emptyIfNoFile and (fJson is None)):
            return {}
        logAndExit(f"Failed to load json file <{jsonFile}>.",exc=exc,exitCode=EXIT.Files_and_paths)
    return jsonData

def safeDumpJsonFile(jsonData, jsonFile, indent=None):
    fJson = ftOpenFile(jsonFile, 'w')
    try:
        json.dump(jsonData, fJson, indent=indent)
        fJson.close()
    except Exception as exc:
        logAndExit(f"Failed to dump json <{jsonData}> to file <{jsonFile}>",
                   exc=exc,
                   exitCode=EXIT.Files_and_paths)

def safeLoadIniFile (iniFile):
    fConfig = ftOpenFile(iniFile, 'r')
    xConfig = configparser.ConfigParser()
    try:
        xConfig.optionxform = str # Hack it to be case sensitive
        xConfig.read_file(fConfig)
        fConfig.close()
    except Exception as exc:
        logAndExit(f"Failed to read configuration file <{iniFile}>.",exc=exc,exitCode=EXIT.Files_and_paths)
    return xConfig

def safeDumpIniFile(xConfig, iniFile):
    fConfig = ftOpenFile(iniFile, 'w')
    try:
        xConfig.write(fConfig,space_around_delimiters=True)
        fConfig.close()
    except Exception as exc:
        logAndExit(f"Failed to dump config data <{xConfig}> to file <{iniFile}>",
                   exc=exc, exitCode=EXIT.Files_and_paths)

@decorate.debugWrap
def make (argsList,dirPath,dockerToolchainImage=None,dockerExtraMounts={},targetId=None, buildDir=None):
    if ((not dirPath) or (argsList is None)):
        logAndExit (f"make: <dirPath={dirPath}> or <argsList={argsList}> cannot be empty/None.",exitCode=EXIT.Dev_Bug)
    # open a file for stdout/stderr
    if (buildDir is None):
        buildDir = getSetting('buildDir',targetId=targetId)
    outMake = ftOpenFile(os.path.join(buildDir,'make.out'),'a')

    if (dockerToolchainImage):
        dockerArgsList = ['sudo', 'docker', 'run', '-it', '--privileged=true',
                          '-v', f'{dirPath}:/root/makeDir']
        for hostPath, dockerPath in dockerExtraMounts.items():
            dockerArgsList += ['-v', f'{hostPath}:{dockerPath}']
        dockerArgsList += [dockerToolchainImage,
                           'bash', '-c', f'cd /root/makeDir; make {" ".join(argsList)}']
        argsList = dockerArgsList
    else:
        argsList = ['make','-C',dirPath] + argsList
        
    logging.info(f"Executing <{' '.join(argsList)}>. Command output is appended to <{outMake.name}>.")
    outMake.write(f"{' '.join(argsList)}\n\n")
    outMake.flush()
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
    trash = getSetting('trash') #do not use getSetting within a try/except
    try:
        xFile = open(filePath,mode)
        trash.throwFile(xFile)
        return xFile
    except Exception as exc:
        errMsg = f"Failed to open <{filePath}> to {modeName}."
        if (exitOnFileError):
            logAndExit (errMsg,exc=exc,exitCode=EXIT.Files_and_paths)
        else:
            errorAndLog(f"{errMsg} Will continue anyway.",doPrint=False,exc=exc)
            return None    

@decorate.debugWrap
def ftReadLines (filePath,exitOnFileError=True,splitLines=True):
    xFile = ftOpenFile (filePath,'r',exitOnFileError=exitOnFileError)
    if ((not xFile) and (not exitOnFileError)):
        return []
    try:
        if (splitLines):
            lines = xFile.read().splitlines()
        else:
            lines = xFile.read()
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
    logging.debug(f"curlRequest: command: <curl {' '.join(options)} {url}>")
    try:
        p = subprocess.run (['curl'] + options + [url], capture_output=True, check=True)
        out = p.stdout.decode('utf-8')
        logging.debug(f"curlRequest: output: <<<{out}>>>.")
    except Exception as exc:
        errorAndLog (f"Failed to run <curl {' '.join(options)} {url}>.", exc=exc, doPrint=False)
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
    return shellCommand (command, check=check, timeout=timeout, **kwargs)

@decorate.debugWrap
def shellCommand (argsList, check=True, timeout=30, **kwargs):
    shellOut = ftOpenFile(os.path.join(getSetting('workDir'),'shell.out'),'a')
    shellOut.write(f"\n\n{argsList}\n")
    shellOut.flush()
    try:
        retRun = subprocess.run(argsList, stdout=shellOut, stderr=shellOut, timeout=timeout, check=check, **kwargs)
    except Exception as exc:
        if ((not check) and (exc.__class__ == subprocess.TimeoutExpired)):
            warnAndLog (f"shell: Timeout in <{argsList}>. Will continue anyway since <check> is disabled.",
                exc=exc, doPrint=False)
            retRun = subprocess.CompletedProcess(argsList,1) #return empty stdout/stderr and error code of 1
        else:
            logAndExit (f"shell: Failed to <{argsList}>. Check <shell.out> for more details.",exc=exc,exitCode=EXIT.Run)
    shellOut.close()
    return retRun

""" the tarArtifacts function can be executed from within exitBesspin -- should not use other functions to avoid recursion """
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
    ipTarget = getSettingFunc(f"awsf1IpTarget")
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

@decorate.debugWrap
@decorate.timeWrap
def computeMd5ForFile (filepath):
    BLOCKSIZE = 65536
    fIn = ftOpenFile(filepath, "rb")
    try:
        md5 = hashlib.md5()
        while True:
            chunk = fIn.read(BLOCKSIZE)
            if (not chunk):
                break
            md5.update(chunk)
        md5Val = md5.hexdigest()
    except Exception as exc:
        logAndExit(f"Failed to compute md5 for <{filepath}>.", exc=exc, exitCode=EXIT.Files_and_paths)
    fIn.close()
    return md5Val

@decorate.debugWrap
def multicastFromHostIp(hostIp: str):
    try:
        hostIp = hostIp.split('.')
        hostIp[-1] = 255
        multicastIp = '.'.join([str(octet) for octet in hostIp])
    except Exception as exc:
        logAndExit(f"Failed to compute multicast IP from <{hostIp}>.", exc=exc, exitCode=EXIT.Unspecified)
    return multicastIp
