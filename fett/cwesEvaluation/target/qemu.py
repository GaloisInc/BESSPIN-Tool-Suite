from fett.base.utils.misc import *
from fett.cwesEvaluation.compat import testgenTargetCompatabilityLayer
import fett.target.qemu

# TODO: This import wont work once we have multiple vuln classes
from fett.cwesEvaluation.tests.resourceManagement.scripts import cweTests

class qemuTarget(fett.target.qemu.qemuTarget):

    @decorate.debugWrap
    @decorate.timeWrap
    def runApp(self, sendFiles=False, timeout=30): #executes the app
        if not sendFiles:
            self.shutdownAndExit("<runApp>: sendFiles must be True for CWEs "
                                 "evaluation",
                                 exitCode = EXIT.Configuration)
        self.sendTar(timeout=timeout)

        # Create directory for logs
        mkdir(os.path.join(getSetting('workDir'), 'cwesEvaluationLogs'),
              "cwesEvaluationLogDir")

        self.executeTest("test_188.riscv")
        #self.interact()

        self.shutdownAndExit(f"<runApp> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)


    def executeTest (self,binTest):
        testName = binTest.split('.')[0]
        if (hasattr(cweTests,testName)):
            outLog = getattr(getattr(cweTests,testName),testName)(
                    testgenTargetCompatabilityLayer(self), binTest)
        else:
            # TODO: I don't think reportAndExit is a real function
            self.reportAndExit ("Error in {0}: Calling unknown method <{1}>.".format(self.filename,testName))
            outLog = ''

        logFile = os.path.join(getSetting('cwesEvaluationLogDir'),
                               f'{testName}.log')
        with open(logFile, 'w') as f:
            # TODO: Log file will be empty if fell into the `else` branch above
            f.write(outLog)



