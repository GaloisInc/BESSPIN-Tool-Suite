import time
import socket, ssl, select

from fett.base.utils.misc import *

def test_384 (target,binTest):
    testNum = 384
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.terminateAndExit(f"Calling <test_{testNum}> for binary <{binTest}>.",exitCode=EXIT.Dev_Bug)

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage in ['debian', 'FreeBSD']):
        outLog += "-"*20 + f"Part01: root then user" + "-"*20 + "\n"
        ## FreeBSD has pam_setenv to set up the user's "session" (different slightly from a pam-session, see README.md)
        ## but debian must use the pam_env session module, so we set up the environment variables here by writing
        ## to each user's $HOME/.pam_environment
        if target.osImage == 'debian':
            outLog += target.runCommand(f"echo SESSION_ID={target.userName}:1234 > ~/.pam_environment")[1]
        target.switchUser()
        if target.osImage == 'debian':
            outLog += target.runCommand(f"echo SESSION_ID=root:1234 > ~/.pam_environment")[1]

        outLog += target.runCommand(f"chown root /home/{target.userName}/{binTest}")[1]
        outLog += target.runCommand(f"chmod 4755 /home/{target.userName}/{binTest}")[1]
        target.switchUser()
        outLog += target.runCommand(f"./{binTest} root {target.userName}", endsWith="word:", erroneousContents="<INVALID>")[1]
        outLog += target.runCommand(target.rootPassword, endsWith="word:", erroneousContents="<INVALID>")[1]
        outLog += target.runCommand(target.userPassword,erroneousContents="<INVALID>")[1]

        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"
    else:
        outLog += f"<NOT-IMPLEMENTED> test_{testNum} is not yet implemented on <{target.osImage}>."
    return outLog
