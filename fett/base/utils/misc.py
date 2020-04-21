#! /usr/bin/env python3
"""
Main logging functions
"""

import logging, enum, traceback, atexit
import os, shutil, glob, subprocess
from fett.base.utils import decorate

# private; not available using import *
_settings = dict()

class EXIT (enum.Enum):
    Success = 0
    Unspecified = enum.auto()
    Nothing_to_do = enum.auto()
    Configuration = enum.auto()
    Create_path = enum.auto()
    File_read = enum.auto()
    Environment = enum.auto()
    Implementation = enum.auto()
    Copy_and_Move = enum.auto()
    Dev_Bug = enum.auto()
    External = enum.auto()
    Run = enum.auto()
    Network = enum.auto()

    def __str__ (self): #to replace '_' by ' ' when printing
        return f"{self.name.replace('_',' ')}"

def exitFett (exitCode):
    if (not isinstance(exitCode,EXIT)):
        exitCode = EXIT.Unspecified
    printAndLog(f"End of FETT! [Exit code {exitCode.value}:{exitCode}]")
    exit(exitCode.value)

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

def dumpSettings ():
    logging.debug(f"settings = {_settings}")

def mkdir(dirPath, addToSettings=None):
    try:
        os.mkdir(dirPath)
        logging.debug(f"Created directory <{dirPath}>.")
    except Exception as exc:
        logAndExit (f"Failed to create <{dirPath}>.",exitCode=EXIT.Create_path,exc=exc)
    if (addToSettings):
        setSetting(addToSettings,dirPath)

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
        logAndExit (f"Failed to open <{filePath}> to {modeName}.",exc=exc,exitCode=EXIT.Create_path)    











