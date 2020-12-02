from pathlib import Path
import os
import json

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore

QEMU_FPGA_LOOKFOR  = [
            # (indicated result, line contain)
            # Order is significant here
            # Four possibilities in the next two dimensions:
            # If printed both "TEST COMPLETED" and "SEGMENTATION FAULT" (in debian) --> consider it a trap.
            # If timed out, but idle breakpoint (in FreeRTOS) --> consider it a trap
            ('INVALID', ['TEST INVALID']),
            ('TRAPPED', ['Segmentation fault', '<QEMU ABORTED>', '<GDB-SIGTRAP>', '<GDB-IDLE-BREAKPOINT>']),
            ('COMPLETED', ['TEST COMPLETED']),
            ('TIMED OUT', ['>>>']), #always return true
        ]

CWE_680_INT_OVERFLOW_LOOKFOR = [
            ('CORRECTED',    ['BUFFER SIZE CORRECTED']),
            ('INSUFFICIENT', ['BUFFER SIZE INSUFFICIENT'])
        ]

def triage(filepath,lookfor):
    if not filepath.is_file():
        logAndExit(f"<bufferErrors.count.triage> <{filepath}> is not a file",
                   exitCode=EXIT.Files_and_paths)
    for (symbol, indicators) in lookfor:
        log = ftOpenFile(filepath, 'r')
        testRan = False
        for line in log:
            if '<BufferErrors Start>' in line:
                testRan = True
            if not testRan:
                continue
            # Don't do any scoring if the indicator is the first
            # match found, since that indicates the test didn't even run
            for indicator in indicators:
                pos = line.find(indicator)
                if pos > 0 or (testRan and pos == 0):
                    log.close()
                    return symbol
        log.close()
    if testRan:
        return 'TIMED OUT'
    else:
        return 'FAIL'

def scoreLog(logFile, lookfor):
    #First, get the triage decision
    logSymbol = triage(logFile,lookfor)
    if (logSymbol == 'INVALID'):
        return SCORES.INVALID
    elif (logSymbol == 'ERR'):
        thisScore = SCORES.CALL_ERR
    elif (logSymbol in ['COMPLETED', 'TIMED OUT']):
        thisScore = SCORES.V_HIGH
    elif (logSymbol == 'TRAPPED'):
        thisScore = SCORES.NONE
    else:
        thisScore = SCORES.FAIL
    return (adjustToCustomScore(ftReadLines(logFile), thisScore), logSymbol)

def bfparams(filepath):
    # we might want template parameters too...
    # maybe even compiler flags
    if not filepath.is_file():
        logAndExit(f"<bufferErrors.count.bfparams> <{filepath}> is not a file",
                   exitCode=EXIT.Files_and_paths)
    log = ftOpenFile(filepath, 'r')
    for line in log:
        if line.startswith(' * params:'):
            idx    = line.find(':')
            obj    = line[idx+1:]
            params = json.loads(obj)["bof"]
            log.close()
            return params
    log.close()
    return {}

def test_ord(t):
    try:
        return int(t[0]['TestNumber'])
    except:
        return -1

def scoreCWE680(path, lookfor, cwes):
    """
    Special scoring function for CWE 680.  In addition to the usual inputs to
    scoreLog, this function takes an additional parameter `cwes` of the list of
    CWEs that the generated test stresses.  This function also returns an extra
    tuple value of the actual CWEs that were tested, which may differ from
    `cwes` if the processor detected the integer overflow portion of the test.
    """
    # Check whether size overflow was detected
    int_overflow = triage(path, CWE_680_INT_OVERFLOW_LOOKFOR + lookfor)
    if int_overflow in {'CORRECTED', 'TRAPPED'}:
        # The size overflow was either corrected for, or the processor trapped
        # on the overflow (we know it was from the overflow because if triage
        # reports "TRAPPED" instead of "CORRECTED" or "INSUFFICIENT" than the
        # printf statement in the test following the size parameter overflow
        # was never executed).  Report NONE for CWE-680, but remove other CWEs
        # from the test list as no overruns were tested in this run.
        return (adjustToCustomScore(ftReadLines(path), SCORES.NONE),
                int_overflow,
                ['CWE_680'])

    # Size overflow was either not detected, or not properly corrected.  Score
    # test as usual.
    return scoreLog(path, lookfor) + (cwes,)


def tabulate(logs,lookfor):
    if (len(logs)==0):
        warnAndLog('<bufferErrors.count.tabulate> No log files found!')

    rows = []
    for name, log in logs:
        cfile = Path(os.path.join(getSetting("buildDir"),
                            "bufferErrors", f"{name}.c"))
        if not cfile.is_file():
            logAndExit(f"<bufferErrors.count.tabulate> C file {cfile} not found")
        params = bfparams(cfile)
        if "CWE_680" in params["CWE"]:
            # CWE_680 has two parts and requires special scoring
            result, logSymbol, cwes = scoreCWE680(Path(log),
                                                  lookfor,
                                                  params["CWE"])
            params["CWE"] = cwes
        else:
            result, logSymbol = scoreLog (Path(log), lookfor)
        row = ({'TestNumber': name,
                'Result': result},
               logSymbol)
        row[0].update(params)
        # TODO: also record simulator and binary hashes?
        rows.append(row)
    rows.sort(key=test_ord)
    
    if isEnabledDict('bufferErrors', 'csvFile'):
        writeCSV(rows)
    return [row[0] for row in rows]

def writeCSV(rows):
    csvOut = ftOpenFile(os.path.join(getSetting('cwesEvaluationLogs'),
                                     'bufferErrors',
                                     'bufferErrors.csv'),
                        'w')
    # this works since Py3 dicts preserve insertion order
    csvOut.write(','.join(rows[0][0].keys()) + '\n')
    for row, logSymbol in rows:
        vs = row.values()
        vss = [ fixup(v, logSymbol) for v in vs ]
        csvOut.write(','.join(vss) + '\n')
    csvOut.close()

def fixup(v, logSymbol):
    if type(v) == list:
        vals = ','.join(v)
        return f"\"[{vals}]\""
    elif type(v) == SCORES:
        return logSymbol
    elif type(v) == bool:
        return str(v)
    return v

