import pexpect

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import scoreTests, prettyVulClass

import fett.cwesEvaluation.bufferErrors.vulClassTester
import fett.cwesEvaluation.PPAC.vulClassTester
import fett.cwesEvaluation.resourceManagement.vulClassTester
import fett.cwesEvaluation.informationLeakage.vulClassTester
import fett.cwesEvaluation.numericErrors.vulClassTester
import fett.cwesEvaluation.hardwareSoC.vulClassTester
import fett.cwesEvaluation.injection.vulClassTester
from fett.cwesEvaluation.multitasking.multitasking import hasMultitaskingException, multitaskingRunner, printAndLogMultitaskingTable

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
def checkMultitaskingScores(vulClass, multitaskingScores, instance):
    results = []
    for cwe, score in getSettingDict("cweScores", vulClass).items():
        if hasMultitaskingException(vulClass, ["testsInfo", f"test_{cwe}"]):
            # Test doesn't run in multitasking mode
            continue
        try:
            multitaskingScore = multitaskingScores[cwe]
            results.append((prettyVulClass(vulClass),
                            f"TEST-{cwe}",
                            str(instance),
                            score,
                            multitaskingScore,
                            "PASS" if multitaskingScore == score else "FAIL"))
        except Exception as exc:
            logAndExit("<checkMultitaskingScores> Failed to check "
                       f"multitasking score for CWE <{cwe}>.",
                       exc=exc,
                       exitCode=EXIT.Dev_Bug)
    return results

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

            table = [("Vul. Class", "TEST", "Instance", "Seq. Score", "Multi. Score", "Result")]
            numMultitaskingScores = 0
            for vulClass in getSetting("enabledCwesEvaluations").keys():
                if supportsMultitasking(vulClass):
                    for instance in range(1, getSetting('instancesPerTestPart')+1):
                        printAndLog(f"Scoring instance {instance} of "
                                    f"multitasking {prettyVulClass(vulClass)} "
                                    "tests.")
                        multitaskingScores = scoreTests(
                                vulClass,
                                 os.path.join(logsDir,
                                              vulClass,
                                              f"instance-{instance}"))
                        table += checkMultitaskingScores(vulClass,
                                                         multitaskingScores,
                                                         instance)
                        numMultitaskingScores += len(multitaskingScores)
            printAndLogMultitaskingTable(table)
            numPassed = len([r for r in table[1:] if r[5] == "PASS"])
            percentPassed = (numPassed / numMultitaskingScores) * 100
            printAndLog(f"{numPassed}/{numMultitaskingScores} multitasking "
                        f"tests scored as expected ({percentPassed:.1f}%).")
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

