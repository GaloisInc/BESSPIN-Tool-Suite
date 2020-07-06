#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has the custom resourceManagement methods to run tests on qemu|fpga.
Note that the file will be loaded as a sourceFileModule, so using '.' is mandatory
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from . import cweTests

class vulClassTester:
    """ should not be instantiated standalone; has to be done through classesHierarchy.py """
    def __init__(self,settings):
        super().__init__(settings)
        return

    def executeTest (self,binTest):
        testName = binTest.split('.')[0]
        if (hasattr(cweTests,testName)):
            outLog = getattr(getattr(cweTests,testName),testName)(self,binTest)
        else:
            self.reportAndExit ("Error in {0}: Calling unknown method <{1}>.".format(self.filename,testName))
            outLog = ''
        return outLog

    def typCommand (self, command):
        return self.runCommand(command,showOnScreen=self.showExecutionOnScreen,shutdownOnError=False)[1]
    
