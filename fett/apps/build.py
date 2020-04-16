#! /usr/bin/env python3
""" 
Building apps
"""

from fett.base.utils.misc import *
import os

@decorate.debugWrap
def buildApps ():
    # create the build directory
    buildDir = os.path.join(getSetting('workDir'),'build')
    mkdir(buildDir,addToSettings='buildDir')

    if (isEnabled('buildApps')):
        # copy makefiles and such
        pass

    if (isEnabled('https')):
        buildHttps()
    elif (isEnabled('ota')):
        buildOta()
    elif (isEnabled('webserver')):
        buildWebserver()
    elif (isEnabled('database')):
        buildDatabase()

"""
- FreeRTOS, building an app means copying the C files/headers/.mk env files to the workDir to prepare for os build.
- Unix: if building is disabled, then nothing to do here. If building is enabled, then we copy and compile here.
"""

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
    sourceDir = os.path.join(getSetting('repoDir'),'fett','apps','database')
    if (isEnabled('buildApps')):
        cp (sourceDir,getSetting('buildDir'),pattern="*.c")
    pass

