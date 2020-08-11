import time
import socket, ssl, select
import pexpect

def test_307 (target,binTest):
    testNum = 307
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))
    nAttempts = target.testsPars['nAllowedAuthAttempts']

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage == 'debian'):
        def OnlyAuthForNofAttempts (actualNAttempts,intraCommand=None):
            retLog = ''
            retCommand = [True, retLog, False]
            iAttempt = 0
            while (retCommand[0]) and (not retCommand[2]) and (iAttempt < actualNAttempts):
                retCommand = target.runCommand("./{0}".format(binTest),expectedContents='PAM started',endsWith="Password:",shutdownOnError=False,timeout=20)
                retLog += retCommand[1]
                if ( (not retCommand[0]) or (retCommand[2]) ): #Bad
                    return retLog
                elif (iAttempt == actualNAttempts-1): #this is it, send correct password
                    retCommand = target.runCommand(target.userPassword,shutdownOnError=False,timeout=20)
                    if (retCommand[2] and (target.settings['processor'] == 'bluespec_p3')): #timeout on bluespec_p3
                        retCommand[1] += target.keyboardInterrupt (shutdownOnError=False)
                        retCommand[1] += "\n<DENIED> Failed to authenticate. (pam timed-out)\n"
                else:
                    retCommand = target.runCommand("x",expectedContents='Failed to authenticate',suppressErrors=True,shutdownOnError=False,timeout=20)
                    if (retCommand[2] and (target.settings['processor'] == 'bluespec_p3')): #timeout on bluespec_p3
                        retCommand[1] += target.keyboardInterrupt (shutdownOnError=False)
                        #reset the errors
                        retCommand[0] = True
                        retCommand[2] = False
                retLog += retCommand[1]
                iAttempt += 1
                if (intraCommand is not None):
                    retLog += target.runCommand (intraCommand,shutdownOnError=False)[1]
            return retLog

        #For each part, the result should be Granted, Granted, Denied
        outLog += "-"*20 + "Part01: PAM with no tally" + "-"*20 + "\n"
        outLog += "\n<authForNofAttempts(1)>\n"
        outLog += OnlyAuthForNofAttempts(1)
        outLog += "\n<authForNofAttempts(N)>\n"
        outLog += OnlyAuthForNofAttempts(nAttempts)
        outLog += "\n<authForNofAttempts(N+1)>\n"
        outLog += OnlyAuthForNofAttempts(nAttempts+1)
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part02: PAM with tally on non-existing file" + "-"*20 + "\n"
        uncommentTally = "sed -i \"s/#//\" /etc/pam.d/pam_307"
        configureNAttempts = "sed -i \"s/&n&/{0}/\" /etc/pam.d/pam_307".format(nAttempts)
        target.executeOnRoot ([uncommentTally, configureNAttempts])
        outLog += "\n<authForNofAttempts(1)>\n"
        outLog += OnlyAuthForNofAttempts(1)
        outLog += "\n<authForNofAttempts(N)>\n"
        outLog += OnlyAuthForNofAttempts(nAttempts)
        outLog += "\n<authForNofAttempts(N+1)>\n"
        outLog += OnlyAuthForNofAttempts(nAttempts+1)
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        outLog += "-"*20 + "Part03: PAM w/ correct and working tally" + "-"*20 + "\n"
        #making the tally file accessible
        target.executeOnRoot(["touch /var/log/tallylog", "chown {0} /var/log/tallylog".format(target.userName)]) 
        outLog += "\n<authForNofAttempts(1)>\n"
        outLog += OnlyAuthForNofAttempts(1)
        target.executeOnRoot(["pam_tally2 -r -u {0}".format(target.userName)])
        outLog += "\n<authForNofAttempts(N)>\n"
        outLog += OnlyAuthForNofAttempts(nAttempts)
        target.executeOnRoot(["pam_tally2 -r -u {0}".format(target.userName)])
        outLog += "\n<authForNofAttempts(N+1)>\n"
        outLog += OnlyAuthForNofAttempts(nAttempts+1)
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        cleanP03 = ["pam_tally2 -r -u {0}".format(target.userName), "rm /var/log/tallylog"]
        prepareP04 = ["sed -i \"s:.so:.so    file=/home/{0}/localLog:\" /etc/pam.d/pam_307".format(target.userName)]
        target.executeOnRoot (cleanP03 + prepareP04)

        outLog += "-"*20 + "Part04: PAM w/ local file and delete it" + "-"*20 + "\n"
        outLog += "\n<authForNofAttempts(1)>\n"
        outLog += OnlyAuthForNofAttempts(1,intraCommand="rm localLog")
        outLog += "\n<authForNofAttempts(N)>\n"
        outLog += OnlyAuthForNofAttempts(nAttempts,intraCommand="rm localLog")
        outLog += "\n<authForNofAttempts(N+1)>\n"
        outLog += OnlyAuthForNofAttempts(nAttempts+1,intraCommand="rm localLog")
        if (target.settings['useCustomScoring']): #will need the gdb output here
            outLog += target.getGdbOutput()
        outLog += "-"*60 + "\n\n\n"

        time.sleep (1)

    elif (target.osImage == 'FreeBSD'):
        if (target.backend == 'qemu'):
            outLog += f"<QEMU-N/A> test_{testNum} is not yet implemented on <qemu>."
            return outLog
        elif (not target.targetObj.isSshConn):
            if (not target.openSshConn()):
                outLog += f"<INVALID> Failed to open an SSH connection for test_{testNum}."
                return outLog
        timeout = 120
        target.switchUser () #this test is executed on ROOT

        def authAtNp1thAttempt ():
            retLog = f"Authenticating at the (N+1)th attempt ...\n"
            sshCommand = f"ssh {target.userName}@{target.settings['FPGANTK_IP_TARGET']}"

            def terminate (sshProcess):
                if (sshProcess is not None):
                    try:
                        sshProcess.terminate(force=True)
                    except:
                        retLog += f"Failed to force terminate the process.\n"

            def getText (sshProcess):
                try:
                    return str(sshProcess.before,'utf-8')
                except:
                    return "--- NO-TEXT ---\n"

            def sendCommand (sshProcess, command):
                try:
                    sshProcess.sendline(command)
                except:
                    retLog += f"Failed to send <{command}>\n"
                    terminate(sshProcess)
            
            try:
                sshProcess = pexpect.spawn(sshCommand,timeout=timeout)
                retExpect = sshProcess.expect([f"Password for {target.userName}@[\w\-\.]+\:",f"{target.userName}@[\w\-\.]+\'s password\:",'Too many authentication failures','Permission denied (publickey,keyboard-interactive).\r\r\n'])
            except Exception as e:
                if (type(e) == pexpect.TIMEOUT):
                    retLog += "<INVALID> Timed-out while opening an SSH connection.\n"
                elif (type(e) == pexpect.EOF):
                    retLog += "<INVALID> SSH process terminated unexpectedly while spwaning.\n"
                else:
                    retLog += "<INVALID> Encountered an unrecognized error while opening an SSH connection.\n"
                return retLog

            iAttempt = 0
            retLog += "SSH process spawned successfully.\n"
            while (iAttempt <= nAttempts+1):
                retLog += f"<iAttempt={iAttempt} --- retExpect={retExpect}>\n"
                if (retExpect in [0,1]): #asking for password
                    retLog += "<ASK-PASSWORD>\n"
                    if (iAttempt == nAttempts): #send the correct password
                        sendCommand(sshProcess,target.userPassword)
                    else: #send a wrong password
                        sendCommand(sshProcess,'x')
                    try:
                        retExpect = sshProcess.expect([f"Password for {target.userName}@[\w\-\.]+\:",f"{target.userName}@[\w\-\.]+\'s password\:",'Too many authentication failures','Permission denied (publickey,keyboard-interactive).\r\r\n',":~ \$"])
                    except Exception as e:
                        if (type(e) in [pexpect.TIMEOUT, pexpect.EOF]):
                            retLog += f"<INVALID> -- {type(e)}"
                        else:
                            retLog += f"<INVALID> -- <UNKNOWN-EXCEPTION>"
                        break

                elif (retExpect in [2,3]): #authentication failure
                    retLog += "<DENIED>\n"
                    break
                elif (retExpect == 4): #logged in
                    retLog += "<GRANTED>\n"
                    sendCommand(sshProcess,"exit")
                else: #that's weird or '-1'
                    retLog += "<INVALID>\n"
                    break

                iAttempt += 1

            retLog += getText(sshProcess)
            terminate(sshProcess)
            return retLog

        partNames = ['MaxAuthTries --> N+1.', 'MaxAuthTries --> 32.']
        maxAuthTries = [nAttempts+1, 32]
        
        for iPart in range(2):
            outLog += "-" * 20 + f"Part0{iPart+1}: {partNames[iPart]}" + "-" * 20 + "\n"
            if (iPart == 0): #backup config
                outLog += target.runCommand ("cp /etc/ssh/sshd_config /root/",shutdownOnError=False)[1]
            else: #reset config
                outLog += target.runCommand ("cp /root/sshd_config /etc/ssh/sshd_config",shutdownOnError=False)[1]
            #apply ssh config
            outLog += target.runCommand (f"echo \"PasswordAuthentication yes\" >> /etc/ssh/sshd_config",shutdownOnError=False)[1]
            outLog += target.runCommand (f"echo \"MaxAuthTries {maxAuthTries[iPart]}\" >> /etc/ssh/sshd_config",shutdownOnError=False)[1]
            outLog += target.runCommand ("service sshd restart",shutdownOnError=False)[1]
            time.sleep(30)
            #try to authenticate
            outLog += authAtNp1thAttempt ()

            outLog += "-"*60 + "\n\n\n"

        target.switchUser () #Go back to user

    elif (target.osImage == 'FreeRTOS'):
        socketThreadsCollect = []
        startTime = time.time()
        # start the network
        target.activateEthernet ()
        outLog += "\n[host]: Pinging target successful!\n"

        if (target.testsPars['TESTGEN_TEST_PART'] == 1):
            # ------------- PART-01 -------------------------
            def clientAuthForNofAttempts (iSubPart, actualNAttempts):
                retLog = ''
                iAttempt = 0
                isGranted = False
                clientSocket = None
                while (iAttempt < actualNAttempts):
                    certSuffix = '' if (iAttempt == actualNAttempts-1) else 'SSITH' #use correct Cert at actualNAttempts
                    try:
                        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        clientSocket.settimeout(60) #blocking operations
                        clientSocket.connect((target.ipTarget,target.portTarget+iSubPart))
                        time.sleep(1)
                    except:
                        retLog += f"\n[host-client-{iSubPart}.{iAttempt}]: INVALID: Failed to create a socket <connecting to{target.portTarget+iSubPart}>.\n"
                        return [retLog, 'INVALID', None]
                    try:
                        TLS_CTX = ssl.SSLContext (ssl.PROTOCOL_TLSv1_2) #create a new context
                        TLS_CTX.verify_mode = ssl.CERT_REQUIRED 
                        TLS_CTX.load_verify_locations (cafile="{0}/caCert{1}.pem".format(target.certsDir,certSuffix)) #load the CA cert
                        TLS_CTX.load_cert_chain(certfile="{0}/clientCert{1}.pem".format(target.certsDir,certSuffix),keyfile="{0}/clientKey{1}.pem".format(target.certsDir,certSuffix))
                    except:
                        retLog += "\n[host-client-{0}.{1}]: INVALID: Failed to load the CA certificate into a TLS context.\n".format(iSubPart,iAttempt)
                        return [retLog, 'INVALID', None]
                    try:
                        clientSocket = TLS_CTX.wrap_socket(clientSocket,do_handshake_on_connect=True) #wrap the connected socket
                        isGranted = True
                        retLog += "\n[host-client-{0}.{1}]: GRANTED: Socket wrapped successfully!\n".format(iSubPart,iAttempt)
                        break
                    except ssl.CertificateError:
                        retLog += "\n[host-client-{0}.{1}]: DENIED: Wrong certificate!\n".format(iSubPart,iAttempt)
                    except socket.timeout:
                        retLog += "\n[host-client-{0}.{1}]: INVALID: Timed-out while trying to wrap the TCP socket.\n".format(iSubPart,iAttempt)
                        return [retLog, 'INVALID', None]
                    except:
                        retLog += "\n[host-client-{0}.{1}]: INVALID: Failed to wrap the TCP socket due to non-CertificateError.\n".format(iSubPart,iAttempt)
                        return [retLog, 'INVALID', None]
                    socketThreadsCollect.append(target.socketCloseAndCollect(clientSocket))
                    del TLS_CTX
                    iAttempt += 1    
                    #do not put time here 
                return [retLog, isGranted, clientSocket]

            for iSubPart, nOfSubPart in enumerate([1, nAttempts, nAttempts+1]):
                message = "TESTGEN-307-P01.{0}".format(iSubPart)
                #to enhance the control flow
                outLog += target.runCommand("waitForTCPReady",endsWith="<TCP-READY>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=15,shutdownOnError=False)[1]
                retAuthAttempts = clientAuthForNofAttempts (iSubPart, nOfSubPart)
                outLog += retAuthAttempts[0]
                if ((retAuthAttempts[1] == 'INVALID') or (retAuthAttempts[2] is None)):
                    outLog += "\n<INVALID> [host-client-{0}]: Failed to establish connection with target.\n".format(iSubPart)
                    break
                elif (retAuthAttempts[1]): #only proceed with sending if granted
                    try:   
                        clientSocket = retAuthAttempts[2]
                        clientSocket.sendall(message.encode('utf-8'))
                    except:
                        outLog += "\n<INVALID> [host-client-{0}]: Failed to send message to target.\n".format(iSubPart)
                        break
                    outLog += target.runCommand("sendToTarget",endsWith="<TARGET-RECV>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=20,shutdownOnError=False)[1]
                else: #DENIED
                    outLog += "\n[host-client-{0}]: DENIED: Failed to connect!\n".format(iSubPart)
                    continue
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
                time.sleep(3)

        elif (target.testsPars['TESTGEN_TEST_PART'] == 2):
            # ------------- PART-02 -------------------------
            def serverAuthForNofAttempts (serverSocket, iSubPart):
                retLog = ''
                iAttempt = 0
                isGranted = False
                connectedSocket = None
                while ((iAttempt < nAttempts+1) and (not isGranted)): #allow one more
                    try:
                        connectedSocket, clientAddress = serverSocket.accept()
                        connectedSocket.settimeout(90) #blocking operations -- need a large value for the TLS protocol
                        retLog += "[host-server-{0}.{1}]: Accepted connection!\n".format(iSubPart,iAttempt)
                    except socket.timeout:
                        retLog += "\n[host-server-{0}.{1}]: INVALID: Failed to accept a connection. (TIMEOUT)\n".format(iSubPart,iAttempt)
                        return [retLog, 'INVALID']
                    except:
                        retLog += "\n[host-server-{0}.{1}]: INVALID: Failed to accept a connection. (Unknown error)\n".format(iSubPart,iAttempt)
                        return [retLog, 'INVALID']

                    retTLS = target.runCommand("waitForTLSReady",endsWith="<TLS-READY>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=20,shutdownOnError=False)
                    retLog += retTLS[1]
                    if ((not retTLS[0]) or retTLS[2]): #bad
                        retLog += "\n[host-server-{0}.{1}]: INVALID: Failed to detect <TLS-READY>.\n".format(iSubPart,iAttempt)
                        return [retLog, 'INVALID']
                    try:
                        TLS_CTX = ssl.SSLContext (ssl.PROTOCOL_TLSv1_2) #create a new context
                        TLS_CTX.load_verify_locations (cafile="{0}/caCert.pem".format(target.certsDir)) #load the CA cert
                        TLS_CTX.load_cert_chain(certfile="{0}/serverCert.pem".format(target.certsDir),keyfile="{0}/serverKey.pem".format(target.certsDir))
                    except:
                        retLog += "\n[host-server-{0}.{1}]: INVALID: Failed to load the CA certificate into a TLS context.\n".format(iSubPart,iAttempt)
                        return [retLog, 'INVALID']
                    
                    try:
                        connectedSocket = TLS_CTX.wrap_socket(connectedSocket, server_side=True ,do_handshake_on_connect=True) #wrap the connected socket
                        retLog += "\n[host-server-{0}.{1}]: Socket wrapped successfully!\n".format(iSubPart,iAttempt)
                        isGranted = True
                    except ssl.SSLEOFError:
                        retLog += "\n[host-server-{0}.{1}]: DENIED: Wrong certificate!\n".format(iSubPart,iAttempt)
                    except socket.timeout:
                        retLog += "\n[host-server-{0}.{1}]: INVALID: Timed-out while trying to wrap the TCP socket.\n".format(iSubPart,iAttempt)
                        return [retLog, 'INVALID']
                    except:
                        retLog += "\n[host-server-{0}.{1}]: INVALID: Failed to wrap the TCP socket due to non-SSLEOFError.\n".format(iSubPart,iAttempt)
                        return [retLog, 'INVALID']

                    if (isGranted):
                        try:   
                            message = "TESTGEN-307-P02.{0}".format(iSubPart)
                            connectedSocket.sendall(message.encode('utf-8'))
                        except:
                            retLog += "\n[host-server-{0}.{1}]: INVALID: Failed to send message to target.\n".format(iSubPart,iAttempt)
                            return [retLog, 'INVALID']
                        retSend = target.runCommand("sendToTarget",endsWith="<TARGET-RECV>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=10,shutdownOnError=False)
                        retLog += retSend[1]
                        if ((not retSend[0]) or retSend[2]): #bad
                            retLog += "<INVALID> [host-server-{0}.{1}]: Failed to send message to target.\n".format(iSubPart,iAttempt)
                            return [retLog, 'INVALID']
                        try:
                            recvData = str(connectedSocket.recv(128),'utf-8')
                            retLog += "\n[host-server-{2}.{3}]: Received [{0} Bytes]:\n<HOST-RECV>:{1}\n".format(len(recvData),recvData,iSubPart,iAttempt)
                        except:
                            retLog += "\n[host-server-{0}.{1}]: INVALID: Failed to receive message from target.\n".format(iSubPart,iAttempt)
                            return [retLog, 'INVALID']
                    socketThreadsCollect.append(target.socketCloseAndCollect(connectedSocket))
                    del TLS_CTX  
                    iAttempt += 1    
                return [retLog, isGranted]

            for iSubPart, nOfSubPart in enumerate([1, nAttempts, nAttempts+1]):
                try:
                    #open the server socket
                    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    serverSocket.bind((target.ipHost,target.portHost+iSubPart+3)) # 3 subparts in P01
                    serverSocket.settimeout(30) #blocking operations
                    serverSocket.listen(5) #backlog is 5
                    outLog += f"\n[host-server-{iSubPart}]: Listening <on {target.portHost+iSubPart+3}>...\n"
                except:
                    outLog += f"\n<INVALID> [host-server-{iSubPart}]: Failed to create a socket <port {target.portHost+iSubPart+3}>.\n"
                    break

                retAuthAttempts = serverAuthForNofAttempts (serverSocket, iSubPart)
                outLog += retAuthAttempts[0]
                if (retAuthAttempts[1] == 'INVALID'):
                    outLog += target.runCommand("getTargetDump",endsWith=">>>End of Fett<<<",onlySearchTheEnd=False,timeout=10,shutdownOnError=False)[1]
                    outLog += "\n<INVALID> [host-server-{0}]: Failed to establish connection with target.\n".format(iSubPart)
                    break
                
                socketThreadsCollect.append(target.socketCloseAndCollect(serverSocket))
                
        else:
            outLog += "\n<INVALID> This test has only two parts! (called with part #{0})\n".format(target.testsPars['TESTGEN_TEST_PART'])
            return outLog

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