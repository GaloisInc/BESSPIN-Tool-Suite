import pexpect

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import scoreTests, prettyVulClass, tabulate

import fett.cwesEvaluation.bufferErrors.vulClassTester
import fett.cwesEvaluation.PPAC.vulClassTester
import fett.cwesEvaluation.resourceManagement.vulClassTester
import fett.cwesEvaluation.informationLeakage.vulClassTester
import fett.cwesEvaluation.numericErrors.vulClassTester
import fett.cwesEvaluation.hardwareSoC.vulClassTester
import fett.cwesEvaluation.injection.vulClassTester
from fett.cwesEvaluation.multitasking.multitasking import hasMultitaskingException, multitaskingRunner, logMultitaskingTable

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
def checkMultitaskingScores(vulClass, multitaskingScores, instance, multitaskingPasses):
    results = []
    for cwe, score in getSettingDict("cweScores", vulClass).items():
        if hasMultitaskingException(vulClass, ["testsInfo", f"test_{cwe}"]):
            # Test doesn't run in multitasking mode
            continue
        try:
            multitaskingScore = multitaskingScores[cwe]
            if vulClass in ['bufferErrors', 'informationLeakage']:
                testName = f"CWE-{cwe}"
            else:
                testName = f"TEST-{cwe}"
            if multitaskingScore == score:
                multitaskingPasses[testName] = multitaskingPasses.get(testName, 0) + 1
                scoreText = "PASS"
            else:
                if testName not in multitaskingPasses:
                    # Record that the test ran but did not pass.
                    multitaskingPasses[testName] = 0
                scoreText = "FAIL"
            results.append((prettyVulClass(vulClass),
                            testName,
                            str(instance),
                            score,
                            multitaskingScore,
                            scoreText))
        except Exception as exc:
            logAndExit("<checkMultitaskingScores> Failed to check "
                       f"multitasking score for CWE <{cwe}>.",
                       exc=exc,
                       exitCode=EXIT.Dev_Bug)
    return results

@decorate.debugWrap
def appendMultitaskingColumn(vulClass, rows, multitaskingPasses):
    for row in rows:
        testNameParts = row[0].split("-")
        testName = f"test_{'_'.join(testNameParts[1:])}"
        if (supportsMultitasking(vulClass) and
            not hasMultitaskingException(vulClass, ["testsInfo", testName])):
            try:
                percentPassed = (multitaskingPasses[row[0]] / getSetting("instancesPerTestPart")) * 100
            except Exception as exc:
                logAndExit("<appendMultitaskingColumn> Failed to find "
                           f"multitasking score for <{row[0]}>.",
                           exc=exc,
                           exitCode=EXIT.Dev_Bug)
            row.append(f"{percentPassed:.1f}%")
        else:
            row.append("N/A")

@decorate.debugWrap
def printTable(vulClass, table):
    rows = tabulate(table,
                    vulClass,
                    prettyVulClass(vulClass),
                    getSetting("runningMultitaskingTests"))
    reportFilePath = os.path.join(getSetting("workDir"), "scoreReport.log")
    fScoresReport = ftOpenFile(reportFilePath, 'a')
    for row in rows:
        printAndLog(row, tee=fScoresReport)
    fScoresReport.close()

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
        sequentialTables = {}
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
            _, table = scoreTests(vulClass, logsDir, prettyVulClass(vulClass), doPrint=False)
            sequentialTables[vulClass] = table

        if multitaskingTests:
            setSetting("runningMultitaskingTests", True)
            logsDir = os.path.join(baseLogDir, "multitasking")
            mkdir(logsDir)
            multitaskingRunner(target).runMultitaskingTests(multitaskingTests, logsDir)

            table = [("Vul. Class", "TEST", "Instance", "Seq. Score", "Multi. Score", "Result")]
            numMultitaskingScores = 0
            multitaskingPasses = {}
            for vulClass in getSetting("enabledCwesEvaluations").keys():
                if supportsMultitasking(vulClass):
                    for instance in range(1, getSetting('instancesPerTestPart')+1):
                        multitaskingScores, _ = scoreTests(
                                vulClass,
                                os.path.join(logsDir,
                                             vulClass,
                                             f"instance-{instance}"),
                                f'{prettyVulClass(vulClass)} multitasking '
                                f'instance {instance}',
                                doPrint=False,
                                reportFileName="multitaskingScoreReport.log")
                        table += checkMultitaskingScores(vulClass,
                                                         multitaskingScores,
                                                         instance,
                                                         multitaskingPasses)
                        numMultitaskingScores += len(multitaskingScores)
            logMultitaskingTable(table)

            for vulClass, table in sequentialTables.items():
                appendMultitaskingColumn(vulClass, table, multitaskingPasses)
                printTable(vulClass, table)

            numPassed = sum(multitaskingPasses.values())
            percentPassed = (numPassed / numMultitaskingScores) * 100
            printAndLog(f"{numPassed}/{numMultitaskingScores} multitasking "
                        f"tests scored as expected ({percentPassed:.1f}%).")
            setSetting("runningMultitaskingTests", False)
        else:
            for vulClass, table in sequentialTables.items():
                printTable(vulClass, table)

    else:
        target.terminateAndExit(f"<runTests> not implemented for <{getSetting('osImage')}>",
                   exitCode=EXIT.Implementation)

@decorate.debugWrap
def isTestEnabled(vulClass, testName):
    if (getSettingDict(vulClass,'runAllTests')):
        return True
    else:
        return getSettingDict(vulClass,['enabledTests',testName])

