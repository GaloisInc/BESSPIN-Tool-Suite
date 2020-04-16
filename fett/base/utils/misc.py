#! /usr/bin/env python3
"""
Main logging functions
"""

import logging
from fett.base.utils import decorate

settings = dict()

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
def logAndExit (message,exc=None,exitCode=1):
    if (exc):
        message += f"\n{formatExc(exc)}."
    errorAndLog(message)
    exit (exitCode)

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

def isSetting (setting,val):
    return (getSetting(setting) == val)

def dumpSettings ():
    global settings
    logging.debug(f"settings = {settings}")
