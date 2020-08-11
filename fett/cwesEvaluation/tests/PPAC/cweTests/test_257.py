import time
import socket, ssl, select

def test_257 (target,binTest):
    testNum = 257
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage in ['FreeBSD', 'debian']):
        outLog += "-"*20 + "Part01: Plaintext Stored." + "-"*20 + "\n"

        outLog += target.runCommand("echo Me: $USER",shutdownOnError=False)[1]
        target.switchUser () # Now on Root
        outLog += target.runCommand("echo Me: $USER",shutdownOnError=False)[1]
        outLog += target.runCommand(f"cp /home/{target.userName}/{binTest} .",shutdownOnError=False)[1]
        outLog += target.runCommand("./{0} {1} '{2}'".format(binTest,target.userName,target.userPassword),shutdownOnError=False)[1]
        target.userPassword = "NotMyOldPassword"
        target.switchUser () # Now on User
        outLog += "-"*20 + "User login" + "-"*20 + "\n"
        outLog += target.runCommand("echo '<GRANTED> login with changed password'",shutdownOnError=False)[1]
        outLog += "-"*60 + "\n\n\n"

    elif (target.osImage == 'FreeRTOS'):
        if (target.testsPars['TESTGEN_TEST_PART'] == 1):
            outLog += "-"*20 + "Part01: sha256 hashes stored." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 2):
            outLog += "-"*20 + "Part02: base64 codes stored." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 3):
            outLog += "-"*20 + "Part03: plaintext stored." + "-"*20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only three parts! (called with part #{0})\n".format(target.testsPars['TESTGEN_TEST_PART'])
            return outLog

        socketThreadsCollect = []
        startTime = time.time()
        # start the network
        target.activateEthernet ()
        outLog += "\n[host]: Pinging target successful!\n"

        for iAttempt in range(2): #send the wrong password once, then the right one
            message = "joy@Work_1999" if (iAttempt==1) else "jediMaster123"
            try:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.settimeout(20) #blocking operations
                clientSocket.connect((target.ipTarget,target.portTarget+iAttempt))
            except:
                outLog += f"\n[host-client-{iAttempt}]: INVALID: Failed to connect to target.\n"
                break
            try:
                TLS_CTX = ssl.SSLContext (ssl.PROTOCOL_TLSv1_2) #create a new context
                TLS_CTX.verify_mode = ssl.CERT_REQUIRED 
                TLS_CTX.load_verify_locations (cafile="{0}/caCert.pem".format(target.certsDir)) #load the CA cert
                TLS_CTX.load_cert_chain(certfile="{0}/clientCert.pem".format(target.certsDir),keyfile="{0}/clientKey.pem".format(target.certsDir))
            except:
                outLog += f"\n[host-client-{iAttempt}]: INVALID: Failed to load the CA certificate into a TLS context.\n"
                break
            try:
                clientSocket = TLS_CTX.wrap_socket(clientSocket,do_handshake_on_connect=True) #wrap the connected socket
                outLog += f"\n[host-client-{iAttempt}]: Socket wrapped successfully!\n"
            except ssl.CertificateError:
                outLog += f"\n[host-client-{iAttempt}]: INVALID: Wrong certificate!\n"
            except socket.timeout:
                outLog += f"\n[host-client-{iAttempt}]: INVALID: Timed-out while trying to wrap the TCP socket.\n"
                break
            except:
                outLog += f"\n[host-client-{iAttempt}]: INVALID: Failed to wrap the TCP socket due to non-CertificateError.\n"
                break    

            try:   
                clientSocket.sendall(message.encode('utf-8'))
            except:
                outLog += f"\n<INVALID> [host-client-{iAttempt}]: Failed to send message to target.\n"
                break
            outLog += target.runCommand("sendToTarget",endsWith="<TARGET-RECV>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=20,shutdownOnError=False)[1]
            try:
                # Look for the response
                ready = select.select([clientSocket], [], [], 10) #10 seconds timeout
                if ready[0]:
                    recvData = str(clientSocket.recv(128),'utf-8')
                    outLog += f"\n[host-client-{iAttempt}]: Received [{len(recvData)} Bytes]:\n<HOST-RECV-{iAttempt}>:{recvData}\n"
                else:
                    raise 
            except:
                outLog += f"\n<INVALID> [host-client-{iAttempt}]: Failed to receive message from target.\n"
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
