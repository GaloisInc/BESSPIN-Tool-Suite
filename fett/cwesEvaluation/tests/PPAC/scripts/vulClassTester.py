#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom PPAC methods to run tests on qemu|fpga.
Note that the file will be loaded as a sourceFileModule, so using '.' is mandatory
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
import sys, os
from . import cweTests
from importlib.machinery import SourceFileLoader
import threading

class vulClassTester:
    """ should not be instantiated standalone; has to be done through classesHierarchy.py """
    def __init__ (self,settings):
        super().__init__(settings)
        return

    def executeTest (self,binTest):
        testName = binTest.split('.')[0]
        if (hasattr(cweTests,testName)):
            outLog = getattr(getattr(cweTests,testName),testName)(self,binTest)
            if ((self.osImage == 'FreeRTOS') and (self.backend == 'fpga')):
                for line in outLog.splitlines():
                    if ("INVALID" in line):
                        self.reportAndExit (f"Error in {self.filename}: Encountered <INVALID> while executing <{testName}>.",testError=True)
        elif (self.settings['pocExploitsMode']):
            try:
                pocTests = SourceFileLoader("pocTestsModule", os.path.join(sys.path[0],'..','..','poc-exploits','2_PPAC','pocTests','__init__.py')).load_module() 
            except:
                self.reportAndExit ("Error in {0}: Failed to load pocTests module. [Maybe you did not 'git submodule update --init'].".format(self.filename))
                outLog = ''
            if (hasattr(pocTests,testName)): #for poc-exploits
                outLog = getattr(getattr(pocTests,testName),testName)(self,binTest)
            else:
                self.reportAndExit ("Error in {0}: Calling unknown method <{1}>.".format(self.filename,testName))
                outLog = ''
        else:
            self.reportAndExit ("Error in {0}: Calling unknown method <{1}>.".format(self.filename,testName))
            outLog = ''
        if ((self.osImage == 'FreeRTOS') and self.showExecutionOnScreen):
            print (outLog)
        return outLog

    def executeOnRoot (self,commands):
        switchBack = not self.isCurrentUserRoot
        if (switchBack): #only do this if user is not root
            self.switchUser()
        for command in commands:
            self.runCommand (command,showOnScreen=self.showExecutionOnScreen)
        if (switchBack):
            self.switchUser()
        return

    def socketCloseAndCollect (self,xSocket):
        def closeSocket (xSocket):
            try:
                xSocket.close()
            except:
                self.reportFile.write("Warning: Unable to close socket.\n")
        xThread = threading.Thread(target=closeSocket, args=(xSocket,))
        xThread.daemon = True
        try:
            socketName = xSocket.getsockname()
        except:
            socketName = "UNKNOWN"
            self.reportFile.write("Warning: Unable to get socket name when closing. Maybe it was already closed.\n")
        self.trash.throwThread(xThread,f"closing socket <{socketName}>")
        xThread.start()
        return xThread