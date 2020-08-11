import time
import socket, ssl, select
import threading, sys
import math

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.asymmetric import rsa

def test_301 (target,binTest):
    testNum = 301
    if (binTest != "test_{0}.riscv".format(testNum)):
        target.reportAndExit ("Error in {0}: Calling <test_{2}> for binary <{1}>.".format(target.filename,binTest,testNum))

    outLog = "\n" + '*'*30 + " TEST {0} ".format(testNum) + '*'*30 + "\n\n"
    outLog += "\n<OSIMAGE={0}>\n".format(target.osImage)

    if (target.osImage in ['debian','FreeBSD']):
        outLog += f"<INVALID> test_{testNum} will only be implemented on <{target.osImage}> if specifically asked for."

    elif (target.osImage == 'FreeRTOS'):
        if (target.testsPars['TESTGEN_TEST_PART'] == 1):
            outLog += "-"*20 + "Part01: DH protocol. Diff key-pair." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 2):
            outLog += "-"*20 + "Part02: DH protocol. Same key-pair." + "-"*20 + "\n"
        elif (target.testsPars['TESTGEN_TEST_PART'] == 3):
            outLog += "-"*20 + "Part03: DH-style protocol. Reflection attack." + "-"*20 + "\n"
        else:
            outLog += "\n<INVALID> This test has only three parts! (called with part #{0})\n".format(target.testsPars['TESTGEN_TEST_PART'])
            return outLog

        socketThreadsCollect = []
        startTime = time.time()
        # start the network
        target.activateEthernet ()
        outLog += "\n[host]: Pinging target successful!\n"

        nParallelRequests = 2

        def keyBytesToStr (keyBytes):
            strKey = ''
            for xByte in keyBytes:
                strKey += "%02x"%(xByte)
            return strKey

        #this function is copied from: https://stackoverflow.com/questions/31548753/convert-a-very-large-base-n-number-to-bytes
        def base_n_to_byte_array(digits, from_base):
            """ Converts a base n number to a byte array.
            :param digits: Digits of the number, starting from highest.
            :param from_base: Base in which the number is given.
            """
            x = 0
            n = len(digits)
            for i in range(0, len(digits)):
                x += digits[i] * int(from_base** (n - i - 1))

            min_length = max(math.ceil(math.log(x, 256)), 1)
            byte_array = x.to_bytes(min_length, byteorder='big')
            return byte_array

        def readMoreFromTarget (logDict, iConn):
            goldenString = f"<TARGET-RECV-{iConn}-PUB-KEY>"
            isFound = False
            for line in logDict['target']:
                if (goldenString in line):
                    isFound = True
                    break
            if (not isFound):
                logDict['target'] += target.runCommand("sendToTarget",endsWith=goldenString,erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=20,shutdownOnError=False)[1]


        def connectToTarget (iConn,retSockets,logDict,logLock):
            def returnSocket (iConn,retSockets,xSocket):
                retSockets[iConn] = xSocket
                return

            logDict[iConn] = f"[host-client-{iConn}]: starting connectToTarget...\n"
            
            try:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.settimeout(30) #blocking operations
                clientSocket.connect((target.ipTarget,target.portTarget+iConn))
                logDict[iConn] += f"[host-client-{iConn}]: Connection established.\n"
            except:
                logDict[iConn] += f"\n[host-client-{iConn}]: INVALID: Failed to connect to target.\n"
                returnSocket (iConn,retSockets,clientSocket)
                return

            try:
                #load the DH parameters from the certificate
                xFile = open(f"{target.testsDir}/lib/dhParams.der",'rb')
                inDerDHParams = xFile.read()
                xFile.close()
                dhParams = serialization.load_der_parameters(inDerDHParams, backend=default_backend())
            except:
                logDict[iConn] += f"\n[host-client-{iConn}]: INVALID: Failed to read the DH parameters file.\n"
                returnSocket (iConn,retSockets,clientSocket)
                return

            try:
                # Generate a keyPair for use in the exchange.
                clientKeyPair = dhParams.generate_private_key()
                #convert pub key to bytes to send over the network
                intClientPubKey = clientKeyPair.public_key().public_numbers().y
                messageDer = base_n_to_byte_array([int(c) for c in str(intClientPubKey)],10)
            except:
                logDict[iConn] += f"\n[host-client-{iConn}]: INVALID: Failed to generate a key pair.\n"
                returnSocket (iConn,retSockets,clientSocket)
                return  

            try:   
                logDict[iConn] += f"[host-client-{iConn}]: Sending to target:\n"
                logDict[iConn] += f"<{keyBytesToStr(messageDer)}>:<HOST-GEN-{iConn}-PUB-KEY>\n"
                clientSocket.sendall(messageDer)
            except:
                logDict[iConn] += f"\n<INVALID> [host-client-{iConn}]: Failed to send message to target.\n"
                returnSocket (iConn,retSockets,clientSocket)
                return
            with logLock: #semaphore because this function will be multithreaded
                readMoreFromTarget (logDict,iConn)
            try:
                # Look for the response
                ready = select.select([clientSocket], [], [], 20) #10 seconds timeout
                if ready[0]:
                    recvData = clientSocket.recv(512)
                    logDict[iConn] += f"\n[host-client-{iConn}]: Received [{len(recvData)} Bytes]\n"
                    logDict[iConn] += f"<{keyBytesToStr(recvData)}>:<HOST-RECV-{iConn}-PUB-KEY>\n"
                else:
                    raise 
            except:
                logDict[iConn] += f"\n<INVALID> [host-client-{iConn}]: Failed to receive message from target.\n"
                returnSocket (iConn,retSockets,clientSocket)
                return

            try:
                #convert the received number to DER using a workaround ;)
                intPubKey = int.from_bytes(recvData, byteorder='big')
                serverKeyPub = dh.DHPublicNumbers(intPubKey,dhParams.parameter_numbers()).public_key(default_backend())
            except:
                logDict[iConn] += f"\n<INVALID> [host-client-{iConn}]: Failed to create a DER publicKey from received bytes.\n"
                returnSocket (iConn,retSockets,clientSocket)
                return

            try:
                #generate the shared secret 
                sharedSecret = clientKeyPair.exchange(serverKeyPub) #use peer's public key
                logDict[iConn] += f"<{keyBytesToStr(sharedSecret)}>:<HOST-GEN-{iConn}-SECRET>\n"
            except:
                logDict[iConn] += f"\n<INVALID> [host-client-{iConn}]: Failed to generate the shared secret.\n"
                returnSocket (iConn,retSockets,clientSocket)
                return

            returnSocket (iConn,retSockets,clientSocket)
            return

        def reflectionAttack (clientSockets,logDict):
            def printAndSend (iConn, keyName, xMsg, xSocket,logDict):
                try:   
                    logDict[0] += f"[host-client-{iConn}]: Sending to target:\n"
                    logDict[0] += f"<{keyBytesToStr(xMsg)}>:<{keyName}>\n"
                    xSocket.sendall(xMsg)
                except:
                    logDict[0] += f"\n<INVALID> [host-client-{iConn}]: Failed to send message to target.\n"
                    raise

            def recvAndPrint (iConn, keyName, xSocket,logDict):
                try:
                    ready = select.select([xSocket], [], [], 20) #20 seconds timeout
                    if ready[0]:
                        recvData = xSocket.recv(512)
                        logDict[0] += f"\n[host-client-{iConn}]: Received [{len(recvData)} Bytes]\n"
                        logDict[0] += f"<{keyBytesToStr(recvData)}>:<{keyName}>\n"
                        return recvData
                    else:
                        raise 
                except:
                    logDict[0] += f"\n<INVALID> [host-client-{iConn}]: Failed to receive message from target.\n"
                    raise

            logDict[0] = f"[host-client]: Starting reflectionAttack function...\n"

            for iSocket in range(2): #connects to two sockets
                try:
                    clientSockets[iSocket] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    clientSockets[iSocket].settimeout(30) #blocking operations
                    clientSockets[iSocket].connect((target.ipTarget,target.portTarget+iSocket))
                    logDict[0] += f"[host-client-{iSocket}]: Connection established.\n"
                except:
                    logDict[0] += f"\n[host-client-{iSocket}]: INVALID: Failed to connect to target.\n"
                    return
            try:
                # generate one random number to fake a request. Make first 7-bits zeros to increase the probability it is <p
                randKey = rsa.generate_private_key(public_exponent=3,key_size=1024,backend=default_backend())
                intRandKey = randKey.public_key().public_numbers().n
                intRandKey = (intRandKey%(2**1016)) + 2**1016
                req0 = base_n_to_byte_array([int(c) for c in str(intRandKey)],10)
            except:
                logDict[0] += f"\n[host-client-0]: INVALID: Failed to generate a fake random number.\n"
                return

            #send the req-0 -- random request
            try:
                printAndSend (0,"HOST-GEN-0-CHALLENGE",req0,clientSockets[0],logDict)
            except:
                return

            logDict[0] += target.runCommand("sendToTarget",endsWith=f"<TARGET-RECV-0-CHALLENGE>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=20,shutdownOnError=False)[1]

            #read the resp-0 -- the challenge answer of req-0
            try:
                resp0 = recvAndPrint(0,"HOST-RECV-0-ANSWER",clientSockets[0],logDict) 
            except:
                return

            #read the chal-0
            try:
                chal0 = recvAndPrint(0,"HOST-RECV-0-CHALLENGE",clientSockets[0],logDict) 
            except:
                return

            #send req-1 -- the received challenge (chal-0)
            req1 = chal0
            try:
                printAndSend (1,"HOST-GEN-1-CHALLENGE",req1,clientSockets[1],logDict)
            except:
                return

            logDict[0] += target.runCommand("sendToTarget",endsWith=f"<TARGET-RECV-1-CHALLENGE>",erroneousContents="<INVALID>",onlySearchTheEnd=False,timeout=20,shutdownOnError=False)[1]

            #read the resp-1 -- the challenge answer of req-1 (And should work as ans-0)
            try:
                resp1 = recvAndPrint(1,"HOST-RECV-1-ANSWER",clientSockets[1],logDict) 
            except:
                return

            #read the chal-1 --useless
            try:
                chal1 = recvAndPrint(1,"HOST-RECV-1-CHALLENGE",clientSockets[1],logDict) 
            except:
                return

            #send ans-0 -- responding to chal-0, should equal the answer to req-1
            ans0 = resp1
            try:
                printAndSend (0,"HOST-GEN-0-RESPONSE",ans0,clientSockets[0],logDict)
            except:
                return

            #send ans-1 -- responding to chal-1, just send the same received val -- useless
            ans1 = ans0
            try:
                printAndSend (1,"HOST-GEN-1-RESPONSE",ans1,clientSockets[1],logDict)
            except:
                return
            
            return

        # --- common part --- 
        retSockets = dict()
        logDict = dict()

        # --- diff part --- 
        if (target.testsPars['TESTGEN_TEST_PART'] == 3):
            reflectionAttack(retSockets,logDict)
            for xSocket in retSockets.values():
                socketThreadsCollect.append(target.socketCloseAndCollect(xSocket))

        else: #parts 1 and 2
            connThreads = []
            logLock = threading.Lock()
            logDict['target'] = f"[logDict]: Dumping the UART from target...\n"
            for iConn in range(nParallelRequests):
                retSockets[iConn] = None
                connThread = threading.Thread(target=connectToTarget, args=(iConn,retSockets,logDict,logLock))
                connThread.daemon = True
                target.trash.throwThread(connThread,f"connThread #{iConn} of test-{testNum}")
                connThread.start()
                connThreads.append(connThread)

            for iThread,connThread in enumerate(connThreads):
                connThread.join(timeout=60)
                socketThreadsCollect.append(target.socketCloseAndCollect(retSockets[iThread]))

        # --- common part --- 
        for iConn in range(nParallelRequests):
            if (iConn in logDict):
                outLog += logDict[iConn]
        if (target.testsPars['TESTGEN_TEST_PART'] < 3):
            outLog += logDict['target']
        
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
