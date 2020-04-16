#! /usr/bin/env python3
""" 
Building apps
"""

from fett.base.utils.misc import *

@decorate.debugWrap
def buildApps ():
    if (isEnabled('https')):
        buildHttps()
    elif (isEnabled('ota')):
        buildOta()
    elif (isEnabled('webserver')):
        buildWebserver()
    elif (isEnabled('database')):
        buildDatabase()

@decorate.debugWrap
@decorate.timeWrap
def buildHttps():
    pass

@decorate.debugWrap
@decorate.timeWrap
def buildOta():
    pass

@decorate.debugWrap
@decorate.timeWrap
def buildWebserver():
    pass

@decorate.debugWrap
@decorate.timeWrap
def buildDatabase():
    pass