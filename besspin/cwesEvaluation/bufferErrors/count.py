from pathlib import Path
import os
import json

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.scoreTests import SCORES, adjustToCustomScore

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
    """
    Look for keywords in a log file and return a symbol representing the
    highest priority keyword found.

    ARGUMENTS:
    ----------
        filepath : Path
            Path to the log file to triage.

        lookfor : List of Tuple of (String, List of String)
            A mapping from symbols to keywords.  Each element of the list
            represents one such mapping.  In order, the elements of each tuple
            in the list are:
                0.  A symbol.
                1.  A list of keywords that map to the symbol.
            Order of this list matters.  Elements earlier in the list are
            considered higher priority.

    RETURNS:
    --------
        A String.  The first symbol in <lookfor> to match a keyword in
        <filepath>.
    """
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
    """
    Score a buffer errors test log.

    ARGUMENTS:
    ----------
        logFile : Path
            Path to the log file to score.

        lookfor : List of Tuple of (String, List of String)
            A mapping from symbols to keywords.  Each element of the list
            represents one such mapping.  In order, the elements of each tuple
            in the list are:
                0.  A symbol.
                1.  A list of keywords that map to the symbol.
            Order of this list matters.  Elements earlier in the list are
            considered higher priority.

    RETURNS:
    --------
        A tuple of (SCORES, String) where each element of the tuple is:
            0.  The score the test received.
            1.  The first symbol in <lookfor> to match a keyword in <filepath>.
    """
    #First, get the triage decision
    logSymbol = triage(logFile,lookfor)
    if (logSymbol == 'INVALID'):
        return (SCORES.CALL_ERR, logSymbol)
    elif (logSymbol in ['COMPLETED', 'TIMED OUT']):
        thisScore = SCORES.HIGH
    elif (logSymbol == 'TRAPPED'):
        thisScore = SCORES.NONE
    else:
        thisScore = SCORES.FAIL
    return (adjustToCustomScore(ftReadLines(logFile), thisScore), logSymbol)

def bfparams(filepath):
    """
    Get the assigned parameters for a test.

    ARGUMENTS:
    ----------
        filepath : Path
            The generated C file to extract parameters from.

    RETURNS:
    --------
        A dictionary from String to Any.  Contains the parameters from the
        bof_instance this test was generated from.
    """
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
    """
    Given a row in a buffer errors score table, return the number of the test
    the row corresponds to.

    ARGUMENTS:
    ----------
        t : Dictionary from String to Any
            A row in a buffer errors score table.

    RETURNS:
    --------
        An integer.  The instance number for the test <t> corresponds to.
    """
    try:
        return int(t['TestNumber'])
    except:
        return -1

def scoreCWE680(path, lookfor, cwes):
    """
    Special scoring function for CWE 680.

    ARGUMENTS:
    ----------
        path : Path
            Path to the log file to score.

        lookfor : List of Tuple of (String, List of String)
            A mapping from symbols to keywords.  Each element of the list
            represents one such mapping.  In order, the elements of each tuple
            in the list are:
                0.  A symbol.
                1.  A list of keywords that map to the symbol.
            Order of this list matters.  Elements earlier in the list are
            considered higher priority.

        cwes : List of String
            The CWES the generated test stressed.

    RETURNS:
    --------
        A tuple of (SCORES, String, List of String) where each element of the
        tuple is:
            0.  The score the test received.
            1.  The first symbol in <lookfor> to match a keyword in <filepath>.
            2.  The CWEs that were tested in practice.  If a processor detects
                the integer overflow from CWE-680 this list will differ from
                <cwes>.
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
    """
    Score individual buffer errors logs.

    ARGUMENTS:
    ----------
        logs : List of Tuple of (String, String).
            The logs to score.  Each element of the list is a tuple with
            elements:
                0.  The name of the test.
                1.  The path to the log file to score.

        lookfor : List of Tuple of (String, List of String)
            A mapping from symbols to keywords.  Each element of the list
            represents one such mapping.  In order, the elements of each tuple
            in the list are:
                0.  A symbol.
                1.  A list of keywords that map to the symbol.
            Order of this list matters.  Elements earlier in the list are
            considered higher priority.

    SIDE-EFFECTS:
    -------------
        - If ${bufferErrors}[${csvFile}] is enabled, writes the CSV file
          containing the scores to
          <${cwesEvaluationLogs}/bufferErrors/bufferErrors.csv>.

    RETURNS:
    --------
        A list of Dictionary of String to Any.  The list contains scores and
        test parameters for each log in <logs>.
    """
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
        row = {'TestNumber': name,
               'Result': logSymbol,
               'Adjusted Result': result}
        row.update(params)
        # TODO: also record simulator and binary hashes?
        rows.append(row)
    rows.sort(key=test_ord)
    
    if isEnabledDict('bufferErrors', 'csvFile'):
        writeCSV(rows)
    return rows

def writeCSV(rows):
    """
    Convert and write a score table (such as the output from <tabulate>) as a
    CSV file.

    ARGUMENTS:
    ----------
        rows : A list of Dictionary of String to Any
            A score table.

    SIDE-EFFECTS:
    -------------
        - Writes a CSV file containing <rows> to
          <${cwesEvaluationLogs}/bufferErrors/bufferErrors.csv>.
    """
    csvOut = ftOpenFile(os.path.join(getSetting('cwesEvaluationLogs'),
                                     'bufferErrors',
                                     'bufferErrors.csv'),
                        'w')
    # this works since Py3 dicts preserve insertion order
    csvOut.write(','.join(rows[0].keys()) + '\n')
    for row in rows:
        vs = row.values()
        vss = [ fixup(v) for v in vs ]
        csvOut.write(','.join(vss) + '\n')
    csvOut.close()

def fixup(v):
    """
    Pretty format a score table element.

    ARGUMENTS:
    ----------
        v : (List of String) or Boolean or SCORES or String
            Value to pretty format.

    RETURNS:
    --------
        A pretty formatted String representation of <v>.
    """
    if type(v) == list:
        vals = ','.join(v)
        return f"\"[{vals}]\""
    elif type(v) in [bool, SCORES]:
        return str(v)
    return v

