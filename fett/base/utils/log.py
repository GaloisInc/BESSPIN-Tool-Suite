#! /usr/bin/env python3
"""
Main logging functions
"""

import logging
from fett.base.utils import decorate

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

