from fett.base.utils.misc import *
from fett.cwesEvaluation.common import runTests
import fett.target.qemu

class qemuTarget(fett.target.qemu.qemuTarget):
    @decorate.debugWrap
    @decorate.timeWrap
    def runApp(self, sendFiles=False, timeout=30): #executes the app
        runTests(self, sendFiles, timeout)

