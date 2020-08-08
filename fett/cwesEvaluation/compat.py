from fett.base.utils.misc import *

# TODO: Many functions are still missing here

class testgenTargetCompatabilityLayer:
    """
    This class wraps a FETT target and presents a testgen target interface
    """
    def __init__(self, target):
        self.target = target
        self.targetObj = target

        self.settings = {"useCustomScoring" : getSetting("useCustomScoring"),
                         "processor" : getSetting('processor'),
                         "FPGANTK_IP_TARGET" : getSetting("fpgaIpTarget"),
                         "FPGANTK_IP_HOST" : getSetting("fpgaIpHost")}

        self.testsPars = {}
        if doesSettingExist("PPAC"):
            self.testsPars["SPOOFING_IP"] = getSettingDict("PPAC", "spoofingIP")
            self.testsPars["nAllowedInteractions"] = getSettingDict("PPAC", "test_nAllowedInteractions")
            self.testsPars["nAllowedAuthAttempts"] = getSettingDict("PPAC", "test_nAllowedAuthAttempts")
        if doesSettingExist("resourceManagement"):
            self.testsPars["nResourceLimit"] = getSettingDict("resourceManagement", "test_nResourceLimit")


        # TODO: Set this to match target?
        self.filename = "compatability"

        # TODO: Make this configurable?
        self.showExecutionOnScreen = False

        self.backend = ('fpga' if isEqSetting('target', 'aws')
                               else getSetting('target'))

    @property
    def onlySsh(self):
        return self.target.onlySsh

    @property
    def osImage(self):
        return getSetting("osImage")

    @property
    def isCurrentUserRoot(self):
        return self.target.isCurrentUserRoot

    @isCurrentUserRoot.setter
    def isCurrentUserRoot(self, value):
        self.target.isCurrentUserRoot = value

    @property
    def userName(self):
        return self.target.userName

    @userName.setter
    def userName(self, value):
        self.target.userName = value

    @property
    def userPassword(self):
        return self.target.userPassword

    @userPassword.setter
    def userPassword(self, value):
        self.target.userPassword = value

    @property
    def rootPassword(self):
        return self.target.rootPassword

    def typCommand(self, command):
        # TODO: Better endsWith (will this even work for freebsd?)
        return self.target.runCommand(command)[1]

    def runCommand(self, command, **kwargs):
        # TODO: Are these interfaces compatable enough?
        return self.target.runCommand(command, **kwargs)

    # TODO: The real reportAndExit takes a bunch of optional params that we
    # should support
    def reportAndExit(self, message):
        logAndExit(message)

    def switchUser(self):
        self.target.switchUser()

    def getGdbOutput(self):
        return self.target.getGdbOutput()

