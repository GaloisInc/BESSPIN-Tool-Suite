#! /usr/bin/env python3
""" 
Main qemu class + misc qemu functions
"""

from fett.base.utils.misc import *
from fett.target.common import *

class qemuTarget (commonTarget):
    def __init__ (self):

        super().__init__()
        return