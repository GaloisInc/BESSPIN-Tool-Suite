from fett.base.utils.misc import *

class testgenTargetCompatibilityLayer:
    """
    This class wraps a FETT target and presents a testgen target interface
    """
    def __init__(self, target):
        self.target = target

        setSetting('pocExploitsMode',False)

        if doesSettingExist("PPAC"):
            self.certsDir = os.path.join(getSetting('buildDir'),'lib_PPAC')
            if isEqSetting('osImage', 'FreeRTOS'):
                self.testPart = getSetting("currentTest")[2]

        self.osImage = getSetting("osImage")

    def __getattr__ (self,attr):
        return getattr(self.target,attr)

    def __setattr__ (self,name,value):
        if (name=='target'): # exception for the special 'target' member
            self.__dict__[name] = value
        else:
            setattr(self.target, name, value)

    def typCommand(self, command): #Note that this returns the `textBack`
        return self.target.runCommand(command,exitOnError=False)[1]

