import pexpect

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import scoreTests

import fett.cwesEvaluation.bufferErrors.vulClassTester
import fett.cwesEvaluation.PPAC.vulClassTester
import fett.cwesEvaluation.resourceManagement.vulClassTester
import fett.cwesEvaluation.informationLeakage.vulClassTester
import fett.cwesEvaluation.numericErrors.vulClassTester
import fett.cwesEvaluation.hardwareSoC.vulClassTester
import fett.cwesEvaluation.injection.vulClassTester
from fett.cwesEvaluation.multitasking.multitasking import multitaskingRunner

cweTests = {
    "bufferErrors" :
        fett.cwesEvaluation.bufferErrors.vulClassTester.vulClassTester,
    "PPAC" :
        fett.cwesEvaluation.PPAC.vulClassTester.vulClassTester,
    "resourceManagement" :
        fett.cwesEvaluation.resourceManagement.vulClassTester.vulClassTester,
    "informationLeakage" :
        fett.cwesEvaluation.informationLeakage.vulClassTester.vulClassTester,
    "numericErrors" :
        fett.cwesEvaluation.numericErrors.vulClassTester.vulClassTester,
    "hardwareSoC" :
        fett.cwesEvaluation.hardwareSoC.vulClassTester.vulClassTester,
    "injection" :
        fett.cwesEvaluation.injection.vulClassTester.vulClassTester,
}

@decorate.debugWrap
@decorate.timeWrap
def executeTest(target, vulClass, binTest, logDir):
    testName = binTest.split('.')[0]
    printAndLog(f"Executing {testName}...", doPrint=(not isEnabledDict(vulClass,'useSelfAssessment')))
    outLog = cweTests[vulClass](target).executeTest(binTest)
    logFileName = os.path.join(logDir, f'{testName}.log')
    logFile = ftOpenFile(logFileName, 'w')
    logFile.write(outLog)
    logFile.close()

@decorate.debugWrap
@decorate.timeWrap
def checkMultitaskingScores(sequentialScores, multitaskingScores):
    mismatches = []
    for cwe, score in sequentialScores.items():
        try:
            if multitaskingScores[cwe] != score:
                mismatches.append(cwe)
        except KeyError:
            # Not all tests run in multitasking mode
            pass
    return mismatches

@decorate.debugWrap
@decorate.timeWrap
def supportsMultitasking(vulClass):
    return (isEnabled('runUnixMultitaskingTests') and
            doesSettingExistDict(vulClass, 'supportsMultitasking') and
            isEnabledDict(vulClass, 'supportsMultitasking'))

def runTests(target, sendFiles=False, timeout=30): #executes the app
    if isEqSetting('osImage', 'FreeRTOS'):
        test, vulClass, _, logFile = getSetting("currentTest")
        if (isEnabledDict(vulClass,'useSelfAssessment')):
            outLog = cweTests[vulClass](target).executeTest(test.replace('.c','.riscv'))
        else:
            # Extract test output
            textBack, wasTimeout, idxReturn = target.expectFromTarget(
                    [">>>End of Fett<<<", pexpect.EOF],
                    "runCweTest",
                    exitOnError=False,
                    timeout=getSetting('FreeRTOStimeout'),
                    suppressWarnings=True)

            if idxReturn == 1:
                if isEqSetting('target', 'qemu'):
                    # No ">>> End Of Testgen <<<", but qemu aborted without a
                    # timeout
                    logFile.write(target.readFromTarget())
                    logFile.write("\n<QEMU ABORTED>\n")
                    return
                else:
                    target.terminateAndExit("<runTests> Unexpected EOF during "
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

        if sendFiles:
            target.sendTar(timeout=timeout)

        # Batch tests by vulnerability class
        multitaskingTests = []
        for vulClass, tests in getSetting("enabledCwesEvaluations").items():
            logsDir = os.path.join(baseLogDir, vulClass)
            mkdir(logsDir)
            for test in tests:
                executeTest(target, vulClass, test, logsDir)
                if (supportsMultitasking(vulClass)):
                    multitaskingTest = cweTests[vulClass](target).testToMultitaskingObj(test)
                    if multitaskingTest:
                        multitaskingTests.append(multitaskingTest)
            scoreTests(vulClass, logsDir)

        if multitaskingTests:
            setSetting("runningMultitaskingTests", True)
            logsDir = os.path.join(baseLogDir, "multitasking")
            mkdir(logsDir)
            multitaskingRunner(target).runMultitaskingTests(multitaskingTests, logsDir)

            mismatches = []
            numMultitaskingScores = 0
            for vulClass in getSetting("enabledCwesEvaluations").keys():
                if supportsMultitasking(vulClass):
                    multitaskingScores = scoreTests(vulClass,
                                                    os.path.join(logsDir,
                                                                 vulClass))
                    mismatches += checkMultitaskingScores(
                            getSettingDict('cweScores', vulClass),
                            multitaskingScores)
                    numMultitaskingScores += len(multitaskingScores)
            numPassed = numMultitaskingScores - len(mismatches)
            percentPassed = (numPassed / numMultitaskingScores) * 100
            printAndLog(f"{numPassed}/{numMultitaskingScores} multitasking "
                        f"tests scored as expected ({percentPassed:.1f}%).")
            if mismatches:
                printAndLog(f"The following tests scored differently in "
                            "multitasking and sequential execution: "
                            f"{', '.join(mismatches)}.")
            setSetting("runningMultitaskingTests", False)

    else:
        target.terminateAndExit(f"<runTests> not implemented for <{getSetting('osImage')}>",
                   exitCode=EXIT.Implementation)

@decorate.debugWrap
def isTestEnabled(vulClass, testName):
    if (getSettingDict(vulClass,'runAllTests')):
        return True
    else:
        return getSettingDict(vulClass,['enabledTests',testName])

