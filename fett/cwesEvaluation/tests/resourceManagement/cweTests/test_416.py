import time

def test_416 (target,binTest):
    testNum = 416
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
        time.sleep(1)

    elif (target.osImage == 'FreeRTOS'):
        outLog += f"<INVALID> test_{testNum} is not yet implemented on <{target.osImage}>."

    else:
        target.reportAndExit("Error in {0}: <test_{2}> is not implemented for <{1}>.".format(target.filename,target.osImage,testNum))
    return outLog
