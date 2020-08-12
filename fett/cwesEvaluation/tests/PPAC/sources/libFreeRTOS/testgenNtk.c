/*
Functions used for Network implementation on FreeRTOS
*/

#include "testgenFreeRTOS.h"

// Declarations
void vStartNetwork (void *pvParameters);
void vServerSocketTCP (void *pvParameters);
static void vCommunicateTCP (void *pvParameters);
void vClientSocketTCP (void *pvParameters);
static uint8_t isNetworkUp = uFALSE; //To know whether the network was up before
static TaskHandle_t xTaskStartNtk = NULL;

/* The default IP and MAC address used by the demo.  The address configuration defined here will be used if ipconfigUSE_DHCP is 0, or if ipconfigUSE_DHCP is
1 but a DHCP server could not be contacted.  See the online documentation for more information. */
static const uint8_t ucIPAddress[4] = {configIP_ADDR0, configIP_ADDR1, configIP_ADDR2, configIP_ADDR3};
static const uint8_t ucNetMask[4] = {configNET_MASK0, configNET_MASK1, configNET_MASK2, configNET_MASK3};
static const uint8_t ucGatewayAddress[4] = {configGATEWAY_ADDR0, configGATEWAY_ADDR1, configGATEWAY_ADDR2, configGATEWAY_ADDR3};
static const uint8_t ucDNSServerAddress[4] = {configDNS_SERVER_ADDR0, configDNS_SERVER_ADDR1, configDNS_SERVER_ADDR2, configDNS_SERVER_ADDR3};
/* Default MAC address configuration.  The demo creates a virtual network connection that uses this MAC address by accessing the raw Ethernet data
to and from a real network connection on the host PC.  See the configNETWORK_INTERFACE_TO_USE definition for information on how to configure
the real network connection to use. */
const uint8_t ucMACAddress[6] = {configMAC_ADDR0, configMAC_ADDR1, configMAC_ADDR2, configMAC_ADDR3, configMAC_ADDR4, configMAC_ADDR5};

#define configSOCKET_LISTEN_TCP_TX_WINDOW_SIZE 2
#define configSOCKET_LISTEN_TCP_RX_WINDOW_SIZE 2

//This task initializes the network and notify the mainTask
void vStartNetwork (void *pvParameters) {
    (void)pvParameters;
    BaseType_t funcReturn;
    xTaskStartNtk = xTaskGetCurrentTaskHandle();

    funcReturn = FreeRTOS_IPInit(ucIPAddress, ucNetMask, ucGatewayAddress, ucDNSServerAddress, ucMACAddress);
    if (funcReturn != pdPASS) {
        onPrintf ("<INVALID> [startNetwork]: Failed to initialize network. [ret=%d].\n",funcReturn);
        vEXIT(1);
    } else {
        onPrintf (">>> Network IP initialized successfully!.\n");
    }

    //wait for NtkHook
    uint32_t recvNotification = NOTIFY_FAIL;
    funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
    if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
        onPrintf ("<INVALID> [startNetwork]: Failed to start network. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
        vEXIT(1);
    }

    onPrintf ("\n<NTK-READY>\n");
    vTaskDelay(pdMS_TO_TICKS(3000)); //give time to the host to ping

    //notify main
    if (xMainTask == NULL) {
        onPrintf ("<INVALID> [startNetwork]: Unable to get the handle of <main:task>.\n");
        vEXIT(1);
    }
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
    if (funcReturn != pdPASS) {
        onPrintf ("<INVALID> [startNetwork]: Failed to notify <main:task>!\n");
        vEXIT(1);
    }

    vTaskDelete (NULL);
} //vStartNetwork

