#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom PPAC methods to run tests on qemu|fpga.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import sys, os
from besspin.cwesEvaluation.compat import cwesEvaluationCompatibilityLayer
from besspin.cwesEvaluation.PPAC import cweTests
from importlib.machinery import SourceFileLoader
import threading

from besspin.base.utils.misc import *

class vulClassTester(cwesEvaluationCompatibilityLayer):
    def __init__ (self,settings):
        super().__init__(settings)
        return

    def executeTest (self,binTest):
        testName = binTest.split('.')[0]
        if (hasattr(cweTests,testName)):
            outLog = getattr(getattr(cweTests,testName),testName)(self,binTest)
        elif (isEnabled('pocExploitsMode')):
            self.terminateAndExit('<pocExploitsMode> not implemented',
                       exitCode=EXIT.Implementation)
        else:
            self.terminateAndExit(f"Calling unknown method <{testName}>.",exitCode=EXIT.Dev_Bug)
            outLog = ''
        return outLog

    def executeOnRoot (self,commands):
        switchBack = not self.isCurrentUserRoot
        if (switchBack): #only do this if user is not root
            self.switchUser()
        for command in commands:
            self.runCommand (command)
        if (switchBack):
            self.switchUser()
        return

    def socketCloseAndCollect (self,xSocket):
        def closeSocket (xSocket):
            try:
                xSocket.close()
            except Exception as exc:
                warnAndLog("Unable to close socket.\n",doPrint=False,exc=exc)
        xThread = threading.Thread(target=closeSocket, args=(xSocket,))
        xThread.daemon = True
        try:
            socketName = xSocket.getsockname()
        except Exception as exc:
            socketName = "UNKNOWN"
            warnAndLog("Unable to get socket name when closing. Maybe it was already closed.\n",doPrint=False,exc=exc)
        getSetting('trash').throwThread(xThread,f"closing socket <{socketName}>")
        xThread.start()
        return xThread
