#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""
from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def install (target):
    # target is a fett target object
    appLog = getSetting('appLog')
    # TODO: carry app filename in dictionary
    # TODO: start a service
    target.runCommand("install ota.elf /usr/local/sbin/otaserver",tee=appLog)
    target.runCommand("otaserver",tee=appLog)