#! /usr/bin/env python3
"""
Building any binaries or images for cyberPhys
"""

from fett.base.utils.misc import *


@decorate.debugWrap
@decorate.timeWrap
def buildCyberPhys (targetId=None):
    targetInfo = f" <for target{targetId}>" if (targetId) else ''
    warnAndLog(f"Nothing to build for cyberPhys yet{targetInfo}.")