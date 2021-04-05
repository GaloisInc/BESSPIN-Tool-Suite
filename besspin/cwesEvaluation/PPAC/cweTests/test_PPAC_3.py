"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
TEST-PPAC-2: Security exceptions are not logged. 
        When the hardware throws a security exception, it does not report/log it to a privileged location.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """
from besspin.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def test_PPAC_3(xTarget):
    retLog = ''
    binName = "test_PPAC_3.riscv"

    isSuccess,textBack,_,_ = xTarget.runCommand(f"./{binName}", erroneousContents=["sh:"])
    retLog += textBack
    if (not isSuccess): #What the hell has happened?
        retLog += "<INVALID> Failed to execute the segfault binary\n"
        return retLog

    #Look for the inciden in the log
    logFile = "messages" if (xTarget.osImage=="FreeBSD") else "kern.log"
    isSuccess,textBack,_,_ = xTarget.runCommand(f"echo \"<nOccurrences=`grep -c {binName} /var/log/{logFile}`>\"", 
        erroneousContents=["sh:","grep:"],exitOnError=False,suppressErrors=True)
    retLog += textBack
    nMatch = re.search(r'<nOccurrences=(?P<nOccurrences>[\d]+)>',textBack)
    if ((not isSuccess) or (nMatch is None)):
        if ("No such file or directory" in textBack):
            retLog += f"<NO-LOG> Failed to find </var/log/{logFile}>.\n"
        else:
            retLog += f"<INVALID> Failed to grep </var/log/{logFile}>.\n"
        return retLog
    if (int(nMatch.group('nOccurrences')) < 1):
        retLog += "<LOG>:<PUB>\n"
    else:
        retLog += "<LOG>:<PRIV>\n"

    #Check for the log's permissions
    if (xTarget.osImage=='debian'):
        statFlags = "-c '<owner=%U>, <group=%G>, <permissions=%A>'"
    else: #FreeBSD
        statFlags = "-f '<owner=%Su>, <group=%Sg>, <permissions=%Sp>'"

    isSuccess,textBack,_,_ = xTarget.runCommand(f"stat {statFlags} /var/log/{logFile}", 
        erroneousContents=["sh:","ls:"],exitOnError=False,suppressErrors=True)
    retLog += textBack
    pMatch = re.search(r'<owner=(?P<owner>\w+)>, <group=(?P<group>\w+)>, <permissions=(?P<permissions>.+)>',textBack)
    if ((not isSuccess) or (pMatch is None)):
        retLog += f"<INVALID> Failed to stat </var/log/{logFile}>.\n"
        return retLog
    retLog += "Checking ownership and permissions...\n"
    # Check owner
    if (pMatch.group('owner') in ['syslog','adm','admin','root']):
        retLog += "<OWNER>:<PRIV>\n"
    else:
        retLog += "<OWNER>:<PUB>\n"
    # Check group
    if (pMatch.group('group') in ['adm','admin','root','wheel']):
        retLog += "<GROUP>:<PRIV>\n"
    else:
        retLog += "<GROUP>:<PUB>\n"
    # Check permissions
    LEN_PERMS = 1 + 3*3
    xPerms = pMatch.group('permissions')
    if (len(xPerms) != LEN_PERMS):
        retLog += f"<INVALID> Unrecognized permissions format in stat output. <len={len(xPerms)}!={LEN_PERMS}>\n"
        return retLog
    own, grp, oth = [xPerms[3*i+1:3*i+4] for i in range(3)] 
    if (oth[1] != '-'): #Others can write
        retLog += "<PERM>:<PUB>\n"
    else:
        retLog += "<PERM>:<PRIV>\n"

    return retLog
