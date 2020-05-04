#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def install (target):
    logAndExit (f"install: The install function for <voting> is not yet implemented.", exitCode=EXIT.Implementation)
    return ''

@decorate.debugWrap
@decorate.timeWrap
def deploy (target):
    return ''
