#! /usr/bin/env python3
"""
Misc required functions for fett.py
"""

import logging, enum, traceback, atexit
import os, shutil, glob, subprocess
import tarfile, sys, re

from fett.base.utils import decorate

# private; not available using import *
_settings = dict()

class EXIT (enum.Enum):
    Success = 0
    Unspecified = enum.auto()
    Nothing_to_do = enum.auto()
    Configuration = enum.auto()
    Files_and_paths = enum.auto()
    Environment = enum.auto()
    Implementation = enum.auto()
    Copy_and_Move = enum.auto()
    Dev_Bug = enum.auto()
    External = enum.auto()
    Run = enum.auto()
    Network = enum.auto()
    Interrupted = enum.auto()
    Tar = enum.auto()

    def __str__ (self): #to replace '_' by ' ' when printing
        return f"{self.name.replace('_',' ')}"

def exitFett (exitCode):
    if (not isinstance(exitCode,EXIT)):
        exitCode = EXIT.Unspecified
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

def printAndLog (message,doPrint=True):
    if (doPrint):
        print("(Info)~  " + message)
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

def getSetting (setting):
    try:
        return _settings[setting]
    except Exception as exc:
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
        tarFile = tarfile.open(name=tarFileName, mode="x:gz")
    except Exception as e:
        logAndExit (f"tar: error creating {tarFileName}", exc=e, exitCode=EXIT.Tar)
    for f in filesList:
        arcname = None
        if type(f) == tuple:
            arcname = f[0]
            f       = f[1]
        try:
            tarFile.add(f, arcname=arcname)
        except Exception as e:
            logAndExit (f"tar: error adding {f} to {tarFileName}", exc=e, exitCode=EXIT.Tar)
    try:
        tarFile.close()
    except Exception as e:
            logAndExit (f"tar: error closing {tarFileName}", exc=e, exitCode=EXIT.Tar)

@decorate.debugWrap
def cp (src,dest,pattern=None):
    if ((not src) or (not dest)):
        if (not src):
            logAndExit (f"cp: source cannot be of NoneType.",exitCode=EXIT.Dev_Bug)
        else:
            logAndExit (f"cp: destination cannot be of NoneType.",exitCode=EXIT.Dev_Bug)
    
    if (pattern):
        if (not os.path.isdir(src)):
            logAndExit (f"cp: pattern has to have a valid source dir <{src}>.",exitCode=EXIT.Copy_and_Move)
        if (not os.path.isdir(dest)):
            logAndExit (f"cp: pattern has to have a valid destination dir <{dest}>.",exitCode=EXIT.Copy_and_Move)
        try:
            listFiles = glob.glob(os.path.join(src, pattern))
        except Exception as exc:
            logAndExit (f"Failed to list <{src}/{pattern}>.",exc=exc,exitCode=EXIT.Copy_and_Move)
        for xFile in listFiles:
            if (os.path.isfile(xFile)):
                try:
                    shutil.copy2(xFile,dest)
                except Exception as exc:
                    logAndExit (f"Failed to copy <{xFile}> to <{dest}>.",exc=exc,exitCode=EXIT.Copy_and_Move)
    else:
        if (not os.path.isfile(src)):
            logAndExit (f"cp: <{src}> is not a valid file.",exitCode=EXIT.Copy_and_Move)
        try:
            shutil.copy2(src,dest)
        except Exception as exc:
            logAndExit (f"Failed to copy <{src}> to <{dest}>.",exc=exc,exitCode=EXIT.Copy_and_Move)

@decorate.debugWrap
def copyDir(src,dest,renameDest=False,copyContents=False):
    if ((not src) or (not dest)):
        logAndExit(f"copyDir: source or destination cannot be of NoneType", exitCode=EXIT.Dev_Bug)
    if (not os.path.isdir(src)):
        logAndExit(f"copyDir: invalid source dir <{src}>.",exitCode=EXIT.Copy_and_Move)
    if ((not renameDest) and (not os.path.isdir(dest))):
        logAndExit(f"copyDir: invalid destination dir <{dest}>.",exitCode=EXIT.Copy_and_Move)
    if(renameDest and copyContents): #that doesn't make sense
        logAndExit(f"copyDir: Cannot call with both renameDest and copyContents.", exitCode=EXIT.Dev_Bug)

    def copyTree (srcTree,destTree):
        try:
            shutil.copytree(srcTree, os.path.join(destTree,os.path.basename(os.path.normpath(srcTree))))
        except Exception as exc:
            logAndExit (f"Failed to copy directory <{srcTree}> to <{destTree}>.",exc=exc,exitCode=EXIT.Copy_and_Move)

    if (copyContents):
        #first, copy files
        cp(src,dest,pattern='*')
        #second, copy dirs -- no need to check walk as we check it's dir, and if it's empty, listDirs will = []
        recursiveContents = [listDirs for dirName,listDirs,listFiles in os.walk(src)]
        listDirs = recursiveContents[0]
        for xDir in listDirs:
            copyDir(os.path.join(src,xDir),dest)
    else:
        copyTree(src,dest)

@decorate.debugWrap
def make (argsList,dirPath):
    if ((not dirPath) or (argsList is None)):
        logAndExit (f"make: <dirPath={dirPath}> or <argsList={argsList}> cannot be empty/None.",exitCode=EXIT.Dev_Bug)
    # open a file for stdout/stderr
    outMake = ftOpenFile(os.path.join(dirPath,'make.out'),'a')

    argsList = ['make','-C',dirPath] + argsList
    logging.info(f"Executing <{' '.join(argsList)}>. Command output is appended to <{outMake.name}>.")
    try:
        subprocess.check_call(argsList, stdout=outMake, stderr=outMake)
    except Exception as exc:
        outMake.close()
        logAndExit (f"Failed to <{' '.join(argsList)}>.",exc=exc,exitCode=EXIT.External)

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

def ftOpenFile (filePath,mode):
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
        logAndExit (f"Failed to open <{filePath}> to {modeName}.",exc=exc,exitCode=EXIT.Files_and_paths)    

def ftReadLines (filePath):
    xFile = ftOpenFile (filePath,'r')
    try:
        lines = xFile.read().splitlines()
        xFile.close()
        return lines
    except Exception as exc:
        logAndExit (f"Failed to read lines from <{filePath}>.",exc=exc,exitCode=EXIT.Files_and_paths)
    
def matchExprInLines (expr,lines):
    if (not lines):
        return None
    for line in lines:
        xMatch = re.match(expr,line)
        if (xMatch is not None):
            return xMatch
    return None








