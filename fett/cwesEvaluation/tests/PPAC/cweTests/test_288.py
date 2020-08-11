import time
import socket, ssl, select

def test_288 (target,binTest):
    testNum = 288
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage == 'debian'):
        def runAuthTest (useCorrectPassword):
            retLog = ''
            retCommand = target.runCommand("./{0}".format(binTest),endsWith=[":~\$",":~$","Password:"],shutdownOnError=False)
            retLog += retCommand[1]
            if (retCommand[3] == 2): #asked for password
                pwUsed = target.userPassword if (useCorrectPassword) else 'x'
                retLog += target.runCommand(pwUsed,shutdownOnError=False)[1]
            return retLog
        
        #some useful commands
        createKeyring = ["keyctl newring keyring288 @u", "keyctl setperm \%:keyring288 0x3f01001b"]
        #permissions for keys/keyrings: setAttributes:link:search:write:read:view (from 00-3f), possessor:uid:gid:oth
        createKey = ["keyctl add user auth:{0} authToken %:keyring288".format(target.userName), "keyctl setperm \%user:auth:{0} 0x3f01000b".format(target.userName)]
        linkKeyring = "keyctl link %:keyring288 @u" #Not a list
        revokeKeyring = ["keyctl revoke %:keyring288"]

        outLog += "-"*20 + "Part01: Valid Keyring. No key. Wrong Password." + "-"*20 + "\n"
        target.executeOnRoot (createKeyring)
        outLog += target.runCommand (linkKeyring,shutdownOnError=False)[1]
        outLog += runAuthTest (False)
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part02: Valid Keyring. No key. Correct Password." + "-"*20 + "\n"
        #keyring already exists and linked from p01
        outLog += runAuthTest (True)
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part03: Valid Keyring. Valid key. Wrong Password." + "-"*20 + "\n"
        #keyring already exists from p01 and p02
        target.executeOnRoot (createKey)
        outLog += target.runCommand (linkKeyring,shutdownOnError=False)[1] #needs to be re-linked because of switchUser
        outLog += runAuthTest (False)
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part04: Valid Keyring. Local key. Wrong Password." + "-"*20 + "\n"
        target.executeOnRoot (revokeKeyring + createKeyring)
        outLog += target.runCommand (linkKeyring,shutdownOnError=False)[1]
        outLog += target.runCommand (createKey[0],shutdownOnError=False)[1] #local key -- no need to edit permissions
        outLog += runAuthTest (False)
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part05: Local Keyring. Local key. Wrong Password." + "-"*20 + "\n"
        target.executeOnRoot (revokeKeyring)
        outLog += target.runCommand (createKeyring[0],shutdownOnError=False)[1] #local keyring -- no need to edit permissions
        outLog += target.runCommand (createKey[0],shutdownOnError=False)[1] #local key -- no need to edit permissions
        outLog += runAuthTest (False)
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        time.sleep (1)

    elif (target.osImage == 'FreeBSD'):
        outLog += "-"*20 + "Part01: $CWD is home directory" + "-"*20 + "\n"
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part02: $CWD is cgi-bin directory" + "-"*20 + "\n"
        outLog += target.runCommand("mkdir -p /tmp/ssith/cgi-bin",shutdownOnError=True)[1]
        outLog += target.runCommand("mv ./{0} /tmp/ssith/cgi-bin/".format(binTest),shutdownOnError=False)[1]
        outLog += target.runCommand("cd /tmp/ssith/cgi-bin".format(binTest),shutdownOnError=False)[1]
        outLog += target.runCommand("./{0}".format(binTest),shutdownOnError=False)[1]
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

    elif (target.osImage == 'FreeRTOS'):
        if (target.testsPars['TESTGEN_TEST_PART'] == 1):
            outLog += "-"*20 + "Part01: Valid permissions. List the username." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 2):
            outLog += "-"*20 + "Part02: Valid permissions. Do not list the username." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 3):
            outLog += "-"*20 + "Part03: List the username, do not verify the client." + "-"*20 + "\n"
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

        certSuffix = 'SSITH' if (target.testsPars['TESTGEN_TEST_PART'] == 3) else ''
        breakAttemptsLoop = False
        for iAttempt in range(2): 
            message = f"TESTGEN-{testNum}-P0{target.testsPars['TESTGEN_TEST_PART']}.{iAttempt}"
            try:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.settimeout(60) #blocking operations
                clientSocket.connect((target.ipTarget,target.portTarget+iAttempt))
            except:
                outLog += "\n[host-client]: INVALID: Failed to connect to target.\n"
                break
            if (iAttempt == 0):
                try:
                    TLS_CTX = ssl.SSLContext (ssl.PROTOCOL_TLSv1_2) #create a new context
                    TLS_CTX.verify_mode = ssl.CERT_REQUIRED 
                    TLS_CTX.load_verify_locations (cafile="{0}/lib/caCert{1}.pem".format(target.testsDir,certSuffix)) #load the CA cert
                    TLS_CTX.load_cert_chain(certfile="{0}/lib/clientCert{1}.pem".format(target.testsDir,certSuffix),keyfile="{0}/lib/clientKey{1}.pem".format(target.testsDir,certSuffix))
                except:
                    outLog += "\n[host-client]: INVALID: Failed to load the CA certificate into a TLS context.\n"
                    break
                try:
                    clientSocket = TLS_CTX.wrap_socket(clientSocket,do_handshake_on_connect=True) #wrap the connected socket
                    outLog += "\n[host-client]: GRANTED: Socket wrapped successfully!\n"
                    breakAttemptsLoop = True
                except ssl.CertificateError:
                    outLog += "\n[host-client]: DENIED: Wrong certificate!\n"
                    continue
                except socket.timeout:
                    outLog += "\n[host-client]: INVALID: Timed-out while trying to wrap the TCP socket.\n"
                    break
                except:
                    outLog += "\n[host-client]: INVALID: Failed to wrap the TCP socket due to non-CertificateError.\n"
                    break    

            doCommunicate = True
            recvSuffix = ''
            while(doCommunicate):
                try:   
                    clientSocket.sendall(message.encode('utf-8'))
                except:
                    outLog += "\n<INVALID> [host-client]: Failed to send message to target.\n"
                    breakAttemptsLoop = True
                    break

                outLog += target.runCommand("sendToTarget",endsWith=f"<TARGET-RECV{recvSuffix}>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=20,shutdownOnError=False)[1]
                try:
                    # Look for the response
                    ready = select.select([clientSocket], [], [], 10) #10 seconds timeout
                    if ready[0]:
                        recvData = str(clientSocket.recv(128),'utf-8')
                        if (recvData == "SEND-USERNAME"):
                            outLog += "\n[host-client]: Received [{0} Bytes]:\n<HOST-RECV-REQUEST>:{1}\n".format(len(recvData),recvData)
                            message = "Jedi Order CLNT"
                            recvSuffix = "-USERNAME"
                        else:
                            outLog += "\n[host-client]: Received [{0} Bytes]:\n<HOST-RECV>:{1}\n".format(len(recvData),recvData)
                            doCommunicate = False #we're done
                    else:
                        raise 
                except:
                    outLog += "\n<INVALID> [host-client]: Failed to receive message from target.\n"
                    breakAttemptsLoop = True
                    break

            socketThreadsCollect.append(target.socketCloseAndCollect(clientSocket))
            if (TLS_CTX):
                del TLS_CTX
            if (breakAttemptsLoop):
                break
        
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
