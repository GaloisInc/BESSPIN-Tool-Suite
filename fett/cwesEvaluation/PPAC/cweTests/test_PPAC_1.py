"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
TEST-PPAC-2: Missing authorization in privileged resource access.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def test_PPAC_1(xTarget):
    retLog = ''
    if (not xTarget.userCreated):
        retLog += "Creating User...\n"
        xTarget.createUser()

    # Remove all su authorization
    isSuccess,textBack,_,_ = xTarget.runCommand(
        "cp /etc/pam.d/su /tmp/su.bak && echo 'auth sufficient pam_permit.so' > /etc/pam.d/su",
        erroneousContents=["cp:","sh:"],exitOnError=False,suppressErrors=True)
    if (not isSuccess):
        retLog += textBack
        retLog += "<INVALID> Failed to modify /etc/pam.d/su\n"
        return retLog

    isCalledWithinSsh = xTarget.isSshConn
    if (isCalledWithinSsh): #already is connected through SSH, exit and re-connect
        xTarget.killSshConn()

    retLog += "Connecting ssh as user...\n"
    retSsh = xTarget.openSshConn(userName=xTarget.userName,endsWith=xTarget.getDefaultEndWith(userName=xTarget.userName))
    if (not retSsh):
        retLog += "<INVALID> Failed to establish SSH connection.\n"
        return retLog

    shellRoot, shellUser = xTarget.getShells()

    _, textBack, _, idxEndsWith = xTarget.runCommand("su root",endsWith=['Password:', shellRoot, shellUser],
                                    exitOnError=False,suppressErrors=True)
    retLog += textBack
    if (idxEndsWith == 0): #Asks for password
        retLog += "<ROOT-DENIED> Asked for password anyway.\n"
        retLog += xTarget.keyboardInterrupt(endsWith=shellUser)
    elif (idxEndsWith == 1): #No Passowrd
        retLog += "\n<ROOT-GRANTED> su root access without password!\n"
        retLog += xTarget.runCommand ("exit",endsWith=shellUser)[1]
    elif (idxEndsWith == 2): #rejected
        retLog += "\n<ROOT-DENIED> Su attempt was blocked\n"
    else: #command failed for some weird reason
        retLog += "\n<INVALID> Failed to execute <su root>.\n"

    xTarget.closeSshConn()
    if (isCalledWithinSsh):
        xTarget.openSshConn()

    # reset pam.d/su
    xTarget.runCommand("cp /tmp/su.bak /etc/pam.d/su",erroneousContents=["cp:"],
        exitOnError=False,suppressErrors=True)

    return retLog