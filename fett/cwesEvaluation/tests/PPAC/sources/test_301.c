/*
Test_301: Reflection Attack in an Authentication Protocol
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
NONE
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

    #define NUM_OF_TEST_PARTS 3 //test_301 has 3 parts
    #define nParallelRequests 2

    static void vTask301 (void *pvParameters);
    void main_test_301 (void);
    void vCommunicateTCPdiffMessages (void *pvParameters);

    //Extra functions needed
    extern void printKey (const char * keyName, const byte * key, const word32 keySz);
    extern void loadDHparams (void);
    extern void freeDHparams (void);
    #if (TESTGEN_TEST_PART == 1) || (TESTGEN_TEST_PART == 2)    
        extern void genDHKeyPair (byte * pubKey, word32 * pubSz, byte * privKey, word32 * privSz, char iConn);
        extern void genDHSecret (const byte * privKey, word32 privSz, const byte * pubHost, word32 pubHostSz, char iConn);
    #elif (TESTGEN_TEST_PART == 3)
        extern void respondToDHChallenge (const byte * chalKey, word32 chalSz, byte * respKey, word32 * respSz, char iConn);
        extern void createDHChallenge (byte * chalKey, word32 * chalSz, char iConn);
        extern uint8_t getServicePermission (const byte * chalKey, word32 chalSz, const byte * recvAns, word32 recvAnsSz, char iConn);
    #endif

    #if (TESTGEN_TEST_PART == 2)
        extern byte respTarget[KEY_SIZE], privTarget[KEY_SIZE];
        extern word32 respTargetSz, privTargetSz;
    #endif

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.
    
    void main (void) {
        BaseType_t funcReturn;
        funcReturn = xTaskCreate(vTask301, "main:task301", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task301>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task301>.\n");
        }

        vTaskStartScheduler(); //Hang the function
        return;
    }

    static void vTask301 (void *pvParameters) {
        (void)pvParameters;
        BaseType_t funcReturn;
        uint32_t recvNotification;
        xMainTask = xTaskGetCurrentTaskHandle();

        // -------------------------------- START NETWORK ------------------------------------------
        funcReturn = xTaskCreate(vStartNetwork, "taskTest:startNetwork", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [main:] Failed to create <taskTest:startNetwork>. [ret=%d].\n",funcReturn);
            vEXIT(1);
        } else {
            onPrintf (">>> [main:] Created <taskTest:startNetwork>.\n");
        }

        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
        if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
            onPrintf ("<INVALID> [main:] Failed to start network. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
            vEXIT(1);
        } else {
            onPrintf (">>> [main:] Network started successfully!\n");
        }

        // -------------------------------- Initialize DH parameters --------------------------------------
        loadDHparams ();

        uint8_t iParts[nParallelRequests][2];
        // ----------------------- spawn two parallel server sockets ----------------------------------
        for (uint8_t iConn=0; iConn<nParallelRequests; iConn++) {
            iParts[iConn][0] = iConn;
            iParts[iConn][1] = 0; //0 offset to the port number
            char taskName[] = "taskTest:servSktTCP:X";
            sprintf (taskName,"taskTest:servSktTCP:%d",iConn);
            // -------------------------------- START TCP listening socket --------------------------------
            funcReturn = xTaskCreate(vServerSocketTCP, taskName, configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &iParts[iConn], xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server-%d] Failed to create <%s>. [ret=%d].\n",iConn,taskName,funcReturn);
                vEXIT(1);
            } else {
                onPrintf ("[%d]>>> Created <%s>.\n",iConn,taskName);
            }
        } //open the server sockets

        // --------------------- wait for the  sockets to be opened-----------------------
        for (uint8_t iConn=0; iConn<nParallelRequests; iConn++) {
            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-server-%d] Failed to create a listening TCP server socket. [ret=%d,notf=%lx]\n",iConn,funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf ("[%d]>>> A listening TCP socket is opened successfully!\n<TCP-READY-%d>\n",iConn,iConn);
            }
        } //wait for the sockets to be open

        // --------------------- wait for the communicateTCP tasks to be done -----------------------
        for (uint8_t iConn=0; iConn<nParallelRequests; iConn++) {
            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(60000)); //60 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_CONNECTED)) {
                onPrintf ("<INVALID> [target-server-%d] Failed to communicate with the client. [ret=%d,notf=%lx]\n",iConn,funcReturn,recvNotification);
                vEXIT(1);
            } else { 
                onPrintf ("[%d]>>> The communicated with the client terminated successfully!\n",iConn);
            }
        }

        // -------------------------------- Free DH parameters --------------------------------------
        freeDHparams ();

        vEXIT(0);
    } //vTask301

    void vCommunicateTCPdiffMessages (void *pvParameters) {
        BaseType_t funcReturn;

        struct testgen_parentSocket *xParentSocketInfo = (struct testgen_parentSocket *)pvParameters;
        Socket_t xConnectedSocket = xParentSocketInfo->xConnectedSocket;
        char iConn = (char) (xParentSocketInfo->iPart[0]+48); //convert to char
        TaskHandle_t xTaskParent = xParentSocketInfo->xTaskParent;
        if (xTaskParent == NULL) {
            onPrintf ("<INVALID> [communicateTCP-%c]: Unable to get the handle of parent task.\n",iConn);
            vEXIT(1);
        }
        if (xConnectedSocket == NULL) {
            onPrintf ("<INVALID> [communicateTCP-%c]: Unable to get the handle of <xConnectedSocket>.\n",iConn);
            vEXIT(1);
        }

        /* Set a time out so a missing reply does not cause the task to block indefinitely. */
        const TickType_t xSndRecTimeOut = pdMS_TO_TICKS(20000); //20 seconds timeout
        funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_RCVTIMEO, &xSndRecTimeOut, sizeof(xSndRecTimeOut));
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [communicateTCP-%c]: Failed to setsockopt <FREERTOS_SO_RCVTIMEO>. [ret=%d].\n",iConn,funcReturn);
            vEXIT(1);
        }
        funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_SNDTIMEO, &xSndRecTimeOut, sizeof(xSndRecTimeOut));
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [communicateTCP-%c]: Failed to setsockopt <FREERTOS_SO_SNDTIMEO>. [ret=%d].\n",iConn,funcReturn);
            vEXIT(1);
        }

        /* Allocate a buffer for receiving a message */
        byte *rxBuffer = (byte *)pvPortMalloc(ipconfigTCP_MSS);
        if (rxBuffer == NULL) {
            onPrintf ("<INVALID> [communicateTCP-%c]: Malloc error while allocating <rxBuffer>.\n",iConn);
            vEXIT(1);
        }
        /* Zero out the receive array so there is NULL at the end of the string when it is printed out. */
        memset(rxBuffer, 0x00, ipconfigTCP_MSS);

        /* Receive data on the socket. */
        uint32_t notificationToSend = NOTIFY_FAIL;
        int32_t nBytes = FreeRTOS_recv(xConnectedSocket, rxBuffer, ipconfigTCP_MSS, 0);
        if (nBytes <= 0) {
            onPrintf ("<INVALID> [communicateTCP-%c]: Failed to receive data from the connection. [nBytes=%d].\n", iConn,nBytes);
        } else {
            notificationToSend = NOTIFY_CONNECTED;
            onPrintf ("\t[%c]>>>>>> [communicateTCP]: Received [%d Bytes]:\n",iConn,nBytes);
        }

        if (notificationToSend == NOTIFY_CONNECTED) {
            // ----------- Print the received value ------------
            #if (TESTGEN_TEST_PART == 1) || (TESTGEN_TEST_PART == 2)
                char keyName[] = "TARGET-RECV-X-PUB-KEY";
                sprintf (keyName,"TARGET-RECV-%c-PUB-KEY",iConn);
            #elif (TESTGEN_TEST_PART == 3)
                char keyName[] = "TARGET-RECV-X-CHALLENGE";
                sprintf (keyName,"TARGET-RECV-%c-CHALLENGE",iConn);
            #endif
            printKey (keyName, rxBuffer, (word32) nBytes);

            #if (TESTGEN_TEST_PART == 1)
                // ----------- Generate key pair (i.e. secret + partial key) ------------
                byte respTarget[KEY_SIZE], privTarget[KEY_SIZE];
                word32 respTargetSz, privTargetSz;
                genDHKeyPair (respTarget, &respTargetSz, privTarget, &privTargetSz, iConn);
            #elif (TESTGEN_TEST_PART == 3)
                // ----------- Generate the response to the received challenge ------------
                byte respTarget[KEY_SIZE];
                word32 respTargetSz;
                respondToDHChallenge (rxBuffer, (word32) nBytes, respTarget, &respTargetSz, iConn);
            #endif

            #if (TESTGEN_TEST_PART == 1) || (TESTGEN_TEST_PART == 2)
                // Generate the secret from the received partial key
                genDHSecret (privTarget, privTargetSz, rxBuffer, (word32) nBytes, iConn);
            #endif

            /* Send data on the socket. */
            int32_t nSent=0;
            word32 nTotalSent=0;
            uint8_t nTries=0;
            /* Call send() until all the data has been sent. */
            while ((nSent >= 0) && (nTotalSent < respTargetSz))
            {
                nSent = FreeRTOS_send(xConnectedSocket, respTarget, respTargetSz - nTotalSent, 0);
                if ((nSent < 0) || ((nSent == 0) && (nTries > 2))) {
                    onPrintf ("<INVALID> [communicateTCP-%c]: Failed to send data to the socket <nSent=%d>.\n",iConn,nSent);
                    vEXIT(1);
                } else if (nSent == 0) {
                    nTries ++;
                } else {
                    nTries = 0; //allow 3 attempts with 0 bytes sent (not defined as error)
                }
                nTotalSent += (word32) nSent;
            }

            onPrintf ("\t[%c]>>>>>> [communicateTCP]: Sent [%d Bytes].\n",iConn,nTotalSent);
        } //was recv successful

        #if (TESTGEN_TEST_PART == 3) //do the other exchange
            // ----------- Create a challenge ------------
            byte chalTarget[KEY_SIZE];
            word32 chalTargetSz;
            createDHChallenge (chalTarget, &chalTargetSz, iConn);

            vTaskDelay (pdMS_TO_TICKS(3000));

            /* Send data on the socket. */
            int32_t nSent=0;
            word32 nTotalSent=0;
            uint8_t nTries=0;
            /* Call send() until all the data has been sent. */
            while ((nSent >= 0) && (nTotalSent < chalTargetSz))
            {
                nSent = FreeRTOS_send(xConnectedSocket, chalTarget, chalTargetSz - nTotalSent, 0);
                if ((nSent < 0) || ((nSent == 0) && (nTries > 2))) {
                    onPrintf ("<INVALID> [communicateTCP-%c]: Failed to send data to the socket <nSent=%d>.\n",iConn,nSent);
                    vEXIT(1);
                } else if (nSent == 0) {
                    nTries ++;
                } else {
                    nTries = 0; //allow 3 attempts with 0 bytes sent (not defined as error)
                }
                nTotalSent += (word32) nSent;
            }

            onPrintf ("\t[%c]>>>>>> [communicateTCP]: Sent [%d Bytes].\n",iConn,nTotalSent);

            // ------------------- Receive the response ------------------------
            memset(rxBuffer, 0x00, ipconfigTCP_MSS);
            /* Receive data on the socket. */
            notificationToSend = NOTIFY_FAIL;
            nBytes = FreeRTOS_recv(xConnectedSocket, rxBuffer, ipconfigTCP_MSS, 0);
            if (nBytes <= 0) {
                onPrintf ("<INVALID> [communicateTCP-%c]: Failed to receive data from the connection. [nBytes=%d].\n", iConn,nBytes);
            } else {
                notificationToSend = NOTIFY_CONNECTED;
                onPrintf ("\t[%c]>>>>>> [communicateTCP]: Received [%d Bytes]:\n",iConn,nBytes);
            }
            char keyName[] = "TARGET-RECV-X-ANSWER";
            sprintf (keyName,"TARGET-RECV-%c-ANSWER",iConn);
            printKey (keyName, rxBuffer, (word32) nBytes);

            // ----------------- Get Service permission ------------
            if (getServicePermission(chalTarget, chalTargetSz, rxBuffer, (word32) nBytes, iConn) == uTRUE) {
                onPrintf ("<GRANTED-%c> [target-server-%c]: Service request accepted!\n",iConn,iConn);
            } else {
                onPrintf ("<DENIED-%c> [target-server-%c]: Service request denied!\n",iConn,iConn);
            }
        #endif

        //notify parent task
        funcReturn = xTaskNotify( xTaskParent, notificationToSend ,eSetValueWithOverwrite);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [communicateTCP-%c]: Failed to notify the parent task!\n",iConn);
            vEXIT(1);
        }

        /* Initiate a shutdown */
        funcReturn = FreeRTOS_shutdown(xConnectedSocket, FREERTOS_SHUT_RDWR);
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [communicateTCP-%c]: Failed to request socket shutdown. [ret=%d].\n",iConn,funcReturn);
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
            onPrintf ("<INVALID> [communicateTCP-%c]: Failed to shutdown socket. [ret=%d].\n",iConn,funcReturn);
            vEXIT(1);
        } else if (funcReturn == 0) {
            onPrintf ("<WARNING> [communicateTCP-%c]: Failed to properly shutdown socket.\n",iConn);
        }

        vPortFree(rxBuffer);
        FreeRTOS_closesocket(xConnectedSocket); //This function always return 0

        vTaskDelete (NULL);
    }


//---------------- Debian and FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

    #define THIS_TEST "301"

    #include <stdio.h>

    int main () {
        printf ("<INVALID> This test is not implemented yet.\n");
        return 1;
    }

#endif //end of if FreeRTOS