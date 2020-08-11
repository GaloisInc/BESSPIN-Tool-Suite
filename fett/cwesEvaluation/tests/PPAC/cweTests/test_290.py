import time
import socket
import subprocess 
import sys, os
import getpass

from fett.base.utils.misc import *

def test_290 (target,binTest):
    #This test is special -- is called using sudo
    testNum = 290
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage in ['debian','FreeBSD']):
        outLog += f"<INVALID> test_{testNum} is covered by TEST-294 for <{target.osImage}>."

    elif (target.osImage == 'FreeRTOS'):
        if (target.testsPars['TESTGEN_TEST_PART'] == 1):
            outLog += "-"*20 + "Part01: Baseline sanity check. No spoofing." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 2):
            outLog += "-"*20 + "Part02: Don't authorize the IP. Try to spoof it." + "-"*20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only three parts! (called with part #{0})\n".format(target.testsPars['TESTGEN_TEST_PART'])
            return outLog

        startTime = time.time()
        # start the network
        retCommand = target.activateEthernet ()
        outLog += retCommand[1]
        if ( (not retCommand[0]) or (retCommand[2]) ): #Bad
            outLog += "\n<INVALID> [host]: Failed to ping the target.\n"
            return outLog
        else:
            outLog += "\n[host]: Pinging target successful!\n"

        for i in range(1): #easier construct to break -- loop executed only once
            outLog += target.runCommand("waitForServer",endsWith="<UDP-READY>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=20,shutdownOnError=False)[1]
            if (target.testsPars['TESTGEN_TEST_PART'] == 1):
                outLog += ">>> [host-client]: Sending a good UDP packet..."
                try:
                    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
                    clientSocket.sendto(bytes("JEDI CLNT", "utf-8"), (target.ipTarget, target.portTarget))
                except:
                    outLog += "<INVALID> [host-client]: Failed to send packet to target.\n"
                    break
                outLog += ">>> [host-client]: Packet sent!"
                target.socketCloseAndCollect(clientSocket).join(timeout=3)
            else: #part2 -- spoofing
                spoofingIP = target.testsPars['SPOOFING_IP']
                pathToSudoPart = os.path.dirname(__file__) + f"/sudoTests/sudo_{testNum}.py"
                sudoPrompt = f"\"Warning: You need sudo privileges to run test_{testNum}: [sudo] password for {getpass.getuser()}: \""
                try:
                    outLog += str(subprocess.check_output (f"sudo -p {sudoPrompt} {sys.executable} {pathToSudoPart} {'+'.join(sys.path)} {target.ipTarget} {target.portTarget} {spoofingIP}",stderr=subprocess.STDOUT,shell=True),'utf-8')
                except KeyboardInterrupt as exc:
                    errorAndLog (f"[host]: Interrupted. Failed to run <sudo sudo_{testNum}>.\n", exc=exc)
                    outLog += f"\n<INVALID> [host]: Interrupted. Failed to run <sudo sudo_{testNum}>.\n"
                except:
                    outLog += f"\n<INVALID> [host]: Failed to run <sudo sudo_{testNum}>.\n"

        if (">>>End of Testgen<<<" not in outLog):
            retFinish = target.runCommand("allProgram",endsWith=">>>End of Testgen<<<",shutdownOnError=False,timeout=20)
            outLog += retFinish[1]
            if ((not retFinish[0]) or retFinish[2]): #bad
                outLog += "\n<WARNING> Execution did not end properly.\n"
        else: #just to be sure
            outLog += target.readFromTarget() #for anything left
        
        minutes, seconds = divmod(time.time()-startTime, 60)
        outLog += "\n\nTest part executed in ~{:0>2}:{:0>2}\n".format(int(minutes),int(seconds))
        outLog += "-"*60 + "\n\n\n"

    else:
        target.reportAndExit("Error in {0}: <test_{2}> is not implemented for <{1}>.".format(target.filename,target.osImage,testNum))
    return outLog
