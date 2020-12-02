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

    def isTestInfoEnabled (self,testName,infoName):
        return isTestInfoEnabled(self.vulClass,testName,infoName)

    def defaultTest(self, testNum, binTest):
        self.terminateAndExit (f"<defaultTest> is not yet implemented for <{self.vulClass}>.",exitCode=EXIT.Dev_Bug)
        return

    def recommendationTest(self, testName):
        return f'<TEXT={getSettingDict(self.vulClass,["testsInfo",testName,"text"])}>\n'