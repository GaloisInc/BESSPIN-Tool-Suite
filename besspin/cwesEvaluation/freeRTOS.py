import glob
import os

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.scoreTests import scoreTests, prettyVulClass
from besspin.target import awsf1, vcu118
import besspin.target.launch

@decorate.debugWrap
@decorate.timeWrap
def runFreeRTOSCwesEvaluation():
    """
    Run the CWEs evaluation on FreeRTOS.  This function will run all enabled
    tests and score the results.

    SIDE-EFFECTS:
    -------------
        - Compiles CWE tests.
        - Executes CWE test binaries on <target>.
        - For each enabled test, sets ${isThereAReasonToBoot} based on whether
          the test's vulnerability class has ${useSelfAssessment} enabled.
        - For each test part, sets ${currentTest} to a tuple of type
          (String, String, Int, String).  In order, these elements are:
            0. The test's C file.
            1. The vulnerability class the test belongs to.
            2. The part of the test to execute.
            3. The log file to write test output to.
        - If running on <awsf1> or <vcu118>, flashes the FPGA between each test
          part run.
        - Boots FreeRTOS on the target for each test part run.
        - If ${useCustomScoring} is enabled or the target has GDB access,
          this function reads GDB output and appends it to the test logs.
        - Writes test output logs and score CSVs to ${logDir}.
        - Prints score tables to terminal.
        - Writes score report to <${workDir}/scoreReport.log>.
        - Writes multitasking score report to
          <${workDir}/multitaskingScoreReport.log>.
    """
    printAndLog (f"Launching BESSPIN <{getSetting('mode')} mode>...")
    baseLogDir = os.path.join(getSetting('workDir'), 'cwesEvaluationLogs')
    mkdir(baseLogDir, addToSettings="cwesEvaluationLogs")
    isFiresimPrepared = False #Preparation in target.launch.prepareEnv is initially skipped
    if (isEqSetting('target','vcu118') and (not isEqSetting('vcu118Mode','nonPersistent'))):
        logAndExit(f"Using the vcu118 mode <{getSetting('vcu118Mode')}> with FreeRTOS in "
            "<evaluateSecurityTests> mode is not supported.",exitCode=EXIT.Configuration)

    for vulClass, tests in getSetting("enabledCwesEvaluations").items():
        logsDir = os.path.join(baseLogDir, vulClass)
        testsDir = os.path.join(getSetting('buildDir'), vulClass)
        mkdir(logsDir)

        for test in tests:
            testName = test.split('.')[0]
            cTest = f"{testName}.c"
            logFile = ftOpenFile(os.path.join(logsDir, f"{testName}.log"), 'w')

            setSetting('isThereAReasonToBoot', not isEnabledDict(vulClass,'useSelfAssessment'))
            if (not isEnabled('isThereAReasonToBoot')):
                setSetting("currentTest", (cTest, vulClass, 0, logFile))
                besspin.target.launch.launchBesspin()
                logFile.close()
                continue #no need for the rest
            
            partsMatch = matchExprInLines(r".*NUM_OF_TEST_PARTS ([0-9]+).*",
                                          ftReadLines(os.path.join(testsDir,cTest)))
            parts = int(partsMatch.group(1)) if partsMatch else 1
            logFile.write(f"<NUMPARTS={parts}>\n")
            
            
            for part in range(1, parts+1):
                printAndLog(f"Running {vulClass}/{testName} part {part}")
                setSetting("currentTest", (cTest, vulClass, part, logFile))

                if isEqSetting('target', 'awsf1'):
                    if isEqSetting('pvAWS', 'firesim'):
                        if (not isFiresimPrepared): 
                            awsf1.prepareFiresim()
                            awsf1.removeKernelModules()
                            awsf1.installKernelModules()
                            awsf1.configTapAdaptor()
                            isFiresimPrepared = True
                        awsf1.programAFI(doPrint=False)
                    else:
                        logAndExit("<runFreeRTOSCwesEvaluation> is not "
                                   "implemented for "
                                   f"<AWS:{getSetting('pvAWS')}>.",
                                   exitCode=EXIT.Implementation)
                elif (isEqSetting('target','vcu118')):
                    vcu118.programBitfile(doPrint=False)
                elif not isEqSetting('target', 'qemu'):
                    logAndExit("<runFreeRTOSCwesEvaluation> is not "
                               f"implemented for <{getSetting('target')}>",
                               exitCode=EXIT.Implementation)
                
                target = besspin.target.launch.launchBesspin()
                target.shutdown()

                #Log the GDB log
                if (isEnabled('useCustomScoring') and target.hasGdbAccess()):
                    logFile.write("\n\n~~~GDB LOGGING~~~\n")
                    gdbLines = '\n'.join(target.gdbOutLines)
                    logFile.write(gdbLines[gdbLines.find("Continuing."):]) # only the useful output
                    logFile.write("\n~~~~~~~~~~~~~~~~~\n")

                if (target.hasGdbAccess()):
                    logging.debug(f"\n~~~GDB LOGGING -- {testName}~~~\n")
                    logging.debug('\n'.join(ftReadLines(target.fGdbOut.name))) # The whole thing for debug
                    logging.debug("\n~~~~~~~~~~~~~~~~~")

            logFile.close()
        # Score the tests
        scoreTests(vulClass, logsDir, prettyVulClass(vulClass))


