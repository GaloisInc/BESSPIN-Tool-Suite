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
        xTarget.runCommand('sed -i "" "s/.*pam_group.*//" /etc/pam.d/su')

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

    shellRoot = xTarget.getDefaultEndWith(userName='root')
    shellUser = xTarget.getDefaultEndWith(userName=xTarget.userName)
    if ((not isinstance(shellRoot,str)) or (not isinstance(shellUser,str))):
        retLog += "<INVALID> BUG in the test; expecting strings for <shellRoot> and <shellUser>.\n"
        return retLog
    shellRoot = shellRoot.replace('~',f"/home/{xTarget.userName}")

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

    if (isCalledWithinSsh):
        xTarget.openSshConn()

    return retLog