#! /usr/bin/env python3
""" 
Building OS images any other needed files
"""

from fett.base.utils.misc import *

@decorate.debugWrap
def prepareOsImage ():
    if(isEqSetting('osImage','FreeRTOS')):
        prepareFreeRTOS ()
    elif(isEqSetting('osImage','debian')):
        prepareDebian ()
    elif(isEqSetting('osImage','FreeBSD')):
        prepareFreeBSD ()

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOS():
    pass

@decorate.debugWrap
@decorate.timeWrap
def prepareDebian():
    # copy the crngOnDebian.riscv
    pass

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeBSD():
    pass