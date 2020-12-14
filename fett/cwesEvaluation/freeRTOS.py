import glob
import os

from fett.base.utils.misc import *
from fett.cwesEvaluation.common import score
from fett.target import awsf1, vcu118
import fett.target.launch

@decorate.debugWrap
@decorate.timeWrap
def runFreeRTOSCwesEvaluation():
    printAndLog (f"Launching FETT <{getSetting('mode')} mode>...")
    baseLogDir = os.path.join(getSetting('workDir'), 'cwesEvaluationLogs')
    mkdir(baseLogDir, addToSettings="cwesEvaluationLogs")
    isFiresimPrepared = False #Preparation in target.launch.prepareEnv is initially skipped

    for vulClass, tests in getSetting("enabledCwesEvaluations").items():
        logsDir = os.path.join(baseLogDir, vulClass)
        testsDir = os.path.join(getSetting('buildDir'), vulClass)
        mkdir(logsDir)

        for test in tests:
            testName = test.split('.')[0]
            cTest = f"{testName}.c"
            logFile = ftOpenFile(os.path.join(logsDir, f"{testName}.log"), 'w')

            setSetting('isThereAReasonToBoot', (vulClass not in ['PPAC', 'hardwareSoC']))
            if (not isEnabled('isThereAReasonToBoot')):
                setSetting("currentTest", (cTest, vulClass, 0, logFile))
                fett.target.launch.launchFett()
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
                
                target = fett.target.launch.launchFett()
                target.shutdown()

                #Log the GDB log
                if (isEnabled('useCustomScoring')):
                    logFile.write("\n\n~~~GDB LOGGING~~~\n")
                    gdbLines = '\n'.join(target.gdbOutLines)
                    logFile.write(gdbLines[gdbLines.find("Continuing."):]) # only the useful output
                    logFile.write("\n~~~~~~~~~~~~~~~~~\n")

                if not isEqSetting('target', 'qemu'):
                    logging.debug(f"\n~~~GDB LOGGING -- {testName}~~~\n")
                    logging.debug('\n'.join(ftReadLines(target.fGdbOut.name))) # The whole thing for debug
                    logging.debug("\n~~~~~~~~~~~~~~~~~")

            logFile.close()
        # Score the tests
        score(os.path.join(getSetting("cwesEvaluationLogs"), vulClass),
              vulClass)


