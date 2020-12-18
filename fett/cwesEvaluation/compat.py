from fett.base.utils.misc import *

class testgenTargetCompatibilityLayer:
    """
    This class wraps a FETT target and presents a testgen target interface
    """
    def __init__(self, target):
        self.objTarget = target
        self.osImage = getSetting("osImage")

    def __getattr__ (self,attr):
        return getattr(self.objTarget,attr)

    def __setattr__ (self,name,value):
        if (name=='objTarget'): # exception for the special 'objTarget' member
            self.__dict__[name] = value
        else:
            setattr(self.objTarget, name, value)

    def typCommand(self, command): #Note that this returns the `textBack`
        return self.objTarget.runCommand(command,exitOnError=False)[1]

    def defaultTest(self, testNum, binTest):
        self.terminateAndExit (f"<defaultTest> is not yet implemented for <{self.vulClass}>.",exitCode=EXIT.Dev_Bug)
        return

    def executeTest (self,binTest):
        if (self.vulClass not in ["PPAC", "hardwareSoC"]):
            self.terminateAndExit (f"<executeTest> is not implemented for <{self.vulClass}>.",exitCode=EXIT.Dev_Bug)
        
        outLog = ''
        try:
            testName = binTest.split('.')[0]
        except Exception as exc:
            self.terminateAndExit (f"executeTest: Failed to parse <{binTest}>.",exc=exc,exitCode=EXIT.Dev_Bug)

        outLog = "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        return outLog