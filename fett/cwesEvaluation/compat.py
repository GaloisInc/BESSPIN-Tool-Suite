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

        # TODO: Set this to match target?
        self.filename = "compatability"

    @property
    def osImage(self):
        return getSetting("osImage")

    def typCommand(self, command):
        # TODO: Better endsWith (will this even work for freebsd?)
        return self.target.runCommand(command)[1]

    # TODO: The real reportAndExit takes a bunch of optional params that we
    # should support
    def reportAndExit(self, message):
        logAndExit(message)