/* Called by FreeRTOS+TCP when the network connects or disconnects.  Disconnect
events are only received if implemented in the MAC driver. */
void vApplicationIPNetworkEventHook(eIPCallbackEvent_t eNetworkEvent) {
    onPrintf (">>> [NtkHook]: A network event has been detected! (eventNum=%d).\n",eNetworkEvent);
    
    /* If the network has just come up...*/
    if ((eNetworkEvent == eNetworkUp) && (isNetworkUp == uFALSE)) //Network never was up
    {
        onPrintf (">>> Network is up!\n");
        char cBuffer[16];
        uint32_t ulIPAddress, ulNetMask, ulGatewayAddress, ulDNSServerAddress;
        /* Print out the network configuration, which may have come from a DHCP
        server. */
        FreeRTOS_GetAddressConfiguration(&ulIPAddress, &ulNetMask, &ulGatewayAddress, &ulDNSServerAddress);
        FreeRTOS_inet_ntoa(ulIPAddress, cBuffer);
        onPrintf("\t\tIP Address: %s\n", cBuffer);

        FreeRTOS_inet_ntoa(ulNetMask, cBuffer);
        onPrintf("\t\tSubnet Mask: %s\n", cBuffer);

        FreeRTOS_inet_ntoa(ulGatewayAddress, cBuffer);
        onPrintf("\t\tGateway Address: %s\n", cBuffer);

        FreeRTOS_inet_ntoa(ulDNSServerAddress, cBuffer);
        onPrintf("\t\tDNS Server Address: %s\n\n", cBuffer);

        //Notify start netowork
        BaseType_t funcReturn;
        if (xTaskStartNtk == NULL) {
            onPrintf ("<INVALID> [NtkHook]: Unable to get the handle of <task:startNetwork>.");
            exitTest (1);
        } else {
            funcReturn = xTaskNotify( xTaskStartNtk, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [NtkHook]: Failed to notify <task:startNetwork>!\n");
                exitTest (1);
            }
        }
        isNetworkUp = uTRUE;
    } //network has just come up

    // HERE DETECTS IF THE NETWORK WENT DOWN 
    if (eNetworkEvent == eNetworkDown) {
        onPrintf ("<INVALID> [NtkHook]: Network is Down!\n");
        exitTest (1);
    }
} //vApplicationIPNetworkEventHook

