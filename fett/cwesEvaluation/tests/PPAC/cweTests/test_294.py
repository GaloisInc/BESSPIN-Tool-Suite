import time
import subprocess
import sys, os
import getpass

from fett.base.utils.misc import *

def test_294(target, binTest):
    # This test is special -- is called using sudo
    testNum = 294
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.shutdownAndExit(f"Calling <test_{testNum}> for binary <{binTest}>.",exitCode=EXIT.Dev_Bug)

    outLog = "\n" + '*' * 30 + " TEST {0} ".format(testNum) + '*' * 30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    spoofingIP = getSettingDict("PPAC", "spoofingIP")

    if (isEqSetting('target','qemu')):
        outLog += f"<QEMU-N/A> test_{testNum} is not yet implemented on <qemu>."

    elif (target.osImage in ['debian','FreeBSD']):
        partNames = ['Block the host\'s ip.', 'Allow the host\'s ip.']
        allowedIP = [spoofingIP.strip('\"'),target.ipHost]

        target.switchUser () #this test is executed on root

        #allow root ssh first
        target.enableSshOnRoot()

        if (not target.onlySsh): #special case. No JTAG available.
            #saving the ssh state
            bkpIsSshConn = target.isSshConn
            if (bkpIsSshConn): #there was an sshConnection
                target.closeSshConn() 
            bkpSshLimitRetries = target.sshLimitRetries
            bkpSshRetries = target.sshRetries
            target.sshLimitRetries = 1 #temporarily
            target.sshRetries = 0 #temporarily

        #deny all 
        outLog += target.runCommand (f"echo \"PasswordAuthentication no\" >> {getSetting('sshdConfigPath')}",shutdownOnError=False)[1]

        for iPart in range(2):
            outLog += "-" * 20 + f"Part0{iPart+1}: {partNames[iPart]}" + "-" * 20 + "\n"

            #only allow the part's IP
            outLog += target.runCommand (f"echo \"Match Address {allowedIP[iPart]}\" >> {getSetting('sshdConfigPath')}",shutdownOnError=False)[1]
            outLog += target.runCommand (f"echo \"    PasswordAuthentication yes\" >> {getSetting('sshdConfigPath')}",shutdownOnError=False)[1]
            target.retartSshService ()
            time.sleep(10)

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
            target.isSshConn = bkpIsSshConn

        target.switchUser () #Go back to user

    elif (target.osImage == 'FreeRTOS'):
        if (target.testPart == 1):
            outLog += "-" * 20 + "Part01: Baseline sanity check. No spoofing." + "-" * 20 + "\n"
        elif (target.testPart == 2):
            outLog += "-" * 20 + "Part02: Don't authorize the IP. Try to spoof it." + "-" * 20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only three parts! (called with part #{0})\n".format(
                target.testPart)
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
                f"sudo -p {sudoPrompt} {sys.executable} {pathToSudoPart} {'+'.join(sys.path)} {target.ipTarget} {target.portTarget} {spoofingIP} {ethAdaptorName} {target.testPart}",
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
        target.shutdownAndExit(f"<test_{testNum}> is not implemented for <{target.osImage}>.",exitCode=EXIT.Dev_Bug)
    return outLog
