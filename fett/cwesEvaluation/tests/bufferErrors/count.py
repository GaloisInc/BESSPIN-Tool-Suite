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

def triage(filepath,lookfor):
    testRan = False
    if not filepath.is_file():
        logAndExit(f"<bufferErrors.count.triage> <{filepath}> is not a file",
                   exitCode=EXIT.Files_and_paths)
    for (symbol, indicators) in lookfor:
        log = ftOpenFile(filepath, 'r')
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

    try:
        fLog = ftOpenFile(logFile,'r')
        logLines = fLog.read().splitlines()
        fLog.close()
        return (adjustToCustomScore(logLines,thisScore),
                logSymbol)
    except:
        return (SCORES.FAIL, logSymbol)

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

def tabulate(dirpath,lookfor):
    dirpath = Path(dirpath)
    if not dirpath.is_dir():
        logAndExit(f"<bufferErrors.count.tabulate> <{dirpath}> is not a directory",
                   exitCode=EXIT.Files_and_paths)
    rows = []
    for path in dirpath.iterdir():
        if path.name.endswith('.log'):
            cfile = Path(os.path.join(getSetting("buildDir"),
                                      "bufferErrors",
                                      f"{path.stem}.c"))
            if not cfile.is_file():
                logAndExit(f"<bufferErrors.count.tabulate> C file {cfile} not found")
            result, logSymbol = scoreLog (path, lookfor)
            row = ({'TestNumber': path.stem,
                    'Result': result},
                   logSymbol)
            row[0].update(bfparams(cfile))
            # TODO: also record simulator and binary hashes?
            rows.append(row)
    rows.sort(key=test_ord)
    if not rows:
        logAndExit('<bufferErrors.count.tabulate> No log files found in '
                   f'<{dirpath}>',
                   exitCode=EXIT.Dev_Bug)
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
    return v

