#! /usr/bin/env python3
""" 
Main fpga class + misc fpga functions
"""

from fett.base.utils.misc import *
from fett.target.common import *

class fpgaTarget (commonTarget):
    def __init__ (self):

        # For FreeBSD
        self.uartAttempts = 0
        self.limitUartAttempts = 8 if(isEqSetting('procFlavor','bluespec')) else 4

        super().__init__()
        return

@decorate.debugWrap
@decorate.timeWrap
def programBifile ():
    logAndExit (f"<fpga.programBifile> is not yet implemented.",exitCode=EXIT.Implementation)

@decorate.debugWrap
def resetEthAdaptor ():
    logAndExit (f"<fpga.resetEthAdaptor> is not yet implemented.",exitCode=EXIT.Implementation)
