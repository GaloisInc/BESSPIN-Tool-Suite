import re

from fett.base.utils.misc import *
from fett.cwesEvaluation.compat import testgenTargetCompatibilityLayer
from fett.cwesEvaluation.scoreTests import tabulate_row

# Name of the file to synchronize the test processes on
LOCK_FILE = "multitask.lock"

def hasMultitaskingException(vulClass, envSection):
    exceptions = envSection + ["multitaskingExceptions"]
    return (doesSettingExistDict(vulClass, exceptions) and
            getSetting('osImage') in getSettingDict(vulClass, exceptions))

def printAndLogMultitaskingTable(table):
    widths = [ (len(r[0]), len(r[1]), len(r[2]), len(r[3]), len(r[4]), len(r[5])) for r in table]
    widthCols = [ 2 + max([w[i] for w in widths]) for i in range(6) ]

    fScoresReport = ftOpenFile(os.path.join(getSetting("workDir"), "scoreReport.log"), 'a')

    # Draw first line
    printAndLog(tabulate_row([], widthCols, drawLine=True), tee=fScoresReport)

    for row in table:
        # Draw row
        printAndLog(tabulate_row(row, widthCols), tee=fScoresReport)

        # Draw line
        printAndLog(tabulate_row([], widthCols, drawSeparation=True),
                    tee=fScoresReport)

    fScoresReport.close()

class multitaskingPart:
    """ A multiatskingPart is a single test part to run as a process """
    def __init__(self, logHeader, logFooter, command):
        # Header text to add to log before command output
        self.logHeader = logHeader

        # Footer text to add to log after command output
        self.logFooter = logFooter

        # Command to run
        self.command = command

class multitaskingTest:
    """ A multiatskingTest is a test that may consist of one or multiple parts """
    def __init__(self, vulClass, logHeader, parts):
        # Vulnerability class the test belongs to
        self.vulClass = vulClass

        # Header text to add to log before running the test parts
        self.logHeader = logHeader

        # List of multatskingParts
        self.parts = parts

class multitaskingRunner(testgenTargetCompatibilityLayer):
    def runMultitaskingTests(self, tests, logDir):
        # Count number of processes to spawn
        numProcs = 0
        for test in tests:
            numProcs += len(test.parts)
        numInstances = getSetting('instancesPerTestPart')
        numProcs *= numInstances

        # Create the multitasking lock file
        self.typCommand(f"touch {LOCK_FILE}")

        printAndLog(f"Running {numProcs} processes in parallel.")
        unredirectedOutput = ""
        iLog = 0
        logDirs = {}
        for instance in range(numInstances):
            for test in tests:
                for part in test.parts:
                    command = (f"./multitask.riscv {numProcs} {part.command} "
                               f"{self.redirectOp} multitask-{iLog}.log &")
                    _, textBack, wasTimeout, _ = self.runCommand(command)
                    # Strip " ^H" from output
                    textBack = textBack.replace(' \x08', "")
                    if wasTimeout or command not in textBack:
                        # In addition to checking for timeouts, the tool must
                        # also check that the command was properly executed.
                        # When the target is overloaded it sometimes drops
                        # characters sent over pexpect.  These dropped
                        # characters are easy to detect as they are also absent
                        # from the command text that the shell prints out.
                        logAndExit("<multitasking>  Cannot spawn additional "
                                   "processes: target has become unresponsive.  "
                                   "Reduce the number of enabled tests and/or "
                                   "reduce <instancesPerTestPart>.",
                                   exitCode=EXIT.Run)
                    unredirectedOutput += textBack
                    iLog += 1
                if test.vulClass not in logDirs:
                    logDirs[test.vulClass] = os.path.join(logDir, test.vulClass)
                    mkdir(logDirs[test.vulClass])
                    for instance in range(1, numInstances+1):
                        mkdir(os.path.join(logDirs[test.vulClass],
                                           f"instance-{instance}"))


        # Remove multitasking lock file and wait for all running jobs to finish
        _, textBack, wasTimeout, _ = self.runCommand(f"rm {LOCK_FILE} && "
                                                     f"wait {self.redirectOp} wait.log",
                                                     exitOnError=False,
                                                     timeout=max(60, 6*numProcs))
        unredirectedOutput += textBack
        if wasTimeout:
            # Kill any running backgrounded jobs
            warnAndLog("<wait> timed out.  Multitasking scores may be incomplete.")
            self.typCommand("pkill -9 multitask.riscv")


        # Wait output includes unredirected output in case some tests ran to
        # completion before calling `wait`
        waitOutput = unredirectedOutput + self.typCommand("cat wait.log")

        # Extract logs
        iLog = 0
        for instance in range(1, numInstances+1):
            for test in tests:
                outLog = test.logHeader
                for part in test.parts:
                    outLog += part.logHeader
                    multitaskLog = f'multitask-{iLog}.log'
                    testOutput = self.typCommand(f"cat {multitaskLog}")
                    outLog += testOutput
                    outLog += "\n"

                    # Look for PID
                    pid_match = re.search(r'<PID ([0-9]+)>', testOutput)
                    if pid_match is None:
                        # This should never happen.  Mark test invalid and
                        # continue.
                        outLog += "\n<INVALID>\nPID extraction failed.\n"
                        outLog += part.logFooter
                        iLog += 1
                        continue
                    pid = pid_match.group(1)

                    # Extract output from `wait`.
                    for line in waitOutput.splitlines():
                        if multitaskLog in line:
                            # Look for multitaskLog in each line as it is a
                            # part of the command string that uniquely
                            # identifies which instance a given test run
                            # belongs to.
                            outLog += line
                            outLog += "\n"

                    if isEqSetting('osImage', 'debian'):
                        # Extract kmesg output
                        for line in unredirectedOutput.splitlines():
                            if f"[{pid}]" in line or f" {pid} " in line:
                                # Relevant kmesg lines always have PID in brackets,
                                # or surrounded by spaces on both sides.  Can't
                                # just search for `pid` without these characters on
                                # eiether side because the number may be
                                # coincidentally present in timestamps, memory
                                # values, etc.
                                outLog += line
                                outLog += "\n"
                    outLog += part.logFooter
                    iLog += 1
                try:
                    testName = test.parts[0].command.split('.')[1][1:]
                except Exception as exc:
                    logAndExit("<multitasking> Failed to extract test name.",
                               exc=exc,
                               exitCode=EXIT.Dev_Bug)
                fileName = os.path.join(logDirs[test.vulClass],
                                        f'instance-{instance}',
                                        f'{testName}.log')
                logFile = ftOpenFile(fileName, 'w')
                logFile.write(outLog)
                logFile.close()
