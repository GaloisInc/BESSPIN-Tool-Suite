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
                         "processor" : getSetting('processor')}

        self.testsPars = {}
        if doesSettingExist("PPAC"):
            self.testsPars["SPOOFING_IP"] = getSettingDict("PPAC", "spoofingIP")
            self.testsPars["nAllowedInteractions"] = getSettingDict("PPAC", "test_nAllowedInteractions")
            self.testsPars["nAllowedAuthAttempts"] = getSettingDict("PPAC", "test_nAllowedAuthAttempts")
            self.certsDir = os.path.join(getSetting('buildDir'),'lib_PPAC')
            if isEqSetting('osImage', 'FreeRTOS'):
                self.testsPars['TESTGEN_TEST_PART'] = getSetting("currentTest")[2]
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

    @property
    def sshRetries(self):
        return self.target.sshRetries

    @sshRetries.setter
    def sshRetries(self, value):
        self.target.sshRetries = value

    @property
    def sshLimitRetries(self):
        return self.target.sshLimitRetries

    @sshLimitRetries.setter
    def sshLimitRetries(self, value):
        self.target.sshLimitRetries = value

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

    def closeSshConn(self):
        self.target.closeSshConn()

    def killSshConn(self):
        self.target.killSshConn()

    def openSshConn(self, **kwargs):
        return self.target.openSshConn(**kwargs)

    def activateEthernet(self):
        return self.target.activateEthernet()

    @property
    def ipTarget(self):
        return self.target.ipTarget

    @property
    def portTarget(self):
        return self.target.portTarget

    @property
    def ipHost(self):
        return self.target.ipHost

    @property
    def portHost(self):
        return self.target.portHost

    def readFromTarget(self, *args, **kwargs):
        # TODO: Are these interfaces compatable enough?
        return self.target.readFromTarget(*args, **kwargs)

