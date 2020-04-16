#! /usr/bin/env python3
"""
Main logging functions
"""

import logging, enum, traceback
import os, shutil, glob
from fett.base.utils import decorate

settings = dict()

class EXIT (enum.Enum):
    Success = 0
    Unspecified = enum.auto()
    Nothing_to_do = enum.auto()
    Configuration = enum.auto()
    Create_path = enum.auto()
    File_read = enum.auto()
    Environment = enum.auto()
    Implementation = enum.auto()
    Global_settings_handling = enum.auto()
    Copy_and_Move = enum.auto()

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

def printAndLog (message):
    print("(Info)~  " + message)
    logging.info(message)

def warnAndLog (message):
    print("(Warning)~  " + message)
    logging.warning(message)

def errorAndLog (message):
    print("(Error)~  " + message)
    logging.error(message)

@decorate.debugWrap
def logAndExit (message,exc=None,exitCode=EXIT.Unspecified):
    if (exc):
        message += f"\n{formatExc(exc)}."
    errorAndLog(message)
    if (exc):
        logging.error(traceback.format_exc())
    exitFett (exitCode)

def setSetting (setting, val):
    global settings
    try:
        settings[setting] = val
    except Exception as exc:
        logAndExit (f"Failed to set setting <{setting}> to <{val}>.",exc=exc,exitCode=EXIT.Global_settings_handling)

def getSetting (setting):
    global settings
    try:
        return settings[setting]
    except Exception as exc:
        logAndExit (f"getSetting: Failed to obtain the value of <{setting}>.",exc=exc,exitCode=EXIT.Global_settings_handling)

def isEnabled(setting):
    return getSetting(setting)

def isEqSetting (setting,val):
    return (getSetting(setting) == val)

def dumpSettings ():
    global settings
    logging.debug(f"settings = {settings}")

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
            logAndExit (f"cp: source cannot be of NoneType.",exitCode=EXIT.Copy_and_Move)
        else:
            logAndExit (f"cp: destination cannot be of NoneType.",exitCode=EXIT.Copy_and_Move)
    
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
                    shutil.copy2(xFile,dst)
                except Exception as exc:
                    logAndExit (f"Failed to copy <{xFile}> to <{dest}>.",exc=exc,exitCode=EXIT.Copy_and_Move)
    else:
        if (not os.path.isfile(src)):
            logAndExit (f"cp: <{src}> is not a valid file.",exitCode=EXIT.Copy_and_Move)
        try:
            shutil.copy2(src,dst)
        except Exception as exc:
            logAndExit (f"Failed to copy <{src}> to <{dest}>.",exc=exc,exitCode=EXIT.Copy_and_Move)
    







