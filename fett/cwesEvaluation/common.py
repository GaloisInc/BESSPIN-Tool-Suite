from fett.base.utils.misc import *
import fett.cwesEvaluation.scoreTests as scoreTests

import fett.cwesEvaluation.tests.bufferErrors.vulClassTester
import fett.cwesEvaluation.tests.bufferErrors.cweScores
import fett.cwesEvaluation.tests.PPAC.vulClassTester
import fett.cwesEvaluation.tests.PPAC.cweScores
import fett.cwesEvaluation.tests.resourceManagement.vulClassTester
import fett.cwesEvaluation.tests.resourceManagement.cweScores
import fett.cwesEvaluation.tests.numericErrors.vulClassTester
import fett.cwesEvaluation.tests.numericErrors.cweScores

cweTests = {
    "bufferErrors" :
        fett.cwesEvaluation.tests.bufferErrors.vulClassTester.vulClassTester,
    "PPAC" :
        fett.cwesEvaluation.tests.PPAC.vulClassTester.vulClassTester,
    "resourceManagement" :
        fett.cwesEvaluation.tests.resourceManagement.vulClassTester.vulClassTester,
    "numericErrors" :
        fett.cwesEvaluation.tests.numericErrors.vulClassTester.vulClassTester
}

cweScores = {
    "bufferErrors" :
        fett.cwesEvaluation.tests.bufferErrors.cweScores,
    "PPAC" :
        fett.cwesEvaluation.tests.PPAC.cweScores,
    "resourceManagement" :
        fett.cwesEvaluation.tests.resourceManagement.cweScores,
    "numericErrors" :
        fett.cwesEvaluation.tests.numericErrors.cweScores
}

@decorate.debugWrap
@decorate.timeWrap
def executeTest(target, vulClass, binTest, logDir):
    testName = binTest.split('.')[0]
    printAndLog(f"Executing {testName}...")
    outLog = cweTests[vulClass](target).executeTest(binTest)
    logFileName = os.path.join(logDir, f'{testName}.log')
    logFile = ftOpenFile(logFileName, 'w')
    logFile.write(outLog)
    logFile.close()

@decorate.debugWrap
@decorate.timeWrap
def score(testLogDir, vulClass):
    module = cweScores[vulClass]

    # TODO: Allow custom scoring
    scorer = scoreTests.customScorerObj(False, None)
    csvPath = os.path.join(testLogDir, "scores.csv")
    scoreTests.scoreTests(module, scorer, csvPath, testLogDir)

@decorate.debugWrap
@decorate.timeWrap
def runTests(target, sendFiles=False, timeout=30): #executes the app
    # Create directory for logs
    baseLogDir = os.path.join(getSetting('workDir'), 'cwesEvaluationLogs')
    mkdir(baseLogDir,
          addToSettings="cwesEvaluationLogs",
          exitIfExists=(not isEqSetting('osImage', 'FreeRTOS')))

    if isEqSetting('osImage', 'FreeRTOS'):
        # Exctract test output
        # TODO: Play around with the timeout.  Some tests timeout at 15
        # seconds, and even 60 seconds.  Set low for now to enable faster
        # debugging.
        output = target.expectFromTarget(">>>End of Fett<<<",
                                         None,
                                         shutdownOnError=False,
                                         timeout=15)

        test, vulClass, _ = getSetting("currentTest")
        if output[1]:
            warnAndLog(f"{test} timed out.  Skipping.")
            return

        # Save in correct log file
        logDir = os.path.join(baseLogDir, vulClass)
        mkdir(logDir, exitIfExists=False)
        testName = test.split('.')[0]
        logFile = ftOpenFile(os.path.join(logDir, f"{testName}.log"), 'a')
        logFile.write(output[0])
        logFile.close()

    elif getSetting('osImage') in ['debian', 'FreeBSD']:
        if not sendFiles:
            target.shutdownAndExit("<runApp>: sendFiles must be True for CWEs "
                                   "evaluation on unix hosts",
                                   exitCode = EXIT.Configuration)
        target.sendTar(timeout=timeout)

        # Batch tests by vulnerability class
        for vulClass, tests in getSetting("enabledCwesEvaluations").items():
            logDir = os.path.join(baseLogDir, vulClass)
            mkdir(logDir)
            for test in tests:
                executeTest(target, vulClass, test, logDir)

            score(logDir, vulClass)
    else:
        logAndExit(f"<runTests> not implemented for <{getSetting('osImage')}>",
                   exitCode=EXIT.Implementation)

@decorate.debugWrap
def isTestEnabled (vulClass, cTestName):
    if (getSettingDict(vulClass,'runAllTests')):
        return True
    else:
        return getSettingDict(vulClass,['configCWEs',os.path.splitext(cTestName)[0]])