//This task opens a listening TCP server socket
void vServerSocketTCP (void *pvParameters) {
    BaseType_t funcReturn;
    uint8_t * iPart = (uint8_t *) pvParameters;
    uint8_t iSubPart = iPart[0];

    /* Attempt to open the socket. */
    Socket_t xListeningSocket = FreeRTOS_socket (FREERTOS_AF_INET, FREERTOS_SOCK_STREAM, FREERTOS_IPPROTO_TCP);
    if (xListeningSocket == FREERTOS_INVALID_SOCKET) {
        onPrintf ("<INVALID> [serverSocketTCP-%d]: Failed to open the socket.\n",iSubPart);
        vEXIT(1);
    } else {
        onPrintf ("\t[%d]>>>>>> Socket opened!\n",iSubPart);
    }

    /* Set a time out so accept() will just wait for a connection. */
    const TickType_t xReceiveTimeOut = portMAX_DELAY;
    funcReturn = FreeRTOS_setsockopt(xListeningSocket, 0, FREERTOS_SO_RCVTIMEO, &xReceiveTimeOut, sizeof(xReceiveTimeOut));
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [serverSocketTCP-%d]: Failed to setsockopt <FREERTOS_SO_RCVTIMEO>. [ret=%d].\n",iSubPart,funcReturn);
        vEXIT(1);
    }

    /* Set the window and buffer sizes that will be used by the socket. */
    WinProperties_t xWinProps;
    xWinProps.lTxBufSize = ipconfigTCP_TX_BUFFER_LENGTH;
    xWinProps.lTxWinSize = configSOCKET_LISTEN_TCP_TX_WINDOW_SIZE;
    xWinProps.lRxBufSize = ipconfigTCP_RX_BUFFER_LENGTH;
    xWinProps.lRxWinSize = configSOCKET_LISTEN_TCP_RX_WINDOW_SIZE;
    funcReturn = FreeRTOS_setsockopt(xListeningSocket, 0, FREERTOS_SO_WIN_PROPERTIES, (void *)&xWinProps, sizeof(xWinProps));
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [serverSocketTCP-%d]: Failed to setsockopt <FREERTOS_SO_WIN_PROPERTIES>. [ret=%d].\n",iSubPart,funcReturn);
        vEXIT(1);
    }

    /* Bind the socket to the port that the client task will send to */ 
    struct freertos_sockaddr xBindAddr;
    xBindAddr.sin_port = FreeRTOS_htons(TCP_PORT_NUMBER+iPart[0]+iPart[1]); // + offset
    funcReturn = FreeRTOS_bind(xListeningSocket, &xBindAddr, sizeof(xBindAddr));
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [serverSocketTCP-%d]: Failed to bind the socket to the port number <%d>. [ret=%d].\n",iSubPart,TCP_PORT_NUMBER+iPart[0]+iPart[1],funcReturn);
        vEXIT(1);
    } else {
        onPrintf ("\t[%d]>>>>>> Socket bound to port <%d>!\n",iSubPart,TCP_PORT_NUMBER+iPart[0]+iPart[1]);
    }

    /* listen for incoming connections. */
    const BaseType_t xBacklog = 5; //Number of allowed connections to that port
    funcReturn = FreeRTOS_listen(xListeningSocket, xBacklog);
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [serverSocketTCP-%d]: Failed to put the port in listening state. [ret=%d].\n",iSubPart,funcReturn);
        vEXIT(1);
    } else {
        onPrintf ("\t[%d]>>>>>> Socket is listening...\n",iSubPart);
    }

    /* Store the info in a struct to pass it to child task */
    struct testgen_parentSocket *xSocketInfo = pvPortMalloc (sizeof(struct testgen_parentSocket));
    if (xSocketInfo == NULL) {
        onPrintf ("<INVALID> [serverSocketTCP-%d]: Malloc error while allocating <xSocketInfo>.\n",iSubPart);
        vEXIT(1);
    }
    xSocketInfo->xConnectedSocket = NULL;
    xSocketInfo->xTaskParent = xTaskGetCurrentTaskHandle();
    xSocketInfo->iPart[0] = iSubPart;
    xSocketInfo->isServer = uTRUE;

    //notify main that the listening socket is open
    if (xMainTask == NULL) {
        onPrintf ("<INVALID> [serverSocketTCP-%d]: Unable to get the handle of <main:task>.\n",iSubPart);
        vEXIT(1);
    }
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
    if (funcReturn != pdPASS) {
        onPrintf ("<INVALID> [serverSocketTCP-%d]: Failed to notify <main:task>!\n",iSubPart);
        vEXIT(1);
    }

    // ------- wait for incoming connection
    struct freertos_sockaddr xClientAddr;
    socklen_t xClientSize = sizeof(xClientAddr);

    #ifdef nConnAttemptsTLS
        uint8_t nConnAttempts = nConnAttemptsTLS;
    #else
        uint8_t nConnAttempts = 0;
    #endif

    uint8_t iAttempt=0;
    uint32_t recvNotification = NOTIFY_FAIL;
    do {
        /* Wait for a client to connect. */
        xSocketInfo->xConnectedSocket = FreeRTOS_accept(xListeningSocket, &xClientAddr, &xClientSize);
        if (xSocketInfo->xConnectedSocket == NULL) {
            onPrintf ("<INVALID> [serverSocketTCP-%d.%d]: Timeout on the listening socket.\n",iSubPart,iAttempt);
            vEXIT(1);
        }
        else if (xSocketInfo->xConnectedSocket == FREERTOS_INVALID_SOCKET) {
            onPrintf ("<INVALID> [serverSocketTCP-%d.%d]: Invalid socket is trying to connect.\n",iSubPart,iAttempt);
            vEXIT(1);
        } else {
            onPrintf ("[%d.%d]>>> [serverSocketTCP]: Accepted Client Connection!\n",iSubPart,iAttempt);
        }

        #ifdef doFETCH_CLIENT_IP
            char ipName[IP_NAME_SIZE];
            FreeRTOS_inet_ntoa( xClientAddr.sin_addr, ipName );
            onPrintf("[%d.%d]>>> [serverSocketTCP]: IP address of incoming connection is: <%s>\n",iSubPart,iAttempt,ipName);
            funcReturn = sendToMsgBuffer ((void *) ipName, strlen(ipName));
            if (funcReturn == uTRUE) {
                onPrintf ("[%d.%d]>>> [serverSocketTCP]: Received message sent to msgBuf.\n",iSubPart,iAttempt);
            } else {
                onPrintf ("<INVALID> [serverSocketTCP-%d.%d]: Failed to send received message to msgBuf.\n",iSubPart,iAttempt);
                vEXIT(1);
            }
        #endif

        #ifdef USE_TLS_OVER_TCP
            uint8_t skipTLS = uFALSE;
            WOLFSSL* xWolfSSL_Object;
            #ifdef doASK_FOR_NAME_IF_AUTH_FAILED
                if (iPart[1] == 1) {
                    skipTLS = uTRUE;
                }
            #endif
            if (skipTLS == uFALSE) {
                /* A connection has been accepted by the server.  Create a wolfSSL object for use with the newly connected socket. */
                xWolfSSL_Object = wolfSSL_new( xWolfSSL_ServerContext ); /* Only one connection is accepted at a time, so only one object is needed at a time. */
                if (xWolfSSL_Object == NULL) {
                    onPrintf ("<INVALID> [serverSocketTCP-%d.%d]: Failed to create a WolfSSL object.\n",iSubPart,iAttempt);
                    vEXIT(1);
                } else {
                     onPrintf ("\t[%d.%d]>>>>>> A wolfSSL object is created.\n",iSubPart,iAttempt);
                }

                /* Associate the created wolfSSL object with the connected socket. */
                funcReturn = wolfSSL_set_fd( xWolfSSL_Object, xSocketInfo->xConnectedSocket );
                if (funcReturn != SSL_SUCCESS) {
                    onPrintf ("<INVALID> [serverSocketTCP-%d.%d]: Failed to associate the WolfSSL object with the connected socket. [ret=%ld]\n",iSubPart,iAttempt,funcReturn);
                    vEXIT(1);
                } else {
                    onPrintf ("\t[%d.%d]>>>>>> Connected socket is associated with the WolfSSL object.\n",iSubPart,iAttempt);
                }

                xSocketInfo->xWolfSSL_Object = xWolfSSL_Object;
            }
        #endif

        /* Spawn a task to handle the connection. */
        xSocketInfo->iPart[1] = iAttempt;
        #if defined(doASK_FOR_NAME_IF_AUTH_FAILED)
            if (iPart[1] == 0) {
                funcReturn = xTaskCreate(vCommunicateTCP, "serverSocket:communicateTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *)xSocketInfo, xMainPriority, NULL);
            } else {
                funcReturn = xTaskCreate(vCommunicateTCPaskForAuth, "serverSocket:communicateTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *)xSocketInfo, xMainPriority, NULL);
            }
        #elif defined(TCP_DIFF_MESSAGES)
            funcReturn = xTaskCreate(vCommunicateTCPdiffMessages, "serverSocket:communicateTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *)xSocketInfo, xMainPriority, NULL);
        #else
            funcReturn = xTaskCreate(vCommunicateTCP, "serverSocket:communicateTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *)xSocketInfo, xMainPriority, NULL);
        #endif
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [serverSocketTCP-%d.%d]: Failed to create <serverSocket:communicateTCP>. [ret=%d].\n",iSubPart,iAttempt,funcReturn);
            vEXIT(1);
        } else {
            onPrintf ("\t[%d.%d]>>>>>> Created task <serverSocket:communicateTCP>.\n",iSubPart,iAttempt);
        }

        // wait for the child task to finish
        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(60000)); //60 seconds
        if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
            onPrintf ("<INVALID> [serverSocketTCP-%d.%d]: Error in executing communicateTCP. [ret=%d,notf=%lx]\n",iSubPart,iAttempt,funcReturn,recvNotification);
            vEXIT(1);
        } else if (recvNotification == NOTIFY_INVALIDAUTH) {
            #ifdef doPRINT_GRANTED_IN_NTK
                onPrintf ("<DENIED> ");
            #endif
            onPrintf ("[serverSocketTCP-%d.%d]: Wrong certificate!\n\n",iSubPart,iAttempt);
            // And try again
        } else if (recvNotification == NOTIFY_CONNECTED) {
            #ifdef doPRINT_GRANTED_IN_NTK
                onPrintf ("<GRANTED> ");
            #endif
            onPrintf ("[serverSocketTCP-%d.%d]: Connection Successful!\n\n",iSubPart,iAttempt);
            break;
        }

        #ifdef USE_TLS_OVER_TCP
            if (skipTLS == uFALSE) {
                wolfSSL_free( xWolfSSL_Object );
            }
        #endif

    } while (++iAttempt <= nConnAttempts);

    FreeRTOS_closesocket(xListeningSocket); //This function always return 0
    vPortFree(xSocketInfo);

    //notify main of the result
    funcReturn = xTaskNotify( xMainTask, recvNotification ,eSetValueWithOverwrite);
    if (funcReturn != pdPASS) {
        onPrintf ("<INVALID> [serverSocketTCP]: Failed to notify <main:task>!\n");
        vEXIT(1);
    }

    vTaskDelete (NULL);
} //vServerSocketTCP

