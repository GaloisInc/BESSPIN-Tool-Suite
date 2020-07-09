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

        self.shutdownAndExit(f"<runApp> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)


    def executeTest (self,binTest):
        testName = binTest.split('.')[0]
        if (hasattr(cweTests,testName)):
            printAndLog(f"Executing {testName}...")
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

    def score(self):
        # TODO: Load modules using SourceFileLoader
        module = cweScores

        # TODO: Allow custom scoring
        scorer = scoreTests.customScorerObj(False, None)

        # TODO: Make this configurable?
        csvPath = os.path.join(getSetting('workDir'), "scores.csv")

        # TODO: Generate report file?  Is CSV + console output enough?  Perhaps
        # we just hijack stdout in the print calls to write to a file (probably
        # shouldn't be calling `print` anyway).  Or modify the script to use
        # the logging functions FETT uses (probably best)
        scoreTests.main(module, scorer, csvPath)

