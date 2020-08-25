import time
import socket, ssl, select

from fett.base.utils.misc import *

def runBinWithPass(target, binTest, old_password, new_password):
    outLog = ""
    outLog += ">>> Running password app\n"
    outLog += target.runCommand(f"./{binTest} {target.userName}",
                                endsWith="Password:",
                                erroneousContents="<INVALID>",
                                shutdownOnError=False)[1]
    outLog += f">>> sending old password '{old_password}'\n"
    time.sleep(1)
    outLog += target.runCommand(f"{old_password}",
                                endsWith="password:" if (isEqSetting('osImage','debian')) else 'new password:',
                                erroneousContents="<INVALID>",
                                shutdownOnError=False)[1]
    outLog += f">>> sending password '{new_password}'\n"
    time.sleep(1)
    outLog += target.runCommand(f"{new_password}",
                                endsWith="password:",
                                erroneousContents="<INVALID>",
                                shutdownOnError=False)[1]
    outLog += f">>> confirming password '{new_password}'\n"
    time.sleep(1)
    outLog += target.runCommand(f"{new_password}",
                                erroneousContents="<INVALID>",
                                shutdownOnError=False)[1]
    return outLog

def test_521 (target,binTest):
    testNum = 521
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage in ['debian', 'FreeBSD']):
        target.switchUser()
        outLog += target.runCommand(f"cp /home/{target.userName}/{binTest} .",shutdownOnError=False)[1]

        passwords = { 0: (target.userPassword, ""),
                      1: ("shortreg", "Too Short"),
                      2: ("slightlylonger", "No special characters"),
                      3: ("h2xR6veW5V8F8z6t3YdP", "First phase of reuse"),
                      4: ("h2xR6veW5V8F8z6t3YdP", "Second phase of reuse"),
                     }
        for phase in range(1,5):
            old = passwords[phase-1]
            pw = passwords[phase]
            outLog += "-"*20 + f"Part0{phase}: {pw[1]}" + "-"*20 + "\n"
            outLog += runBinWithPass(target, binTest, old[0], pw[0])
            outLog += "-"*60 + "\n\n\n"
        # Reset user password
        outLog += target.runCommand(f"passwd {target.userName}",
                                    endsWith="word:",
                                    shutdownOnError=False)[1]
        outLog += target.runCommand(f"{passwords[0][0]}",
                                    endsWith="word:",
                                    shutdownOnError=False)[1]
        outLog += target.runCommand(f"{passwords[0][0]}",
                                    shutdownOnError=False)[1]
        target.switchUser()
    else:
        outLog += f"<NOT-IMPLEMENTED> test_{testNum} is not yet implemented on <{target.osImage}>."
    return outLog
