import pexpect

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import scoreTests

import fett.cwesEvaluation.tests.bufferErrors.vulClassTester
import fett.cwesEvaluation.tests.bufferErrors.cweScores
import fett.cwesEvaluation.tests.PPAC.vulClassTester
import fett.cwesEvaluation.tests.PPAC.cweScores
import fett.cwesEvaluation.tests.resourceManagement.vulClassTester
import fett.cwesEvaluation.tests.resourceManagement.cweScores
import fett.cwesEvaluation.tests.informationLeakage.vulClassTester
import fett.cwesEvaluation.tests.informationLeakage.cweScores
import fett.cwesEvaluation.tests.numericErrors.vulClassTester
import fett.cwesEvaluation.tests.numericErrors.cweScores

cweTests = {
    "bufferErrors" :
        fett.cwesEvaluation.tests.bufferErrors.vulClassTester.vulClassTester,
    "PPAC" :
        fett.cwesEvaluation.tests.PPAC.vulClassTester.vulClassTester,
    "resourceManagement" :
        fett.cwesEvaluation.tests.resourceManagement.vulClassTester.vulClassTester,
    "informationLeakage" :
        fett.cwesEvaluation.tests.informationLeakage.vulClassTester.vulClassTester,
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
    "informationLeakage" :
        fett.cwesEvaluation.tests.informationLeakage.cweScores,
    "numericErrors" :
        fett.cwesEvaluation.tests.numericErrors.cweScores
}

@decorate.debugWrap
@decorate.timeWrap
def executeTest(target, vulClass, binTest, logDir):
    if isEnabled('isUnix') and target.isCurrentUserRoot:
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
        test, vulClass, _, logFile = getSetting("currentTest")
        if (vulClass=='PPAC'):
            outLog = cweTests[vulClass](target).executeTest(test.replace('.c','.riscv'))
        else:
            # Exctract test output
            textBack, wasTimeout, idxReturn = target.expectFromTarget(
                    [">>>End of Fett<<<", pexpect.EOF],
                    None,
                    shutdownOnError=False,
                    timeout=getSetting('FreeRTOStimeout'))

            if idxReturn == 1:
                if isEqSetting('target', 'qemu'):
                    # No ">>> End Of Testgen <<<", but qemu aborted without a
                    # timeout
                    logFile.write(target.readFromTarget())
                    logFile.write("\n<QEMU ABORTED>\n")
                    return
                else:
                    target.shutdownAndExit("<runTests> Unexpected EOF during "
                                           "test run.",
                                           exitCode=EXIT.Dev_Bug)
            if wasTimeout:
                logFile.write(target.readFromTarget())
                logFile.write("\n<TIMEOUT>\n")
                warnAndLog(f"{test} timed out.  Skipping.",doPrint=False)
                return
            outLog = textBack
        
        logFile.write(outLog)

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

        # Move any pam or limit files
        target.runCommand(f"chown root:{target.rootGroup} pam*")
        target.runCommand("mv pam* /etc/pam.d/")
        target.runCommand(f"chown root:{target.rootGroup} limits*")
        target.runCommand("mv limits* /etc/security/")
        if (isEqSetting('osImage','FreeBSD')): #need to be only writable by root
            target.runCommand("chmod 644 /etc/pam.d/pam* /etc/security/limits*")

        # Become a normal user
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
        target.shutdownAndExit(f"<runTests> not implemented for <{getSetting('osImage')}>",
                   exitCode=EXIT.Implementation)

@decorate.debugWrap
def isTestEnabled (vulClass, cTestName):
    if (getSettingDict(vulClass,'runAllTests')):
        return True
    else:
        return getSettingDict(vulClass,['configCWEs',os.path.splitext(cTestName)[0]])
