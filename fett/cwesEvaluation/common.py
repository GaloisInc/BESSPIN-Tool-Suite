from fett.base.utils.misc import *
import fett.cwesEvaluation.scoreTests as scoreTests

import fett.cwesEvaluation.tests.resourceManagement.scripts.vulClassTester
import fett.cwesEvaluation.tests.resourceManagement.scripts.cweScores
import fett.cwesEvaluation.tests.numericErrors.scripts.vulClassTester
import fett.cwesEvaluation.tests.numericErrors.scripts.cweScores

cweTests = {
    "resourceManagement" :
        fett.cwesEvaluation.tests.resourceManagement.scripts.vulClassTester.vulClassTester,
    "numericErrors" :
        fett.cwesEvaluation.tests.numericErrors.scripts.vulClassTester.vulClassTester
}

cweScores = {
    "resourceManagement" :
        fett.cwesEvaluation.tests.resourceManagement.scripts.cweScores,
    "numericErrors" :
        fett.cwesEvaluation.tests.numericErrors.scripts.cweScores
}

@decorate.debugWrap
@decorate.timeWrap
def executeTest(target, vulClass, binTest, logDir):
    testName = binTest.split('.')[0]
    printAndLog(f"Executing {testName}...")
    outLog = cweTests[vulClass](target).executeTest(binTest)
    logFile = os.path.join(logDir, f'{testName}.log')
    with open(logFile, 'w') as f:
        f.write(outLog)

@decorate.debugWrap
@decorate.timeWrap
def score(testLogDir, vulClass):
    module = cweScores[vulClass]

    # TODO: Allow custom scoring
    scorer = scoreTests.customScorerObj(False, None)

    # TODO: Make this configurable?
    csvPath = os.path.join(testLogDir, "scores.csv")

    scoreTests.main(module, scorer, csvPath, testLogDir)


@decorate.debugWrap
@decorate.timeWrap
def runTests(target, sendFiles=False, timeout=30): #executes the app
    if not sendFiles:
        target.shutdownAndExit("<runApp>: sendFiles must be True for CWEs "
                             "evaluation",
                             exitCode = EXIT.Configuration)
    target.sendTar(timeout=timeout)

    # Create directory for logs
    baseLogDir = os.path.join(getSetting('workDir'), 'cwesEvaluationLogs')
    mkdir(baseLogDir)

    # Batch tests by vulnerability class
    for vulClass, tests in getSetting("enabledCwesEvaluations").items():
        # TODO: Correct endsWith
        logDir = os.path.join(baseLogDir, vulClass)
        mkdir(logDir)
        for test in tests:
            executeTest(target, vulClass, test, logDir)

        score(logDir, vulClass)

