import glob
import os

from fett.base.utils.misc import *
from fett.cwesEvaluation.common import score
from fett.target import aws
import fett.target.launch

@decorate.debugWrap
@decorate.timeWrap
def collectTests():
    testsDir = os.path.join(getSetting("repoDir"),
                            "fett",
                            "cwesEvaluation",
                            "tests")
    tests = {}
    for vulClass in getSetting("vulClasses"):
        testDir = os.path.join(testsDir, vulClass, "sources")
        for test in glob.glob(os.path.join(testDir, "test_*.c")):
            # Extract number of parts in test
            partsMatch = matchExprInLines(r".*NUM_OF_TEST_PARTS ([0-9]+).*",
                                          ftReadLines(test))
            testInfo = (os.path.basename(test),
                        int(partsMatch.group(1)) if partsMatch else 1)
            try:
                tests[vulClass].append(testInfo)
            except KeyError:
                tests[vulClass] = [testInfo]
    return tests

@decorate.debugWrap
@decorate.timeWrap
def runFreeRTOSCwesEvaluation():
    started = False
    for vulClass, tests in collectTests().items():
        for test, parts in tests:
            for part in range(1, parts+1):
                printAndLog(f"Running {vulClass}/{test} part {part}")
                setSetting("currentTest", (test, vulClass, part))
                if started:
                    if isEqSetting('target', 'aws'):
                        if isEqSetting('pvAWS', 'firesim'):
                            # TODO: Is there a way to avoid reflashing the
                            # FPGA?
                            aws.programAFI()
                        else:
                            logAndExit("<runFreeRTOSCwesEvaluation> is not "
                                       "implemented for "
                                       f"<AWS:{getSetting('pvAWS')}>.",
                                       exitCode=EXIT.Implementation)
                    else:
                        logAndExit("<runFreeRTOSCwesEvaluation> is not "
                                   f"implemented for <{getSetting('target')}>",
                                   exitCode=EXIT.Implementation)
                    target = fett.target.launch.launchFett()
                else:
                    target = fett.target.launch.startFett()
                    started = True

                target.shutdown()

        # Score the tests
        score(os.path.join(getSetting("cwesEvaluationLogs"), vulClass),
              vulClass)