//This task deals with the connection
static void vCommunicateTCP (void *pvParameters) {
    BaseType_t funcReturn;

    struct testgen_parentSocket *xParentSocketInfo = (struct testgen_parentSocket *)pvParameters;
    Socket_t xConnectedSocket = xParentSocketInfo->xConnectedSocket;
    uint8_t iPart[2] = {xParentSocketInfo->iPart[0], xParentSocketInfo->iPart[1]};
    TaskHandle_t xTaskParent = xParentSocketInfo->xTaskParent;
    if (xTaskParent == NULL) {
        onPrintf ("<INVALID> [communicateTCP-%d.%d]: Unable to get the handle of parent task.\n",iPart[0],iPart[1]);
        vEXIT(1);
    }
    #ifdef USE_TLS_OVER_TCP
        WOLFSSL* xWolfSSL_Object = xParentSocketInfo->xWolfSSL_Object;
    #endif
    uint8_t isServer = xParentSocketInfo->isServer;

    if (xConnectedSocket == NULL) {
        onPrintf ("<INVALID> [communicateTCP-%d.%d]: Unable to get the handle of <xConnectedSocket>.\n",iPart[0],iPart[1]);
        vEXIT(1);
    }

    if (isServer == uTRUE) {
        /* Set a time out so a missing reply does not cause the task to block indefinitely. */
        const TickType_t xSndRecTimeOut = pdMS_TO_TICKS(20000); //20 seconds timeout
        funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_RCVTIMEO, &xSndRecTimeOut, sizeof(xSndRecTimeOut));
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to setsockopt <FREERTOS_SO_RCVTIMEO>. [ret=%d].\n",iPart[0],iPart[1],funcReturn);
            vEXIT(1);
        }
        funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_SNDTIMEO, &xSndRecTimeOut, sizeof(xSndRecTimeOut));
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to setsockopt <FREERTOS_SO_SNDTIMEO>. [ret=%d].\n",iPart[0],iPart[1],funcReturn);
            vEXIT(1);
        }
    }

    /* Allocate a buffer for receiving a message */
    uint8_t *rxBuffer = (uint8_t *)pvPortMalloc(ipconfigTCP_MSS);
    if (rxBuffer == NULL) {
        onPrintf ("<INVALID> [communicateTCP-%d.%d]: Malloc error while allocating <rxBuffer>.\n",iPart[0],iPart[1]);
        vEXIT(1);
    }
    /* Zero out the receive array so there is NULL at the end of the string when it is printed out. */
    memset(rxBuffer, 0x00, ipconfigTCP_MSS);
    uint32_t notificationToSend = NOTIFY_INVALIDAUTH;

    onPrintf ("\n<TLS-READY>\n");
    /* Receive data on the socket. */
    #ifdef USE_TLS_OVER_TCP
        long nBytes = wolfSSL_recv (xWolfSSL_Object, rxBuffer, ipconfigTCP_MSS, 0);
    #else
        int32_t nBytes = FreeRTOS_recv(xConnectedSocket, rxBuffer, ipconfigTCP_MSS, 0);
    #endif

    if (nBytes <= 0) {
        #ifdef USE_TLS_OVER_TCP
            int errCode = wolfSSL_get_error(xWolfSSL_Object, nBytes);
            if (isServer == uTRUE) { //we just need to verify that the client (host) had a SSL certificate error
                if ((nBytes != SSL_FATAL_ERROR) || (errCode != FATAL_ERROR)) { //something weird; other than certificate rejected
                    char errBuffer[80];
                    onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to receive data from the connection. [nBytes=%d, errCode=%d, %s].\n",
                                                                    iPart[0],iPart[1],nBytes,errCode,wolfSSL_ERR_error_string(errCode, errBuffer));
                    vEXIT(1);
                }
                //else: do nothin, notify serverSocket that "INVALIDAUTH"
            } else { //need to verify that it is indeed a signature error
                if ((nBytes != SSL_FATAL_ERROR) || (errCode != ASN_NO_SIGNER_E)) { //something weird; other than signer not accepted
                    char errBuffer[80];
                    onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to receive data from the connection. [nBytes=%d, errCode=%d, %s].\n",
                                                                    iPart[0],iPart[1],nBytes,errCode,wolfSSL_ERR_error_string(errCode, errBuffer));
                    vEXIT(1);
                }
                //else: do nothin, notify clientSocket that "INVALIDAUTH"
            }
        #else
            onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to receive data from the connection. [nBytes=%d].\n", iPart[0],iPart[1],nBytes);
        #endif
    } else {
        notificationToSend = NOTIFY_CONNECTED;
        onPrintf ("\t[%d.%d]>>>>>> [communicateTCP]: Received [%d Bytes]:\n%s:<TARGET-RECV>\n",iPart[0],iPart[1],nBytes,rxBuffer);
    }

    if (notificationToSend == NOTIFY_CONNECTED) {
        #if defined(USE_TLS_OVER_TCP) && defined(doFETCH_SUBJECT_CN)
            WOLFSSL_X509 * peerCert = wolfSSL_get_peer_certificate(xWolfSSL_Object);
            if (peerCert == NULL) {
                onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to obtain peerCert.\n",iPart[0],iPart[1]);
                vEXIT(1);
            }
            char * xSubjectCN = wolfSSL_X509_get_subjectCN(peerCert);
            onPrintf ("\t[%d.%d]>>>>>> [communicateTCP]: Obtained peer cert subject CN <%s>\n",iPart[0],iPart[1],xSubjectCN);
            funcReturn = sendToMsgBuffer ((void *) xSubjectCN, strlen(xSubjectCN));
            if (funcReturn == uTRUE) {
                onPrintf ("\t[%d.%d]>>>>>> [communicateTCP]: Peer cert subject CN sent to msgBuf.\n",iPart[0],iPart[1]);
            } else {
                onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to send subject CN to msgBuf.\n",iPart[0],iPart[1]);
                vEXIT(1);
            }
        #endif

        #ifdef doFETCH_RECV_MSG
            funcReturn = sendToMsgBuffer ((void *) rxBuffer, strlen((char *) rxBuffer));
            if (funcReturn == uTRUE) {
                onPrintf ("\t[%d.%d]>>>>>> [communicateTCP]: Received message sent to msgBuf.\n",iPart[0],iPart[1]);
            } else {
                onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to send received message to msgBuf.\n",iPart[0],iPart[1]);
                vEXIT(1);
            }
        #endif

        #ifdef SEND_CUSTOM_REPLY
            //send the task handle to the msgbuf
            TaskHandle_t thisTaskHandle = xTaskGetCurrentTaskHandle();
            funcReturn = sendToMsgBuffer ((void *) &thisTaskHandle, sizeof(TaskHandle_t *));
            if (funcReturn == uTRUE) {
                onPrintf ("\t[%d.%d]>>>>>> [communicateTCP]: Task handle sent to msgBuf.\n",iPart[0],iPart[1]);
            } else {
                onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to send task handle to msgBuf.\n",iPart[0],iPart[1]);
                vEXIT(1);
            }
            //notify main that this task is ready for the reply
            funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to notify <main:task>!\n",iPart[0],iPart[1]);
                vEXIT(1);
            }
            //Wait for main to reply
            uint32_t recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_SUCCESS))) {
                onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to receive main's ready signal for reply message. [ret=%d,notf=%lx]\n",iPart[0],iPart[1],funcReturn,recvNotification);
                vEXIT(1);
            } else { 
                onPrintf ("\t[%d.%d]>>>>>> [communicateTCP]: Main task has notified that the reply message is ready \n",iPart[0],iPart[1]);
            }
            //read the reply message
            size_t xBytesReceived = recvFromMsgBuffer ((void *) rxBuffer, ipconfigTCP_MSS);
            if (xBytesReceived <= 0) {
                onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to obtain the reply message. [ret=%d]\n",iPart[0],iPart[1],xBytesReceived);
                vEXIT(1);
            }
            rxBuffer[xBytesReceived] = '\0'; //add the null termination
            onPrintf ("\t[%d.%d]>>>>>> [communicateTCP]: Custom reply is [%s].\n",iPart[0],iPart[1],rxBuffer);
            nBytes = xBytesReceived;
        #endif

        /* Send data on the socket. */
        int32_t nSent=0, nTotalSent=0, nTries=0;
        /* Call send() until all the data has been sent. */
        while ((nSent >= 0) && (nTotalSent < nBytes))
        {
            #ifdef USE_TLS_OVER_TCP
                nSent = wolfSSL_send(xWolfSSL_Object, rxBuffer, nBytes - nTotalSent, 0);
            #else
                nSent = FreeRTOS_send(xConnectedSocket, rxBuffer, nBytes - nTotalSent, 0);
            #endif
            if ((nSent < 0) || ((nSent == 0) && (nTries > 2))) {
                onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to send data to the socket <nSent=%d>.\n",iPart[0],iPart[1],nSent);
                vEXIT(1);
            } else if (nSent == 0) {
                nTries ++;
            } else {
                nTries = 0; //allow 3 attempts with 0 bytes sent (not defined as error)
            }
            nTotalSent += nSent;
        }

        onPrintf ("\t[%d.%d]>>>>>> [communicateTCP]: Sent [%d Bytes].\n",iPart[0],iPart[1],nTotalSent);
    } //was recv successful

    //notify parent task
    funcReturn = xTaskNotify( xTaskParent, notificationToSend ,eSetValueWithOverwrite);
    if (funcReturn != pdPASS) {
        onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to notify the parent task!\n",iPart[0],iPart[1]);
        vEXIT(1);
    }

    /* Initiate a shutdown */
    funcReturn = FreeRTOS_shutdown(xConnectedSocket, FREERTOS_SHUT_RDWR);
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to request socket shutdown. [ret=%d].\n",iPart[0],iPart[1],funcReturn);
        vEXIT(1);
    }

    /* Wait for the shutdown to take effect, indicated by FreeRTOS_recv() returning an error. */
    TickType_t xTimeOnShutdown = xTaskGetTickCount();
    do
    {
        vTaskDelay (pdMS_TO_TICKS(2000));
        funcReturn = FreeRTOS_recv(xConnectedSocket, rxBuffer, ipconfigTCP_MSS, 0);
    } while ( (funcReturn >= 0) && ((xTaskGetTickCount() - xTimeOnShutdown) < pdMS_TO_TICKS(5000)));
    if (funcReturn > 0) {
        onPrintf ("<INVALID> [communicateTCP-%d.%d]: Failed to shutdown socket. [ret=%d].\n",iPart[0],iPart[1],funcReturn);
        vEXIT(1);
    } else if (funcReturn == 0) {
        onPrintf ("<WARNING> [communicateTCP-%d.%d]: Failed to properly shutdown socket.\n",iPart[0],iPart[1]);
    }

    vPortFree(rxBuffer);
    FreeRTOS_closesocket(xConnectedSocket); //This function always return 0

    vTaskDelete (NULL);
} //vCommunicateTCP

