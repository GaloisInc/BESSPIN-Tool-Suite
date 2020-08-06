import time
import socket, ssl, select

def test_289 (target,binTest):
    testNum = 289
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage == 'debian'):
        outLog += "-"*20 + "Part01: Use a fake username. Attempt to authenticate" + "-"*20 + "\n"
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        if (target.settings['useCustomScoring']): #will need the gdb output here
            # TODO: What do I need to do to support custom scoring here?
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part02: Rename username. Attempt to authenticate" + "-"*20 + "\n"
        killAllUserProcesses = "for xPid in $(ps -u {0} -o pid=); do kill -9 $xPid; done" #To be customized -- This is important to be able to run usermod
        renameUserToFrom = "usermod --login {0} {1}" #To be customized 
        # TODO: It looks like this script is being called with target on root.
        # I think I should change that?
        #target.switchUser () #NOW ON ROOT
        target.runCommand (killAllUserProcesses.format(target.userName),shutdownOnError=False)
        target.runCommand ("sed -i \"s/&USERNAME&/{0}/\" /etc/pam.d/pam_289".format(target.userName),shutdownOnError=False)
        time.sleep (20) #Give time to close the process opened by the user
        retCommand = target.runCommand (renameUserToFrom.format("ssithLord", target.userName),erroneousContents="usermod:",shutdownOnError=False)
        if ((not retCommand[0]) or (retCommand[2])): #Error
            outLog += "\n<INVALID>\nFailed to execute \"usermod --login\"!\n"
        backupUserName = target.userName
        target.userName = "ssithLord" #To be able to login when using switchUser
        target.switchUser () #BACK ON USER: ssithLord
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        target.userName = backupUserName
        target.switchUser () #NOW ON ROOT
        target.runCommand (killAllUserProcesses.format("ssithLord"),shutdownOnError=False)
        time.sleep (20) #Give time to close the process opened by the user
        target.runCommand (renameUserToFrom.format(target.userName,"ssithLord"),erroneousContents="usermod:",shutdownOnError=False) #reset userName
        target.switchUser () #Back on user
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part03: Change the bash. Attempt to authenticate" + "-"*20 + "\n"
        retCommand = target.runCommand("chsh -s /bin/rbash",endsWith="Password:",timeout=15,shutdownOnError=False)
        outLog += retCommand[1]
        if ((not retCommand[0]) or (retCommand[2])): #Error
            outLog += "\n<INVALID>\nFailed to execute \"chsh\"!\n"
        else:
            outLog += target.runCommand(target.userPassword,shutdownOnError=False)[1]
            outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
            outLog += target.runCommand("chsh -s /bin/bash",endsWith="Password:",timeout=15,shutdownOnError=False)[1]
            outLog += target.runCommand(target.userPassword,shutdownOnError=False)[1]
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"
        time.sleep (5)

    elif (target.osImage == 'FreeBSD'):
        renameGroupToFrom = "pw groupmod -l {0} -n {1}" #To be customized

        outLog += "-"*20 + "Part01: Sanity check: block user's group. Attempt to authenticate" + "-"*20 + "\n"

        target.switchUser() #NOW ON ROOT
        target.runCommand ("sed -i -e \"s/NOTAGROUP/{0}/\" /etc/pam.d/pam_289".format(target.userName),shutdownOnError=False)
        target.switchUser() #NOW ON USER
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part02: Use a fake group name. Attempt to authenticate" + "-"*20 + "\n"
        target.switchUser() #NOW ON ROOT
        target.runCommand ("sed -i -e \"s/{0}/NOT_A_GROUP/\" /etc/pam.d/pam_289".format(target.userName),shutdownOnError=False)
        target.switchUser() #NOW ON USER
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part03: Rename a real group. Attempt to authenticate" + "-"*20 + "\n"
        target.switchUser () #NOW ON ROOT
        # Add a group for the user
        userGroup = "bad_group"
        addGroup = f"pw groupadd {userGroup} -M {target.userName}"
        target.runCommand (addGroup, shutdownOnError=False)
        target.runCommand ("sed -i -e \"s/NOTAGROUP/{0}/\" /etc/pam.d/pam_289".format(userGroup),shutdownOnError=False)
        retCommand = target.runCommand (renameGroupToFrom.format("ssithLord", userGroup),erroneousContents="usermod:",shutdownOnError=False)
        if ((not retCommand[0]) or (retCommand[2])): #Error
            outLog += "\n<INVALID>\nFailed to execute \"usermod --login\"!\n"

        target.switchUser () #BACK ON USER: ssithLord
        outLog += target.runCommand("./{0}".format(binTest),endsWith="Password:",shutdownOnError=False)[1]
        target.switchUser () #NOW ON ROOT
        time.sleep (1)
        target.runCommand (renameGroupToFrom.format(userGroup,"ssithLord"),erroneousContents="usermod:",shutdownOnError=False) #reset userName
        target.switchUser () #Back on user
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        time.sleep (1)

    elif (target.osImage == 'FreeRTOS'):
        if (target.testsPars['TESTGEN_TEST_PART'] == 1):
            outLog += "-"*20 + "Part01: Valid permissions. Do not list the username or the task." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 2):
            outLog += "-"*20 + "Part02: List the username. Use a different capitalization username." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 3):
            outLog += "-"*20 + "Part03: List the task name. Create a child task." + "-"*20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only three parts! (called with part #{0})\n".format(target.testsPars['TESTGEN_TEST_PART'])
            return outLog

        socketThreadsCollect = []
        startTime = time.time()
        # start the network
        retCommand = target.activateEthernet ()
        outLog += retCommand[1]
        if ( (not retCommand[0]) or (retCommand[2]) ): #Bad
            outLog += "\n<INVALID> [host]: Failed to ping the target.\n"
            return outLog
        else:
            outLog += "\n[host]: Pinging target successful!\n"

        for i in range(1): #easier construct to break -- loop executed only once
            message = f"TESTGEN-{testNum}-P0{target.testsPars['TESTGEN_TEST_PART']}.0"
            try:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.settimeout(60) #blocking operations
                clientSocket.connect((target.ipTarget,target.portTarget))
            except:
                outLog += "\n[host-client]: INVALID: Failed to connect to target.\n"
                break
            try:
                TLS_CTX = ssl.SSLContext (ssl.PROTOCOL_TLSv1_2) #create a new context
                TLS_CTX.verify_mode = ssl.CERT_REQUIRED 
                TLS_CTX.load_verify_locations (cafile="{0}/lib/caCert.pem".format(target.testsDir)) #load the CA cert
                TLS_CTX.load_cert_chain(certfile="{0}/lib/clientCert.pem".format(target.testsDir),keyfile="{0}/lib/clientKey.pem".format(target.testsDir))
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
            outLog += target.runCommand("sendToTarget",endsWith="<TARGET-RECV>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=20,shutdownOnError=False)[1]
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
        
        if (">>>End of Testgen<<<" not in outLog):
            retFinish = target.runCommand("allProgram",endsWith=">>>End of Testgen<<<",shutdownOnError=False,timeout=20)
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
