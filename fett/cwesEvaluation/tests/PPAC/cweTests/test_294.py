import time
import subprocess
import sys, os
import getpass

from fett.base.utils.misc import *

def test_294(target, binTest):
    # This test is special -- is called using sudo
    testNum = 294
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit(
            "Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename, binTest, testNum))

    outLog = "\n" + '*' * 30 + " TEST {0} ".format(testNum) + '*' * 30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    spoofingIP = target.testsPars['SPOOFING_IP']

    if (target.backend == 'qemu'):
        outLog += f"<QEMU-N/A> test_{testNum} is not yet implemented on <qemu>."

    elif (target.osImage in ['debian','FreeBSD']):
        partNames = ['Block the host\'s ip.', 'Allow the host\'s ip.']
        allowedIP = [spoofingIP.strip('\"'),target.ipHost]

        target.switchUser () #this test is executed on root

        if (not target.onlySsh): #special case. No JTAG available.
            #saving the ssh state
            bkpIsSshConn = target.targetObj.isSshConn
            if (bkpIsSshConn): #there was an sshConnection
                target.closeSshConn() 
            bkpSshLimitRetries = target.sshLimitRetries
            bkpSshRetries = target.sshRetries
            target.sshLimitRetries = 1 #temporarily
            target.sshRetries = 0 #temporarily

        #allow root ssh first
        outLog += target.runCommand ("echo \"PermitRootLogin yes\" >> /etc/ssh/sshd_config",shutdownOnError=False)[1]
        if (target.osImage == 'debian'):
            #deny all 
            outLog += target.runCommand ("echo \"PasswordAuthentication no\" >> /etc/ssh/sshd_config",shutdownOnError=False)[1]
            # service will be reset again in the loop anyway
        elif (target.osImage == 'FreeBSD'):
            outLog += self.runCommand("/etc/rc.d/sshd start",shutdownOnError=False)[1]
            outLog += target.runCommand ("echo \"sshd : ALL : deny\" > /etc/hosts.allow",shutdownOnError=False)[1]

        for iPart in range(2):
            outLog += "-" * 20 + f"Part0{iPart+1}: {partNames[iPart]}" + "-" * 20 + "\n"

            #only allow the part's IP
            if (target.osImage == 'debian'):
                outLog += target.runCommand (f"echo \"Match Address {allowedIP[iPart]}\" >> /etc/ssh/sshd_config",shutdownOnError=False)[1]
                outLog += target.runCommand ("echo \"    PasswordAuthentication yes\" >> /etc/ssh/sshd_config",shutdownOnError=False)[1]
                outLog += target.runCommand ("service ssh restart",shutdownOnError=False)[1]
                time.sleep(10)
            elif (target.osImage == 'FreeBSD'):
                outLog += target.runCommand (f"sed  -i \"\" \"1 s/^/sshd : {allowedIP[iPart]} : allow\\n/\" /etc/hosts.allow",shutdownOnError=False)[1]

            if ((not target.onlySsh) or (iPart == 1)):
                if (target.onlySsh):
                    target.closeSshConn()
                #attempt to connect
                retSsh = target.openSshConn(specialTest=True)
                if (retSsh == 'BLOCKED_IP'):
                    target.killSshConn()
                    outLog += "\n<SSH-ATTEMPT>:<BLOCKED-IP>\n"
                elif (retSsh): #connection successful
                    if (not target.onlySsh):
                        target.closeSshConn()
                    outLog += "\n<SSH-ATTEMPT>:<ALLOWED-IP>\n"
                else: #failed due to non-recognized reason
                    outLog += "\n<INVALID> Failed to establish an SSH connection."
            else: #special case. No JTAG available.
                outLog += "\n<SSH-ATTEMPT>:<BLOCKED-IP>\n"

            outLog += "-" * 60 + "\n\n\n"

        if (not target.onlySsh): #special case. No JTAG available.
            #restoring the state
            target.sshLimitRetries = bkpSshLimitRetries 
            target.sshRetries = bkpSshRetries
            target.targetObj.isSshConn = bkpIsSshConn

        target.switchUser () #Go back to user

    elif (target.osImage == 'FreeRTOS'):
        if (target.testsPars['TESTGEN_TEST_PART'] == 1):
            outLog += "-" * 20 + "Part01: Baseline sanity check. No spoofing." + "-" * 20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 2):
            outLog += "-" * 20 + "Part02: Don't authorize the IP. Try to spoof it." + "-" * 20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only three parts! (called with part #{0})\n".format(
                target.testsPars['TESTGEN_TEST_PART'])
            return outLog

        startTime = time.time()
        # start the network
        target.activateEthernet ()
        outLog += "\n[host]: Pinging target successful!\n"

        if (isEqSetting('target','aws')):
            ethAdaptorName = getSetting('awsTapAdaptorName')
        elif (isEqSetting('target','fpga')):
            ethAdaptorName = getSetting('fpgaEthAdaptorName')
        else:
            errorAndLog(f"<ethAdaptorName> is not defined in <test_290> for <{getSetting('target')}>.")
            outLog += f"\n<INVALID> <ethAdaptorName> is not defined for <{getSetting('target')}>."
            return outLog
        pathToSudoPart = os.path.dirname(__file__) + f"/sudoTests/sudo_{testNum}.py"
        sudoPrompt = f"\"Warning: You need sudo privileges to run test_{testNum}: [sudo] password for {getpass.getuser()}: \""

        outLog += target.runCommand("waitForServer", endsWith="<TCP-READY>", erroneousContents="<INVALID>",
                                    timeout=20, shutdownOnError=False)[1]
        try:
            outLog += str(subprocess.check_output(
                f"sudo -p {sudoPrompt} {sys.executable} {pathToSudoPart} {'+'.join(sys.path)} {target.ipTarget} {target.portTarget} {spoofingIP} {ethAdaptorName} {target.testsPars['TESTGEN_TEST_PART']}",
                stderr=subprocess.STDOUT, shell=True), 'utf-8')
        except KeyboardInterrupt as exc:
            errorAndLog(f"[host]: Interrupted. Failed to run <sudo sudo_{testNum}>.\n", exc=exc)
            outLog += f"\n<INVALID> [host]: Interrupted. Failed to run <sudo sudo_{testNum}>.\n"
        except:
            outLog += f"\n<INVALID> [host]: Failed to run <sudo sudo_{testNum}>.\n"

        if (">>>End of Fett<<<" not in outLog):
            retFinish = target.runCommand("allProgram", endsWith=">>>End of Fett<<<", shutdownOnError=False,
                                          timeout=20)
            outLog += retFinish[1]
            if ((not retFinish[0]) or retFinish[2]):  # bad
                outLog += "\n<WARNING> Execution did not end properly.\n"
        else:  # just to be sure
            outLog += target.readFromTarget()  # for anything left

        minutes, seconds = divmod(time.time() - startTime, 60)
        outLog += "\n\nTest part executed in ~{:0>2}:{:0>2}\n".format(int(minutes), int(seconds))
        outLog += "-" * 60 + "\n\n\n"

    else:
        target.reportAndExit(
            "Error in {0}: <test_{2}> is not implemented for <{1}>.".format(target.filename, target.osImage, testNum))
    return outLog
