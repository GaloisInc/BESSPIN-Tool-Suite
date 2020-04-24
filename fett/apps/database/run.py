#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def runApp (target):
    # target is a fett target object
    outLog = ''
    # All we need to do is install sqlite into a suitable location,
    # like /usr/bin
    outLog += target.runCommand("echo \"Installing sqlite into /usr/bin...\"")[1]
    outLog += target.runCommand("install sqlite /usr/bin")[1]
    return outLog
