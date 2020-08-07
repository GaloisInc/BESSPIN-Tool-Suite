from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import scoreTests

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
    if isEnabled('isUnix') and target.isCurrentUserRoot:
        # TODO: Test that this didn't break anything
        # Tests expect to started as normal user
        target.switchUser()
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

    csvPath = os.path.join(testLogDir, "scores.csv")
    scoreTests(module, csvPath, testLogDir)

@decorate.debugWrap
@decorate.timeWrap
def runTests(target, sendFiles=False, timeout=30): #executes the app
    if isEqSetting('osImage', 'FreeRTOS'):
        # Exctract test output
        # TODO: Play around with the timeout.  Some tests timeout at 15
        # seconds, and even 60 seconds.  Set low for now to enable faster
        # debugging.
        output = target.expectFromTarget(">>>End of Fett<<<",
                                         None,
                                         shutdownOnError=False,
                                         timeout=getSetting('FreeRTOStimeout'))

        test, vulClass, _, logFile = getSetting("currentTest")

        if output[1]:
            logFile.write(target.readFromTarget())
            logFile.write("\n<TIMEOUT>\n")
            warnAndLog(f"{test} timed out.  Skipping.",doPrint=False)
            return
        else:
            logFile.write(output[0])

    elif getSetting('osImage') in ['debian', 'FreeBSD']:
        # Create directory for logs
        baseLogDir = os.path.join(getSetting('workDir'), 'cwesEvaluationLogs')
        mkdir(baseLogDir, addToSettings="cwesEvaluationLogs")

        if not sendFiles:
            target.shutdownAndExit("<runApp>: sendFiles must be True for CWEs "
                                   "evaluation on unix hosts",
                                   exitCode = EXIT.Dev_Bug)
        target.sendTar(timeout=timeout)

        # Copy binaries to non-root user's home as well
        wasRoot = target.isCurrentUserRoot
        if not target.isCurrentUserRoot:
            target.switchUser()
        target.runCommand(f"cp *.riscv /home/{target.userName}")
        target.runCommand(f"chown {target.userName}:{target.userName} "
                          f"/home/{target.userName}/*.riscv")
        target.switchUser()

        # Batch tests by vulnerability class
        for vulClass, tests in getSetting("enabledCwesEvaluations").items():
            logDir = os.path.join(baseLogDir, vulClass)
            mkdir(logDir)
            for test in tests:
                executeTest(target, vulClass, test, logDir)

            score(logDir, vulClass)

        if target.isCurrentUserRoot != wasRoot:
            target.switchUser()
    else:
        logAndExit(f"<runTests> not implemented for <{getSetting('osImage')}>",
                   exitCode=EXIT.Implementation)

@decorate.debugWrap
def isTestEnabled (vulClass, cTestName):
    if (getSettingDict(vulClass,'runAllTests')):
        return True
    else:
        return getSettingDict(vulClass,['configCWEs',os.path.splitext(cTestName)[0]])
