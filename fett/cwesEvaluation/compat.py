from fett.base.utils.misc import *

class testgenTargetCompatibilityLayer:
    """
    This class wraps a FETT target and presents a testgen target interface
    """
    def __init__(self, target):
        self.target = target
        self.targetObj = target

        setSetting('pocExploitsMode',False)

        if doesSettingExist("PPAC"):
            self.certsDir = os.path.join(getSetting('buildDir'),'lib_PPAC')
            if isEqSetting('osImage', 'FreeRTOS'):
                self.testPart = getSetting("currentTest")[2]

        # TODO: Set this to match target?
        self.filename = "compatibility"

        self.osImage = getSetting("osImage")

    def __getattr__ (self,attr):
        val = getattr(self.target,attr)
        return val

    def __setattr__ (self,name,value):
        if (name=='target'): # exception for the special 'target' member
            self.__dict__[name] = value
        else:
            setattr(self.target, name, value)

    def typCommand(self, command):
        # TODO: Better endsWith (will this even work for freebsd?)
        return self.target.runCommand(command,shutdownOnError=False)[1]

    # TODO: The real reportAndExit takes a bunch of optional params that we
    # should support
    def reportAndExit(self, message, **kwargs):
        logAndExit(message, **kwargs)
