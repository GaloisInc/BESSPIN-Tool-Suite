"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
TEST-PPAC-2: Reliance on OS and software authentication. 
            The hardware solely relies on the OS for authenticating a user, or an administrator.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def test_PPAC_2(xTarget):
    retLog = ''
    if (not xTarget.userCreated):
        retLog += "Creating User...\n"
        xTarget.createUser()

    if (xTarget.osImage=="FreeBSD"):
        retLog += "Removing <pam_group> from pam.d/su...\n"
        isSuccess,textBack,_,_ = xTarget.runCommand('sed -i "" "s/.*pam_group.*//" /etc/pam.d/su',
            erroneousContents=["sed:"],exitOnError=False,suppressErrors=True)
        if (not isSuccess):
            retLog += textBack
            retLog += "<INVALID> Failed to modify /etc/pam.d/su\n"
            return retLog

    isCalledWithinSsh = xTarget.isSshConn
    if (isCalledWithinSsh): #already is connected through SSH, exit and re-connect
        xTarget.killSshConn()

    retLog += "Connecting ssh as user...\n"
    retSsh = xTarget.openSshConn(userName=xTarget.userName,endsWith=xTarget.getDefaultEndWith(userName=xTarget.userName),specialTest=True)
    if (retSsh=='BLOCKED_IP'):
        retLog += "<USER-DENIED>\n"
        return retLog
    elif (not retSsh):
        retLog += "<INVALID> Failed to establish SSH connection and user is not blocked.\n"
        return retLog

    retLog += "\n<USER-GRANTED> Logged in using password only!\n"

    shellRoot, shellUser = xTarget.getShells()

    _, textBack, _, idxEndsWith = xTarget.runCommand("su root",endsWith=['Password:', shellRoot, shellUser],exitOnError=False,suppressErrors=True)
    retLog += textBack
    if (idxEndsWith == 0): #Asks for password
        isSuccess, textBack, _, _ = xTarget.runCommand (xTarget.rootPassword,endsWith=shellRoot,exitOnError=False,suppressErrors=True)
        retLog += textBack
        if (isSuccess):
            retLog += "\n<ROOT-GRANTED> su root access using password!\n"
            retLog += xTarget.runCommand ("exit",endsWith=shellUser)[1]
        else:
            retLog += "\n<ROOT-DENIED>\n"
    elif (idxEndsWith == 1): #No Passowrd at all!
        retLog += "\n<ROOT-GRANTED> su root access WITHOUT password!\n"
        retLog += xTarget.runCommand ("exit",endsWith=shellUser)[1]
    elif (idxEndsWith == 2): #rejected
        retLog += "\n<ROOT-DENIED>\n"
    else: #command failed for some weird reason
        retLog += "\n<INVALID> Failed to execute <su root>.\n"

    xTarget.closeSshConn()
    if (isCalledWithinSsh):
        xTarget.openSshConn()

    return retLog