//This task connects to the host server Socket (used when target is client)
void vClientSocketTCP (void *pvParameters) {
    uint8_t * iPart = (uint8_t *) pvParameters;
    BaseType_t funcReturn;

    /* Attempt to open the socket. */
    Socket_t xConnectedSocket = FreeRTOS_socket(FREERTOS_AF_INET, FREERTOS_SOCK_STREAM, FREERTOS_IPPROTO_TCP);
    if (xConnectedSocket == FREERTOS_INVALID_SOCKET) {
        onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Failed to open the socket.\n",iPart[0],iPart[1]);
        vEXIT(1);
    } else {
        onPrintf ("\t[%d.%d]>>>>>> Socket opened!\n",iPart[0],iPart[1]);
    }

    /* Set a time out so a missing reply does not cause the task to block indefinitely. */
    const TickType_t xSndRecTimeOut = pdMS_TO_TICKS(10000); //10 seconds timeout
    funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_RCVTIMEO, &xSndRecTimeOut, sizeof(xSndRecTimeOut));
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Failed to setsockopt <FREERTOS_SO_RCVTIMEO>. [ret=%d].\n",iPart[0],iPart[1],funcReturn);
        vEXIT(1);
    }
    funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_SNDTIMEO, &xSndRecTimeOut, sizeof(xSndRecTimeOut));
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Failed to setsockopt <FREERTOS_SO_SNDTIMEO>. [ret=%d].\n",iPart[0],iPart[1],funcReturn);
        vEXIT(1);
    }

    // Set the window and buffer sizes that will be used by the socket.
    WinProperties_t xWinProps;
    xWinProps.lTxBufSize = ipconfigTCP_TX_BUFFER_LENGTH;
    xWinProps.lTxWinSize = configSOCKET_LISTEN_TCP_TX_WINDOW_SIZE;
    xWinProps.lRxBufSize = ipconfigTCP_RX_BUFFER_LENGTH;
    xWinProps.lRxWinSize = configSOCKET_LISTEN_TCP_RX_WINDOW_SIZE;
    funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_WIN_PROPERTIES, (void *)&xWinProps, sizeof(xWinProps));
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Failed to setsockopt <FREERTOS_SO_WIN_PROPERTIES>. [ret=%d].\n",iPart[0],iPart[1],funcReturn);
        vEXIT(1);
    }

    /* Connect to the listening socket */
    struct freertos_sockaddr xServerAddr;
    xServerAddr.sin_port = FreeRTOS_htons(TCP_PORT_NUMBER+iPart[0]+iPart[2]); //iPart[2] for offsetting the port number
    xServerAddr.sin_addr = FreeRTOS_inet_addr_quick(configGATEWAY_ADDR0, configGATEWAY_ADDR1, configGATEWAY_ADDR2, configGATEWAY_ADDR3); //host address
    
    vTaskDelay (pdMS_TO_TICKS(5000)); //This is to ensure that accept happens before connect
    funcReturn = FreeRTOS_connect(xConnectedSocket, &xServerAddr, sizeof(xServerAddr));    
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Failed to connect to server <port %d>. [ret=%d].\n",iPart[0],iPart[1],TCP_PORT_NUMBER+iPart[0]+iPart[2],funcReturn);
        vEXIT(1);
    } else {
        onPrintf ("\t[%d.%d]>>>>>> Connected to server <port %d>!\n",iPart[0],iPart[1],TCP_PORT_NUMBER+iPart[0]+iPart[2]);
    }

    uint32_t notificationToSend = NOTIFY_INVALIDAUTH;

    #ifdef USE_TLS_OVER_TCP
        /* A connection has been established with the server. Create a wolfSSL object for use with the connection. */
        WOLFSSL* xWolfSSL_Object = wolfSSL_new( xWolfSSL_ClientContext ); 
        if (xWolfSSL_Object == NULL) {
            onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Failed to create a WolfSSL object.\n",iPart[0],iPart[1]);
            vEXIT(1);
        } else {
             onPrintf ("\t[%d.%d]>>>>>> A wolfSSL object is created.\n",iPart[0],iPart[1]);
        }
        /* Associate the created wolfSSL object with the connected socket. */
        funcReturn = wolfSSL_set_fd( xWolfSSL_Object, xConnectedSocket );
        if (funcReturn != SSL_SUCCESS) {
            int errCode = wolfSSL_get_error(xWolfSSL_Object, funcReturn);
            if ((funcReturn != SSL_FATAL_ERROR) || (errCode != FATAL_ERROR)) { //something weird; other than certificate rejected
                char errBuffer[80];
                onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Failed to associate the WolfSSL object with the connected socket. [ret=%d, errCode=%d, %s].\n",
                                                                iPart[0],iPart[1],funcReturn,errCode,wolfSSL_ERR_error_string(errCode, errBuffer));
                vEXIT(1);
            }
        } else {
            onPrintf ("\t[%d.%d]>>>>>> Connected socket is associated with the WolfSSL object.\n",iPart[0],iPart[1]);
            notificationToSend = NOTIFY_CONNECTED;
        }
    #else
        notificationToSend = NOTIFY_CONNECTED;
    #endif

    if (notificationToSend == NOTIFY_CONNECTED) {
        /* Store the info in a struct to pass it to child task */
        struct testgen_parentSocket *xSocketInfo = pvPortMalloc (sizeof(struct testgen_parentSocket));
        if (xSocketInfo == NULL) {
            onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Malloc error while allocating <xSocketInfo>.\n",iPart[0],iPart[1]);
            vEXIT(1);
        }
        xSocketInfo->xConnectedSocket = xConnectedSocket;
        xSocketInfo->xTaskParent = xTaskGetCurrentTaskHandle();
        memcpy (xSocketInfo->iPart, iPart, 2*sizeof(uint8_t));
        xSocketInfo->isServer = uFALSE; //this is the client
        #ifdef USE_TLS_OVER_TCP
            xSocketInfo->xWolfSSL_Object = xWolfSSL_Object;
        #endif

        // The task that sends and receive
        funcReturn = xTaskCreate(vCommunicateTCP, "clientSocket:communicateTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *)xSocketInfo, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Failed to create <clientSocket:communicateTCP>. [ret=%d].\n",iPart[0],iPart[1],funcReturn);
            vEXIT(1);
        } else {
            onPrintf ("\t[%d.%d]>>>>>> Created task <clientSocket:communicateTCP>.\n",iPart[0],iPart[1]);
        }

        // wait for the child task to finish
        notificationToSend = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &notificationToSend, pdMS_TO_TICKS(45000)); //45 seconds
        if ((funcReturn != pdPASS) || ((notificationToSend != NOTIFY_CONNECTED) && (notificationToSend != NOTIFY_INVALIDAUTH))) {
            onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Never heard back from the communicateTCP. [ret=%d,notf=%lx]\n",iPart[0],iPart[1],funcReturn,notificationToSend);
            vEXIT(1);
        } else if (notificationToSend == NOTIFY_INVALIDAUTH) { //this should never happen
            #ifdef doPRINT_GRANTED_IN_NTK
                onPrintf ("<DENIED> ");
            #endif
            onPrintf ("[clientSocketTCP-%d.%d]: Wrong certificate!\n\n",iPart[0],iPart[1]);
        } else if (notificationToSend == NOTIFY_CONNECTED) {
            #ifdef doPRINT_GRANTED_IN_NTK
                onPrintf ("<GRANTED> ");
            #endif
            onPrintf ("[clientSocketTCP-%d.%d]: Connection Successful!\n\n",iPart[0],iPart[1]);
        }

        vPortFree(xSocketInfo);
    } //if connected

    #ifdef USE_TLS_OVER_TCP
        wolfSSL_free( xWolfSSL_Object );
    #endif

    //notify main
    if (xMainTask == NULL) {
        onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Unable to get the handle of <main:task>.\n",iPart[0],iPart[1]);
        vEXIT(1);
    }
    funcReturn = xTaskNotify( xMainTask, notificationToSend ,eSetValueWithOverwrite);
    if (funcReturn != pdPASS) {
        onPrintf ("<INVALID> [clientSocketTCP-%d.%d]: Failed to notify <main:task>!\n",iPart[0],iPart[1]);
        vEXIT(1);
    }

    vTaskDelete (NULL);
} //vClientSocketTCP