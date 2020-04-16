#! /usr/bin/env python3
"""
Main logging functions
"""

import logging, enum
from fett.base.utils import decorate

settings = dict()

class EXIT (enum.Enum):
    Success = 0
    Unspecified = enum.auto()
    Nothing_to_do = enum.auto()
    Configuration = enum.auto()
    Create_path = enum.auto()
    File_read = enum.auto()

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
    exitFett (exitCode)

def setSetting (setting, val):
    global settings
    try:
        settings[setting] = val
    except Exception as exc:
        logAndExit (f"Failed to set setting <{setting}> to <{val}>.",exc=exc)

def getSetting (setting):
    global settings
    try:
        return settings[setting]
    except Exception as exc:
        logAndExit (f"getSetting: Failed to obtain the value of <{setting}>.",exc=exc)

def isEnabled(setting):
    return getSetting(setting)

def isEqSetting (setting,val):
    return (getSetting(setting) == val)

def dumpSettings ():
    global settings
    logging.debug(f"settings = {settings}")
