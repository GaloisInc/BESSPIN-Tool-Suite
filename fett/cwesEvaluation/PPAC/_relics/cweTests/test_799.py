import time
import socket, ssl, select
import threading
from fett.base.utils.misc import *

def test_799 (target,binTest):
    testNum = 799
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.terminateAndExit(f"Calling <test_{testNum}> for binary <{binTest}>.",exitCode=EXIT.Dev_Bug)
    nInteractions = getSettingDict("PPAC", "test_nAllowedInteractions")

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    #The following is shared between debian and FreeBSD
    pathToMqueue = '/dev' if (target.osImage == 'debian') else '/mnt'
    extraNohup = '' if (target.osImage == 'debian') else '> nohup.out'
    killRootNohup = ["./{0} shutdown".format(binTest), "sleep 1"]
    getNoHupOut = ["mv nohup.out /home/{0}/nohup.out".format(target.userName),
                "chown {0}:{0} /home/{0}/nohup.out".format(target.userName)]
    cpTestToRoot = [f"cp /home/{target.userName}/{binTest} ."]

    def dumpNoHup ():
        retLog = "\n" + "x"*10 + " Dumping root nohup.out " + "x"*10 + "\n"
        target.executeOnRoot (killRootNohup + getNoHupOut)
        retLog += target.runCommand ("cat nohup.out",exitOnError=False)[1]
        retLog += target.runCommand ("rm -f nohup.out",exitOnError=False)[1]       
        return retLog

    if (target.osImage == 'debian'):
        #useful in many parts
        nohupTestOnRoot = [f"nohup ./{binTest} {extraNohup}&", " ", "sleep 3", f"chmod 666 {pathToMqueue}/mqueue/Qroot"] #nohup+& needs an extra enter
        nBytesMsgQueue = nInteractions * 2 * 49 #49 is emperical from Debian implementation. 2 is the token length (1 letter + null char)
        writeNlimits = "echo \"{0}  hard    msgqueue    {1}\" > /etc/security/limits_799.conf" #needs formatting
        exposeLimits = ["chown {0} /etc/security/limits_799.conf".format(target.userName)]
        resetLimits = ["chown root /etc/security/limits_799.conf"]
        createUsersList = ["touch /etc/test799users"]
        resetUsersList = ["rm /etc/test799users", "touch /etc/test799users"]

        outLog += "-"*20 + "Part01: PAM w/ exposed test799users and manipulate it" + "-"*20 + "\n"
        exposeUsersList = ["chown {0} /etc/test799users".format(target.userName)]
        target.executeOnRoot (cpTestToRoot + [writeNlimits.format(target.userName,nBytesMsgQueue)] + createUsersList + exposeUsersList + nohupTestOnRoot)
        outLog += target.runCommand("./{0}".format(binTest),exitOnError=False)[1]
        outLog += target.runCommand("echo \"NotRealUser\" > /etc/test799users",exitOnError=False)[1]
        outLog += target.runCommand("./{0}".format(binTest),exitOnError=False)[1] #attempt to breach
        outLog += dumpNoHup()
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part02: PAM w/ exposed limits and a longer queue" + "-"*20 + "\n"
        target.executeOnRoot (resetUsersList + exposeLimits + nohupTestOnRoot)
        nBytesForLongQueue = (nInteractions+1) * 2 * 49
        outLog += target.runCommand (writeNlimits.format(target.userName,nBytesForLongQueue),exitOnError=False)[1]
        outLog += target.runCommand("./{0} 1".format(binTest),exitOnError=False)[1] #1 for long Queue
        outLog += dumpNoHup()
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part03: PAM w/ exposed limits and a wider queue" + "-"*20 + "\n"
        target.executeOnRoot (resetUsersList + exposeLimits + nohupTestOnRoot)
        nBytesForWideQueue = nInteractions * (2+2) * 49
        outLog += target.runCommand (writeNlimits.format(target.userName,nBytesForWideQueue),exitOnError=False)[1]
        outLog += target.runCommand("./{0} 2".format(binTest),exitOnError=False)[1] #2 for wide Queue
        outLog += dumpNoHup()
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"        

        outLog += "-"*20 + "Part04: Valid protection using limits and lisfile. Attempt a long queue." + "-"*20 + "\n"
        target.executeOnRoot (resetLimits + [writeNlimits.format(target.userName,nBytesMsgQueue)] + resetUsersList + nohupTestOnRoot)
        outLog += target.runCommand("./{0} 1".format(binTest),exitOnError=False)[1] #1 for a long Queue
        outLog += dumpNoHup()
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part05: Valid protection using limits and lisfile. Attempt an extra token." + "-"*20 + "\n"
        target.executeOnRoot (resetUsersList + nohupTestOnRoot)
        outLog += target.runCommand("./{0} 3".format(binTest),exitOnError=False)[1] #3 for an extra token
        outLog += dumpNoHup()
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part06: Valid protection using limits and lisfile. No breaching." + "-"*20 + "\n"
        target.executeOnRoot (resetUsersList + nohupTestOnRoot)
        outLog += target.runCommand("./{0}".format(binTest),exitOnError=False)[1]
        outLog += dumpNoHup()
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"
    
        time.sleep (1)

    elif (target.osImage == 'FreeBSD'):
        nohupTestOnRoot = [f"nohup ./{binTest} {extraNohup}&", " ", "sleep 3", f"chmod 666 {pathToMqueue}/mqueue/Qroot"] #nohup+& needs an extra enter
        mountMqueuefs = ["mkdir /mnt/mqueue", "mount -t mqueuefs null /mnt/mqueue"]
        createGroup = ["pw groupadd service799"]
        resetGroup = ["pw groupdel service799"] + createGroup

        outLog += "-"*20 + "Part01: Valid protection. No breaching. Ask again after receiving tokens" + "-"*20 + "\n"
        target.executeOnRoot (cpTestToRoot + mountMqueuefs + createGroup + nohupTestOnRoot)
        outLog += target.runCommand(f"./{binTest}",exitOnError=False)[1]
        outLog += target.runCommand(f"./{binTest}",exitOnError=False)[1]
        outLog += dumpNoHup()
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part02: Valid protection. Attempt an extra token." + "-"*20 + "\n"
        target.executeOnRoot (resetGroup + nohupTestOnRoot)
        outLog += target.runCommand(f"./{binTest} 3",exitOnError=False)[1]
        outLog += dumpNoHup()
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part03: Exposed /etc/group. Attempt to get the service twice." + "-"*20 + "\n"
        exposeEtcGroup = ["cp /etc/group /tmp/group.bkp", "chmod 646 /etc/group"]
        target.executeOnRoot (resetGroup + exposeEtcGroup + nohupTestOnRoot)
        time.sleep(3)
        outLog += target.runCommand(f"./{binTest}",exitOnError=False)[1]
        outLog += target.runCommand(f"sed \"s/:{target.userName}/:/g\" /etc/group > /tmp/group.tmp",exitOnError=False)[1]
        outLog += target.runCommand(f"cp /tmp/group.tmp /etc/group",exitOnError=False)[1]
        outLog += target.runCommand(f"./{binTest}",exitOnError=False)[1]
        outLog += dumpNoHup()
        restoreEtcGroup = ["mv /tmp/group.bkp /etc/group", "chmod 644 /etc/group"]
        target.executeOnRoot (restoreEtcGroup)
        if (isEnabled('useCustomScoring')): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        time.sleep (1)

    elif (target.osImage == 'FreeRTOS'):
        if (target.testPart == 1):
            outLog += "-"*20 + "Part01: Baseline sanity check." + "-"*20 + "\n"
        elif (target.testPart == 2):
            outLog += "-"*20 + "Part02: Using an exposed semaphore." + "-"*20 + "\n"
        elif (target.testPart == 3):
            outLog += "-"*20 + "Part03: Using an exposed structure." + "-"*20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only three parts! (called with part #{0})\n".format(target.testPart)
            return outLog

        socketThreadsCollect = []
        startTime = time.time()
        # start the network
        target.activateEthernet ()
        outLog += "\n[host]: Pinging target successful!\n"

        for iSubPart in range(nInteractions+1):
            message = f"TESTGEN-{testNum}-P0{target.testPart}.{iSubPart}"
            try:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.settimeout(90) #blocking operations
                clientSocket.connect((target.ipTarget,target.portTarget+iSubPart))
                #time.sleep(1)
            except Exception as exc:
                errorAndLog (f"test799: Failed to connect to target.",exc=exc,doPrint=False)
                outLog += "\n[host-client-{0}]: INVALID: Failed to connect to target.\n".format(iSubPart)
                break
            try:
                TLS_CTX = ssl.SSLContext (ssl.PROTOCOL_TLSv1_2) #create a new context
                TLS_CTX.verify_mode = ssl.CERT_REQUIRED 
                TLS_CTX.load_verify_locations (cafile="{0}/caCert.pem".format(target.certsDir)) #load the CA cert
                TLS_CTX.load_cert_chain(certfile="{0}/clientCert.pem".format(target.certsDir),keyfile="{0}/clientKey.pem".format(target.certsDir))
            except Exception as exc:
                errorAndLog (f"test799: Failed to load the CA certificate into a TLS context.",exc=exc,doPrint=False)
                outLog += "\n[host-client-{0}]: INVALID: Failed to load the CA certificate into a TLS context.\n".format(iSubPart)
                break
            try:
                clientSocket = TLS_CTX.wrap_socket(clientSocket,do_handshake_on_connect=True) #wrap the connected socket
                outLog += "\n[host-client-{0}]: GRANTED: Socket wrapped successfully!\n".format(iSubPart)
            except ssl.CertificateError:
                outLog += "\n[host-client-{0}]: DENIED: Wrong certificate!\n".format(iSubPart)
            except socket.timeout:
                outLog += "\n[host-client-{0}]: INVALID: Timed-out while trying to wrap the TCP socket.\n".format(iSubPart)
                break
            except Exception as exc:
                errorAndLog (f"test799: Failed to TLS wrap the TCP socket.",exc=exc,doPrint=False)
                outLog += "\n[host-client-{0}]: INVALID: Failed to wrap the TCP socket due to non-CertificateError.\n".format(iSubPart)
                break    

            try:   
                clientSocket.sendall(message.encode('utf-8'))
            except:
                outLog += "\n<INVALID> [host-client-{0}]: Failed to send message to target.\n".format(iSubPart)
                break
            outLog += target.runCommand("sendToTarget",endsWith="<TARGET-RECV>",erroneousContents="<INVALID>",timeout=20,exitOnError=False)[1]
            try:
                # Look for the response
                ready = select.select([clientSocket], [], [], 10) #10 seconds timeout
                if ready[0]:
                    recvData = str(clientSocket.recv(128),'utf-8')
                    outLog += "\n[host-client-{2}]: Received [{0} Bytes]:\n<HOST-RECV>:{1}\n".format(len(recvData),recvData,iSubPart)
                else:
                    raise 
            except:
                outLog += "\n<INVALID> [host-client-{0}]: Failed to receive message from target.\n".format(iSubPart)
                break
            socketThreadsCollect.append(target.socketCloseAndCollect(clientSocket))
            del TLS_CTX
        
        if (">>>End of Fett<<<" not in outLog):
            retFinish = target.runCommand("allProgram",endsWith=">>>End of Fett<<<",exitOnError=False,timeout=20)
            outLog += retFinish[1]
            if ((not retFinish[0]) or retFinish[2]): #bad
                outLog += "\n<WARNING> Execution did not end properly.\n"
        else: #just to be sure
            outLog += target.readFromTarget() #for anything left
        for xThread in socketThreadsCollect:
            xThread.join(timeout=3)
        minutes, seconds = divmod(time.time()-startTime, 60)
        outLog += "\n\nTest part executed in ~{:0>2}:{:0>2}\n".format(int(minutes),int(seconds))
        outLog += "-"*60 + "\n\n\n"
        
    else:
        target.terminateAndExit(f"<test_{testNum}> is not implemented for <{target.osImage}>.",exitCode=EXIT.Dev_Bug)
    return outLog