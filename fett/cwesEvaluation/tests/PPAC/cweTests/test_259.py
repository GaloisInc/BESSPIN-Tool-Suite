import time
import socket, ssl, select

from fett.base.utils.misc import *

def test_259 (target,binTest):
    testNum = 259
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage in ['debian','FreeBSD']):
        outLog += f"<INVALID> test_{testNum} is covered by TEST-257 for <{target.osImage}>."

    elif (target.osImage == 'FreeRTOS'):
        if (target.testPart == 1):
            outLog += "-"*20 + "Part01: Inbound test." + "-"*20 + "\n"
        elif (target.testPart == 2):
            outLog += "-"*20 + "Part02: Outbound test." + "-"*20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only three parts! (called with part #{0})\n".format(target.testPart)
            return outLog

        socketThreadsCollect = []
        startTime = time.time()
        # start the network
        target.activateEthernet ()
        outLog += "\n[host]: Pinging target successful!\n"

        if (target.testPart == 1):

            for iAttempt in range(2): #send the wrong password once, then the right one
                if (iAttempt == 0):
                    message = "jediMaster123"
                    clientSuffix = '2'
                else:
                    message = "joy@Work_1999"
                    clientSuffix = ''
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
                    TLS_CTX.load_verify_locations (cafile=f"{target.certsDir}/caCert.pem") #load the CA cert
                    TLS_CTX.load_cert_chain(certfile=f"{target.certsDir}/client{clientSuffix}Cert.pem",keyfile=f"{target.certsDir}/client{clientSuffix}Key.pem")
                except:
                    outLog += f"\n[host-client-{iAttempt}]: INVALID: Failed to load the CA certificate into a TLS context.\n"
                    break
                try:
                    clientSocket = TLS_CTX.wrap_socket(clientSocket,do_handshake_on_connect=True) #wrap the connected socket
                    outLog += f"\n[host-client-{iAttempt}]: Socket wrapped successfully!\n"
                except ssl.CertificateError:
                    outLog += f"\n[host-client-{iAttempt}]: INVALID: Wrong certificate!\n"
                    break
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
                outLog += target.runCommand("sendToTarget",endsWith="<TARGET-RECV>",erroneousContents="<INVALID>",timeout=20,shutdownOnError=False)[1]
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

        else: #PART02
            for i in range(1): #only once -- easier construct to break
                try:
                    #open the server socket
                    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    serverSocket.bind((target.ipHost,target.portHost)) # 3 subparts in P01
                    serverSocket.settimeout(30) #blocking operations
                    serverSocket.listen(5) #backlog is 5
                    outLog += "\n[host-server]: Listening...\n"
                except:
                    outLog += "\n<INVALID> [host-server]: Failed to create a socket.\n"
                    break

                try:
                    connectedSocket, clientAddress = serverSocket.accept()
                    connectedSocket.settimeout(25) #blocking operations -- need a large value for the TLS protocol
                    outLog += "[host-server]: Accepted connection!\n"
                except socket.timeout:
                    outLog += "\n[host-server]: INVALID: Failed to accept a connection. (TIMEOUT)\n"
                    break
                except:
                    outLog += "\n[host-server]: INVALID: Failed to accept a connection. (Unknown error)\n"
                    break

                retTLS = target.runCommand("waitForTLSReady",endsWith="<TLS-READY>",erroneousContents="<INVALID>",timeout=20,shutdownOnError=False)
                outLog += retTLS[1]
                if ((not retTLS[0]) or retTLS[2]): #bad
                    outLog += "\n[host-server]: INVALID: Failed to detect <TLS-READY>.\n"
                    break

                try:
                    TLS_CTX = ssl.SSLContext (ssl.PROTOCOL_TLSv1_2) #create a new context
                    TLS_CTX.load_verify_locations (cafile="{0}/caCert.pem".format(target.certsDir)) #load the CA cert
                    TLS_CTX.load_cert_chain(certfile="{0}/serverCert.pem".format(target.certsDir),keyfile="{0}/serverKey.pem".format(target.certsDir))
                except:
                    outLog += "\n[host-server]: INVALID: Failed to load the CA certificate into a TLS context.\n"
                    break

                try:
                    connectedSocket = TLS_CTX.wrap_socket(connectedSocket, server_side=True ,do_handshake_on_connect=True) #wrap the connected socket
                    outLog += "\n[host-server]: Socket wrapped successfully!\n"
                except ssl.SSLEOFError:
                    outLog += "\n[host-server]: DENIED: Wrong certificate!\n"
                    break
                except socket.timeout:
                    outLog += "\n[host-server]: INVALID: Timed-out while trying to wrap the TCP socket.\n"
                    break
                except:
                    outLog += "\n[host-server]: INVALID: Failed to wrap the TCP socket due to non-SSLEOFError.\n"
                    break

                try:   
                    message = "SEND LOGIN CREDENTIALS"
                    connectedSocket.sendall(message.encode('utf-8'))
                except:
                    outLog += "\n[host-server]: INVALID: Failed to send message to target.\n"
                    break
                retSend = target.runCommand("sendToTarget",endsWith="<TARGET-RECV>",erroneousContents="<INVALID>",timeout=10,shutdownOnError=False)
                outLog += retSend[1]
                if ((not retSend[0]) or retSend[2]): #bad
                    outLog += "<INVALID> [host-server]: Failed to send message to target.\n"
                    break
                try:
                    recvData = str(connectedSocket.recv(128),'utf-8')
                    outLog += "\n[host-server]: Received [{0} Bytes]:\n<HOST-RECV>:{1}\n".format(len(recvData),recvData)
                except:
                    outLog += "\n[host-server]: INVALID: Failed to receive message from target.\n"
                    break

                socketThreadsCollect.append(target.socketCloseAndCollect(connectedSocket)) 
                socketThreadsCollect.append(target.socketCloseAndCollect(serverSocket))
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
