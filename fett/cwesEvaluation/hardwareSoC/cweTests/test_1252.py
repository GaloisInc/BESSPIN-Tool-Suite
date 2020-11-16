from fett.base.utils.misc import *
import fett.cwesEvaluation.hardwareSoC.vulClassTester as vulClassTester

def test_1252 (target,binTest):
    testNum = 1252
    if (binTest != f"test_{testNum}.riscv"):
        target.terminateAndExit(f"Calling <test_{testNum}> for binary <{binTest}>.",exitCode=EXIT.Dev_Bug)

    if (not target.hasGdbAccess()):
        target.terminateAndExit(f"<test_{testNum}> requires GDB access!",exitCode=EXIT.Dev_Bug)

    with vulClassTester.inGdbTest(target):
        if (target.xlen==32):
            outLog = ""
        elif (target.xlen==64):
            outLog = ""

    if (target.osImage in ['debian','FreeBSD']):
        outLog += target.runCommand(" ")[1]
    elif (target.osImage == 'FreeRTOS'):
        outLog += target.endFreeRTOSTest()
    else:
        target.terminateAndExit(f"<test_{testNum}> is not implemented for <{target.osImage}>.",exitCode=EXIT.Dev_Bug)

    return outLog