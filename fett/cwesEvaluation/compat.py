from fett.base.utils.misc import *

# TODO: Many functions are still missing here

class testgenTargetCompatabilityLayer:
    """
    This class wraps a FETT target and presents a testgen target interface
    """
    def __init__(self, target):
        self.target = target

        # TODO: Populate dicts from config file
        self.testsPars = {"nResourceLimit" : 10}
        self.settings = {"useCustomScoring" : False}

    @property
    def osImage(self):
        return getSetting("osImage")

    def typCommand(self, command):
        return self.target.runCommand(command)[1]

