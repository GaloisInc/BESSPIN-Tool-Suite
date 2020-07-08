import time

def test_476 (target,binTest):
    testNum = 476
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))
    nResourceLimit = target.testsPars['nResourceLimit']

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage == 'debian' or target.osImage == 'FreeBSD'):
        #Run the test
        outLog += "-"*20 + "Part01: exhaust the resources." + "-"*20 + "\n"
        outLog += target.typCommand(f"./{binTest}")
        outLog += "-"*60 + "\n\n\n"

        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"
        time.sleep (1)
        
    elif (target.osImage == 'FreeRTOS'):
        if (target.testsPars['TESTGEN_TEST_PART'] == 1):
            outLog += "-"*20 + "Part01: Inbound test." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 2):
            outLog += "-"*20 + "Part02: Outbound test." + "-"*20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only two parts! (called with part #{0})\n".format(target.testsPars['TESTGEN_TEST_PART'])
            return outLog
        if (">>>End of Testgen<<<" not in outLog):
            retFinish = target.runCommand("allProgram",endsWith=">>>End of Testgen<<<",shutdownOnError=False,timeout=20)
            outLog += retFinish[1]
            if ((not retFinish[0]) or retFinish[2]): #bad
                outLog += "\n<WARNING> Execution did not end properly.\n"
        else: #just to be sure
            outLog += target.readFromTarget() #for anything left

        outLog += "-"*60 + "\n\n\n"

    else:
        target.reportAndExit("Error in {0}: <test_{2}> is not implemented for <{1}>.".format(target.filename,target.osImage,testNum))
    return outLog
