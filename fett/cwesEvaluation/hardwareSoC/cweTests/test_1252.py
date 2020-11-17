from fett.base.utils.misc import *
import fett.cwesEvaluation.hardwareSoC.vulClassTester as vulClassTester

def test_1252 (target,binTest):
    testNum = 1252
    if (binTest != f"test_{testNum}.riscv"):
        target.terminateAndExit(f"Calling <test_{testNum}> for binary <{binTest}>.",exitCode=EXIT.Dev_Bug)

    if (not target.hasGdbAccess()):
        target.terminateAndExit(f"<test_{testNum}> requires GDB access!",exitCode=EXIT.Dev_Bug)

    outLog = ""
    with vulClassTester.inGdbTest(target):
        pmpRegsNames = [f'pmpcfg{iCfg}' for iCfg in range(4)] + [f'pmpaddr{iCfg}' for iCfg in range(16)]
        pmpRegsVals = target.getRegsValues(regNames=pmpRegsNames)

        #Check that we now have all the PMP regs values
        
        if (len(set(pmpRegsNames) - set(pmpRegsVals))>0): #missing regs
            errorAndLog("test_1252: Failed to find the values of the following regs: "
                f"<{','.join(set(pmpRegsNames)-set(pmpRegsVals))}>")
            outLog += "<INVALID> Missing registers values."
        else:
            bCfgPerAddr = {} #this dict will carry the 8-bits CFGs of the pmpaddr0-15
            if (target.xlen==32):
                for iCfg in range(4):
                    mask = int(0xff)
                    for iByte in range(4):
                        bCfgPerAddr[iCfg*4+iByte] = (pmpRegsVals[f'pmpcfg{iCfg}'] & mask) >> (iByte*8)
                        mask <<= 8
            elif (target.xlen==64):
                for iCfg in range(2):
                    mask = int(0xff)
                    for iByte in range(8):
                        bCfgPerAddr[iCfg*8+iByte] = (pmpRegsVals[f'pmpcfg{iCfg*2}'] & mask) >> (iByte*8)
                        mask <<= 8

            for iCfg in range(16): #looping through the 16 possible regions
                outLog += f"<cfg{iCfg}>: "
                
                A = (int(0x18) & bCfgPerAddr[iCfg]) >> 3
                X = (int(0x4) & bCfgPerAddr[iCfg]) >> 2
                W = (int(0x2) & bCfgPerAddr[iCfg]) >> 1
                R = int(0x1) & bCfgPerAddr[iCfg]

                if (A==0):
                    outLog += f"<Disabled>\n"
                    continue
                elif (A==1): #TOR (Top Of Range)
                    if (    ((iCfg==0) and (pmpRegsVals[f'pmpaddr{iCfg}']>0)) or
                            ((iCfg>0) and (pmpRegsVals[f'pmpaddr{iCfg-1}'] < pmpRegsVals[f'pmpaddr{iCfg}']))
                        ):
                        outLog += f"<TOR> - "
                    else:
                        outLog += f"<TOR> - <Bad-Range>\n"
                        continue
                elif (A==2):
                    outLog += f"<NA4> - "
                elif (A==3):
                    outLog += f"<NAPOT> - "

                if (X==0):
                    outLog += "<EXECUTION>\n"
                elif (W==0):
                    outLog += "<WRITE>\n"
                elif (R==0):
                    outLog += "<READ>\n"
                else:
                    outLog += "<Non-Protected>\n"

    if (isEnabled('useCustomScoring')): #will need the gdb output here
        outLog += target.getGdbOutput()

    return outLog

