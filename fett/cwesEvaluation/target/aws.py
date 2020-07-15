from fett.base.utils.misc import *
from fett.cwesEvaluation.common import runTests
import fett.target.aws

class firesimTarget(fett.target.aws.firesimTarget):
    @decorate.debugWrap
    @decorate.timeWrap
    def runApp(self, sendFiles=False, timeout=30): #executes the app
        runTests(self, sendFiles, timeout)

class connectalTarget(fett.target.aws.connectalTarget):
    @decorate.debugWrap
    @decorate.timeWrap
    def runApp(self, sendFiles=False, timeout=30): #executes the app
        runTests(self, sendFiles, timeout)

