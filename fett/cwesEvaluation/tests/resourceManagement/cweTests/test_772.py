import time
import re

from fett.base.utils.misc import *

def test_772 (target,binTest):
    testNum = 772
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))
    nResourceLimit = target.testsPars['nResourceLimit']

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage == 'debian' or target.osImage == 'FreeBSD'):
        outLog += "-"*20 + "Part01: exhaust the resources." + "-"*20 + "\n"
        
        # Snapshot the current limits.
        # @note kiniry Linux uses `ulimit` and FreeBSD uses `limits` to
        # check and set limits.
        # `S` is for *soft* limit; `H` is for *hard* (kernel) limits.
        # `n` is for number of open file descriptors, which is the resource
        # that is the focus of this particular CWE test.
        if (target.osImage == 'debian'):
            limitCmd = "ulimit"
        else:
            limitCmd = "limits"
        limBackup = {'S': -1, 'H': -1}
        for limType in limBackup:
            retLim = target.typCommand(f"echo \"limit=`{limitCmd} -{limType}n`\"")
            outLog += retLim
            for line in retLim.splitlines():
                if (target.osImage == 'debian'):
                    limMatch = re.match(r'^.*limit=(?P<theLimit>\d+).*$',line)
                else:
                    limMatch = re.match(r'^.*openfiles[ ]+(?P<theLimit>\d+)$',line)
                if (limMatch is not None):
                    limBackup[limType] = (int(limMatch.group('theLimit')))
        if ((limBackup['S'] == -1) or (limBackup['H'] == -1)):
             outLog += f"\n<INVALID> Failed to get the original system maximum number of open file descriptors limits.\n"

        # Change the limit to the configurable value.
        # @note kiniry This value must be *smaller* than the value defined
        # at compile-time in `test_772.c` (see `MAX_NUM_OF_FILES`).
        for limType in limBackup:
            if (target.osImage == 'debian'):
                outLog += target.typCommand(f"{limitCmd} -{limType}n {nResourceLimit}")
            else:
                outLog += target.typCommand(f"{limitCmd} -P $$ -{limType}n {nResourceLimit}")

        # Run the test.
        outLog += target.typCommand(f"./{binTest}")

        # Reset the limits.
        for limType in reversed(list(limBackup.keys())):
            outLog += target.typCommand(f"{limitCmd} -{limType}n {limBackup[limType]}")

        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"
        time.sleep (1)

    else:
        target.reportAndExit("Error in {0}: <test_{2}> is not implemented for <{1}>.".format(target.filename,target.osImage,testNum))
    return outLog
