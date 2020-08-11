import time
import socket, ssl, select

def test_284 (target,binTest):
    testNum = 284
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))
    
    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage == 'debian'):
        #some useful commands
        exposeUsersList = ["chown {0} /etc/test284users".format(target.userName)]
        resetUsersList = ["rm /etc/test284users", "touch /etc/test284users"]
        addUserToUsersList = ["echo \"{0}\" > /etc/test284users".format(target.userName)]
        exposeAuthLog = ["chmod 646 /var/log/auth.log"] 
        resetAuthLog = ["chmod 640 /var/log/auth.log", "> /var/log/auth.log"]
         
        def checkAuthLog ():
            retLog = "\n" + "x"*10 + " Checking auth.log for \"pam_284\" " + "x"*10 + "\n"
            target.runCommand ("touch authLog.dump",shutdownOnError=False)
            target.executeOnRoot (["cat /var/log/auth.log > /home/{0}/authLog.dump".format(target.userName)])
            retLog += target.runCommand ("echo \"nOccurrences=`grep -c \"pam_284\" authLog.dump`\"",shutdownOnError=False)[1] #do not use $()
            target.runCommand ("rm authLog.dump",shutdownOnError=False)
            time.sleep(1) #for some reason, it is necessary
            return retLog

        outLog += "-"*20 + "Part01: Valid permissions. List the username" + "-"*20 + "\n"
        target.executeOnRoot (addUserToUsersList)
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        outLog += checkAuthLog()
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part02: Valid permissions. Do not list username" + "-"*20 + "\n"
        target.executeOnRoot (resetAuthLog + resetUsersList)
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        outLog += checkAuthLog()
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part03: Use an exposed test284users. Attemp to breach." + "-"*20 + "\n"
        target.executeOnRoot (resetAuthLog + exposeUsersList)
        outLog += target.runCommand("echo \"{0}\" > /etc/test284users".format(target.userName),shutdownOnError=False)[1]
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        outLog += checkAuthLog()
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part04: Add user to list. Use an exposed auth.log to delete traces." + "-"*20 + "\n"
        target.executeOnRoot (resetAuthLog + exposeAuthLog + resetUsersList + addUserToUsersList)
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        outLog += target.runCommand("sed \"/pam_284/d\" /var/log/auth.log > temp.txt",shutdownOnError=False)[1]
        outLog += target.runCommand("cp temp.txt /var/log/auth.log",shutdownOnError=False)[1]
        outLog += checkAuthLog()
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        time.sleep (1)

    elif (target.osImage == 'FreeBSD'):
        #some useful commands
        #exposeUsersList = ["chown {0} /etc/test284users".format(target.userName)]
        denyUser = [f"sed  -i \"\" \"s/group=.* /group=wheel /\" /etc/pam.d/pam_{testNum}"]
        allowUser = [f"sed  -i \"\" \"s/group=.* /group={target.userName} /\" /etc/pam.d/pam_{testNum}"]
        exposeDebugLog = ["chmod 606 /var/log/debug.log"] 
        resetDebugLog = ["chmod 600 /var/log/debug.log", "> /var/log/debug.log"]

        def checkDebugLog ():
            retLog = "\n" + "x"*10 + f" Checking auth.log for \"pam_{testNum}\" " + "x"*10 + "\n"
            target.runCommand ("touch debugLog.dump",shutdownOnError=False)
            target.executeOnRoot ([f"cat /var/log/debug.log > /home/{target.userName}/debugLog.dump"])
            retLog += target.runCommand (f"echo \"nOccurrences=`grep -c \"test_{testNum}\" debugLog.dump`\"",shutdownOnError=False)[1] #do not use $()
            target.runCommand ("rm debugLog.dump",shutdownOnError=False)
            time.sleep(1) #for some reason, it is necessary
            return retLog

        outLog += "-"*20 + "Part01: Valid permissions. Allow the user's group" + "-"*20 + "\n"
        target.executeOnRoot (allowUser)
        outLog += target.runCommand(f"./{binTest}",shutdownOnError=False)[1]
        outLog += checkDebugLog()
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part02: Valid permissions. Deny user's group" + "-"*20 + "\n"
        target.executeOnRoot (resetDebugLog + denyUser)
        outLog += target.runCommand(f"./{binTest}",shutdownOnError=False)[1]
        outLog += checkDebugLog()
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        #breaching part
        outLog += "-"*20 + "Part03: Deny user's group. Expose /etc/group" + "-"*20 + "\n"
        exposeEtcGroup = ["cp /etc/group /tmp/group.bkp", "chmod 646 /etc/group"]
        target.executeOnRoot (resetDebugLog + exposeEtcGroup)
        #make myself wheel
        outLog += target.runCommand(f"sed \"s/root/root,{target.userName}/g\" /etc/group > /tmp/group.tmp",shutdownOnError=False)[1]
        outLog += target.runCommand(f"cp /tmp/group.tmp /etc/group",shutdownOnError=False)[1]
        outLog += target.runCommand(f"./{binTest}",shutdownOnError=False)[1]
        outLog += checkDebugLog()
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part04: Allow the user's group. Use an exposed debug.log to delete traces." + "-"*20 + "\n"
        restoreEtcGroup = ["mv /tmp/group.bkp /etc/group", "chmod 644 /etc/group"]
        target.executeOnRoot (restoreEtcGroup + resetDebugLog + allowUser + exposeDebugLog)
        outLog += target.runCommand(f"./{binTest}",shutdownOnError=False)[1]
        outLog += target.runCommand(f"sed \"/test_{testNum}/d\" /var/log/debug.log > temp.txt",shutdownOnError=False)[1]
        outLog += target.runCommand("cp temp.txt /var/log/debug.log",shutdownOnError=False)[1]
        outLog += checkDebugLog()
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

    elif (target.osImage == 'FreeRTOS'):
        if (target.testsPars['TESTGEN_TEST_PART'] == 1):
            outLog += "-"*20 + "Part01: Valid permissions. Do not list username." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 2):
            outLog += "-"*20 + "Part02: Valid permissions. List the username." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 3):
            outLog += "-"*20 + "Part03: Use an exposed usersList. Attempt to breach." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 4):
            outLog += "-"*20 + "Part04: Use an exposed logQueue. Attempt to delete traces." + "-"*20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only three parts! (called with part #{0})\n".format(target.testsPars['TESTGEN_TEST_PART'])
            return outLog

        socketThreadsCollect = []
        startTime = time.time()
        # start the network
        target.activateEthernet ()
        outLog += "\n[host]: Pinging target successful!\n"

        for i in range(1): #easier construct to break -- loop executed only once
            message = f"TESTGEN-{testNum}-P0{target.testsPars['TESTGEN_TEST_PART']}.0"
            try:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.settimeout(60) #blocking operations
                clientSocket.connect((target.ipTarget,target.portTarget))
                #time.sleep(1)
            except:
                outLog += "\n[host-client]: INVALID: Failed to connect to target.\n"
                break
            try:
                TLS_CTX = ssl.SSLContext (ssl.PROTOCOL_TLSv1_2) #create a new context
                TLS_CTX.verify_mode = ssl.CERT_REQUIRED 
                TLS_CTX.load_verify_locations (cafile="{0}/caCert.pem".format(target.certsDir)) #load the CA cert
                TLS_CTX.load_cert_chain(certfile="{0}/clientCert.pem".format(target.certsDir),keyfile="{0}/clientKey.pem".format(target.certsDir))
            except:
                outLog += "\n[host-client]: INVALID: Failed to load the CA certificate into a TLS context.\n"
                break
            try:
                clientSocket = TLS_CTX.wrap_socket(clientSocket,do_handshake_on_connect=True) #wrap the connected socket
                outLog += "\n[host-client]: GRANTED: Socket wrapped successfully!\n"
            except ssl.CertificateError:
                outLog += "\n[host-client]: DENIED: Wrong certificate!\n"
            except socket.timeout:
                outLog += "\n[host-client]: INVALID: Timed-out while trying to wrap the TCP socket.\n"
                break
            except:
                outLog += "\n[host-client]: INVALID: Failed to wrap the TCP socket due to non-CertificateError.\n"
                break    

            try:   
                clientSocket.sendall(message.encode('utf-8'))
            except:
                outLog += "\n<INVALID> [host-client]: Failed to send message to target.\n"
                break
            outLog += target.runCommand("sendToTarget",endsWith="<TARGET-RECV>",erroneousContents="<INVALID>",timeout=20,shutdownOnError=False)[1]
            try:
                # Look for the response
                ready = select.select([clientSocket], [], [], 10) #10 seconds timeout
                if ready[0]:
                    recvData = str(clientSocket.recv(128),'utf-8')
                    outLog += "\n[host-client]: Received [{0} Bytes]:\n<HOST-RECV>:{1}\n".format(len(recvData),recvData)
                else:
                    raise 
            except:
                outLog += "\n<INVALID> [host-client]: Failed to receive message from target.\n"
                break
            socketThreadsCollect.append(target.socketCloseAndCollect(clientSocket))
            del TLS_CTX
        
        if (">>>End of Fett<<<" not in outLog):
            retFinish = target.runCommand("allProgram",endsWith=">>>End of Fett<<<",shutdownOnError=False,timeout=20)
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
        target.reportAndExit("Error in {0}: <test_{2}> is not implemented for <{1}>.".format(target.filename,target.osImage,testNum))
    return outLog