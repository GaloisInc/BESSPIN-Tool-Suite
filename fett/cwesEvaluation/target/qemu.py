from fett.base.utils.misc import *
from fett.cwesEvaluation.compat import testgenTargetCompatabilityLayer
import fett.cwesEvaluation.scoreTests as scoreTests
import fett.target.qemu

# TODO: These imports wont work once we have multiple vuln classes
from fett.cwesEvaluation.tests.resourceManagement.scripts import cweTests, cweScores

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

        for test in getSetting("enabledCwesEvaluations"):
            self.executeTest(test)
        #self.interact()

        self.score()

    def executeTest (self,binTest):
        testName = binTest.split('.')[0]
        if (hasattr(cweTests,testName)):
            printAndLog(f"Executing {testName}...")
            outLog = getattr(getattr(cweTests,testName),testName)(
                    testgenTargetCompatabilityLayer(self), binTest)
        else:
            self.shutdownAndExit(f"<cwesEvaluation qemu>: Calling unknown "
                                 f"method <testName>.",
                                 exitCode=EXIT.Dev_Bug)


        logFile = os.path.join(getSetting('cwesEvaluationLogDir'),
                               f'{testName}.log')
        with open(logFile, 'w') as f:
            f.write(outLog)

    def score(self):
        # TODO: Load modules using SourceFileLoader
        module = cweScores

        # TODO: Allow custom scoring
        scorer = scoreTests.customScorerObj(False, None)

        # TODO: Make this configurable?
        csvPath = os.path.join(getSetting('workDir'), "scores.csv")

        scoreTests.main(module, scorer, csvPath)

