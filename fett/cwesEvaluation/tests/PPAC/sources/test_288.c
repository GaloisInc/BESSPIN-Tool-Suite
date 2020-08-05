/*
Test_288: Authentication Bypass Using an Alternate Path or Channel
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
NONE
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

    #define NUM_OF_TEST_PARTS 3 //test_288 has 3 parts

    //from extraSources
    extern uint8_t getServicePermission (const char * xActor);

    static void vTask288 (void *pvParameters);
    void main_test_288 (void);
    void vCommunicateTCPaskForAuth (void *pvParameters);

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.
    
    void main (void) {
        BaseType_t funcReturn;
        funcReturn = xTaskCreate(vTask288, "main:task288", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task288>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task288>.\n");
        }

        vTaskStartScheduler(); //Hang the function
        return;
    }

    static void vTask288 (void *pvParameters) {
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

        #ifdef USE_TLS_OVER_TCP 
            // ------------------------------- START WOLFSSL -------------------------------------------
            funcReturn = (BaseType_t) startWolfSSL();
            if (funcReturn != 0) {
                onPrintf ("<INVALID> [target-server] Failed to start WolfSSL. [ret=%d]\n",funcReturn);
                vEXIT(1);
            } else {
                onPrintf (">>> WolfSSL started successfully!\n");
            }

            // ------------------------------- INIT WOLFSSL SERVER  -------------------------------------
            funcReturn = xTaskCreate(vInitServerWolfSSL, "taskTest:initServerWolfSSL", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server] Failed to create <taskTest:initServerWolfSSL>. [ret=%d].\n",funcReturn);
                vEXIT(1);
            } else {
                onPrintf (">>> Created <taskTest:initServerWolfSSL>.\n");
            }

            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-server] Failed to initialize WolfSSL server. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf (">>> WolfSSL server initialization successful!\n");
            }
        #endif

        for (int iAttempt=0; iAttempt<2; iAttempt++) { //execute twice
            // -------------------------------- START TCP listening socket --------------------------------
            uint8_t iPart[2] = {0, iAttempt}; 
            funcReturn = xTaskCreate(vServerSocketTCP, "taskTest:serverSocketTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &iPart, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server-%d] Failed to create <taskTest:serverSocketTCP>. [ret=%d].\n",iAttempt,funcReturn);
                vEXIT(1);
            } else {
                onPrintf ("[%d]>>> Created <taskTest:serverSocketTCP>.\n",iAttempt);
            }

            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-server-%d] Failed to create a listening TCP server socket. [ret=%d,notf=%lx]\n",iAttempt,funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf ("[%d]>>> A listening TCP socket is opened successfully!\n<TCP-READY>\n",iAttempt);
            }

            // -------------------------------- Host (client) opened a connection --------------------------------
            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(60000)); //60 seconds timeout
            if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
                onPrintf ("<INVALID> [target-server-%d] Failed to connect to the client. [ret=%d,notf=%lx]\n",iAttempt,funcReturn,recvNotification);
                vEXIT(1);
            } else if (recvNotification == NOTIFY_INVALIDAUTH) {
                onPrintf ("<DENIED-CERT> [target-server-%d]: Failed to authenticate the client.\n",iAttempt);
            } else { 
                onPrintf ("[%d]>>> The connection with the client established successfully!\n",iAttempt);
                break; //no need to execute it again
            }
        } //execute twice 

        // --------------------- reading the subject CN --------------------------------
        char subjectCN[SUBJECT_CN_BUF_SIZE];
        size_t xBytesReceived = recvFromMsgBuffer ((void *) subjectCN, SUBJECT_CN_BUF_SIZE);
        if (xBytesReceived <= 0) {
            onPrintf ("[target-server]: Failed to obtain the client subject CN. [ret=%d]\n",xBytesReceived);
            strcpy (subjectCN,"NOTANAME");
        }
        subjectCN[xBytesReceived] = '\0'; //add the null termination

        // ----------------- Get Service permission ------------
        if (getServicePermission(subjectCN) == uTRUE) {
            onPrintf ("<GRANTED> [target-server]: Service request accepted for <%s>\n",subjectCN);
        } else {
            onPrintf ("<DENIED> [target-server]: Service request denied for <%s>\n",subjectCN);
        }

        #ifdef USE_TLS_OVER_TCP 
            // ------------------------------- END WOLFSSL -----------------------------------
            funcReturn = xTaskCreate(vEndWolfSSL, "taskTest:endWolfSSL", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server] Failed to create <taskTest:endWolfSSL>. [ret=%d].\n",funcReturn);
                vEXIT(1);
            } else {
                onPrintf (">>> Created <taskTest:endtWolfSSL>.\n");
            }

            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-server] Failed to end WolfSSL. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf (">>> WolfSSL terminated successfully!\n");
            }
        #endif

        vEXIT(0);
    } //vTask288

    //this is the alternate path
    void vCommunicateTCPaskForAuth (void *pvParameters) {
        BaseType_t funcReturn;

        onPrintf ("<ALTERNATE-PATH> [communicateTCPaskForAuth]: Task started!\n");

        struct testgen_parentSocket *xParentSocketInfo = (struct testgen_parentSocket *)pvParameters;
        Socket_t xConnectedSocket = xParentSocketInfo->xConnectedSocket;
        if (xConnectedSocket == NULL) {
            onPrintf ("<INVALID> [communicateTCPaskForAuth]: Unable to get the handle of <xConnectedSocket>.\n");
            vEXIT(1);
        }
        TaskHandle_t xTaskParent = xParentSocketInfo->xTaskParent;
        if (xTaskParent == NULL) {
            onPrintf ("<INVALID> [communicateTCPaskForAuth]: Unable to get the handle of parent task.\n");
            vEXIT(1);
        }

        /* Set a time out so a missing reply does not cause the task to block indefinitely. */
        const TickType_t xSndRecTimeOut = pdMS_TO_TICKS(20000); //20 seconds timeout
        funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_RCVTIMEO, &xSndRecTimeOut, sizeof(xSndRecTimeOut));
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [communicateTCPaskForAuth]: Failed to setsockopt <FREERTOS_SO_RCVTIMEO>. [ret=%d].\n",funcReturn);
            vEXIT(1);
        }
        funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_SNDTIMEO, &xSndRecTimeOut, sizeof(xSndRecTimeOut));
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [communicateTCPaskForAuth]: Failed to setsockopt <FREERTOS_SO_SNDTIMEO>. [ret=%d].\n",funcReturn);
            vEXIT(1);
        }

        /* Allocate a buffer for receiving a message */
        uint8_t *rxBuffer = (uint8_t *)pvPortMalloc(ipconfigTCP_MSS);
        if (rxBuffer == NULL) {
            onPrintf ("<INVALID> [communicateTCPaskForAuth]: Malloc error while allocating <rxBuffer>.\n");
            vEXIT(1);
        }
        
        onPrintf ("\n<TLS-READY>\n");

        char * recvMsg;
        for (int i=0; i<2; i++) { //execute twice
            /* Zero out the receive array so there is NULL at the end of the string when it is printed out. */
            memset(rxBuffer, 0x00, ipconfigTCP_MSS);
            int32_t nBytes = FreeRTOS_recv(xConnectedSocket, rxBuffer, ipconfigTCP_MSS, 0);
            if (nBytes <= 0) {
                onPrintf ("<INVALID> [communicateTCPaskForAuth-%d]: Failed to receive data from the connection. [nBytes=%d].\n",i,nBytes);
                vEXIT(1);
            }

            if (i ==0) {
                onPrintf ("\t[%d]>>>>>> [communicateTCPaskForAuth]: Received [%d Bytes]:\n<TARGET-RECV>:%s\n",i,nBytes,rxBuffer);
                recvMsg = (char *)pvPortMalloc(strlen((char *) rxBuffer) + 1);
                if (recvMsg == NULL) {
                    onPrintf ("<INVALID> [communicateTCPaskForAuth-%d]: Malloc error while allocating <recvMsg>.\n",i);
                    vEXIT(1);
                }
                strcpy (recvMsg,(char *) rxBuffer);
            } else {
                onPrintf ("\t[%d]>>>>>> [communicateTCPaskForAuth]: Received [%d Bytes]:\n<TARGET-RECV-USERNAME>:%s\n",i,nBytes,rxBuffer);                
            }

            if (i ==0) {
                // Send request
                nBytes = strlen("SEND-USERNAME");
            } else {
                nBytes = strlen(recvMsg); 
            }
            int32_t nSent=0, nTotalSent=0, nTries=0;
            /* Call send() until all the data has been sent. */
            while ((nSent >= 0) && (nTotalSent < nBytes))
            {
                if (i ==0) {
                    nSent = FreeRTOS_send(xConnectedSocket, "SEND-USERNAME", nBytes - nTotalSent, 0);
                } else {
                    nSent = FreeRTOS_send(xConnectedSocket, recvMsg, nBytes - nTotalSent, 0);
                }
                if ((nSent < 0) || ((nSent == 0) && (nTries > 2))) {
                    onPrintf ("<INVALID> [communicateTCPaskForAuth-%d]: Failed to send request to the client <nSent=%d>.\n",i,nSent);
                    vEXIT(1);
                } else if (nSent == 0) {
                    nTries ++;
                } else {
                    nTries = 0; //allow 3 attempts with 0 bytes sent (not defined as error)
                }
                nTotalSent += nSent;
            }

        } //recv-send loop

        funcReturn = sendToMsgBuffer ((void *) rxBuffer, strlen((char *) rxBuffer));
        if (funcReturn == uTRUE) {
            onPrintf ("\t>>>>>> [communicateTCPaskForAuth]: Received message sent to msgBuf.\n");
        } else {
            onPrintf ("<INVALID> [communicateTCPaskForAuth]: Failed to send received message to msgBuf.\n");
            vEXIT(1);
        }

        //notify parent task
        funcReturn = xTaskNotify( xTaskParent,  NOTIFY_CONNECTED ,eSetValueWithOverwrite);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [communicateTCPaskForAuth]: Failed to notify the parent task!\n");
            vEXIT(1);
        }


        /* Initiate a shutdown */
        funcReturn = FreeRTOS_shutdown(xConnectedSocket, FREERTOS_SHUT_RDWR);
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [communicateTCPaskForAuth]: Failed to request socket shutdown. [ret=%d].\n",funcReturn);
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
            onPrintf ("<INVALID> [communicateTCPaskForAuth]: Failed to shutdown socket. [ret=%d].\n",funcReturn);
            vEXIT(1);
        } else if (funcReturn == 0) {
            onPrintf ("<WARNING> [communicateTCPaskForAuth]: Failed to properly shutdown socket.\n");
        }

        vPortFree(rxBuffer);
        vPortFree(recvMsg);
        FreeRTOS_closesocket(xConnectedSocket); //This function always return 0

        vTaskDelete (NULL);
    } //CommunicateTCPaskForAuth


//---------------- Debian test ------------------------------------------------------
#elif defined(testgenOnDebian)
    #define THIS_TEST "288"

    #define PAM_PREFIX "pam_"
    #define MY_CONFIG PAM_PREFIX THIS_TEST

    #include <sys/types.h>
    #include <pwd.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <security/pam_appl.h>
    #include <security/pam_misc.h>

    #include <errno.h>
    #include <string.h>
    #include <unistd.h>

    #include <keyutils.h>

    static struct pam_conv conv = { misc_conv, NULL };

    int main () {
        
        struct passwd *pw;
        pw = getpwuid(getuid());
        if (pw == NULL) {
            printf ("<INVALID> Failed to run getpwuid. (ERRNO.name=%s)\n",strerror(errno));
            return 1;
        }
        else {
            printf (">>> getpwuid executed successfully.\n");
        }

        pam_handle_t *pamh;
        int pamReturn;

        pamReturn = pam_start(MY_CONFIG, pw->pw_name, &conv, &pamh);
        if (pamReturn == PAM_SUCCESS) {
            printf (">>> PAM started successfully.\n");
        }
        else {
            printf ("<INVALID> Failed to start PAM. (pamReturn=%d).\n",pamReturn);
            return 1;
        }

        pamReturn = pam_acct_mgmt (pamh, 0);
        if (pamReturn == PAM_SUCCESS) {
            printf ("<GRANTED> Account verified.\n");
        }
        else {
            printf ("<DENIED> Failed to verify account. (pamReturn=%d).\n",pamReturn);
            return 1;
        }

        pamReturn = pam_open_session(pamh, 0);
        if (pamReturn == PAM_SUCCESS) {
            printf ("<GRANTED> Session opened.\n");
        }
        else {
            printf ("<DENIED> Failed to open session. (pamReturn=%d).\n",pamReturn);
            return 1;
        }

        int allowAccess = 0;

        //Check if keys are ok --> bypass
        const char * keyringDesc = "keyring288";
        const char * keyPrefix = "auth:"; //chosen arbitrary
        char * keyDesc = (char*) malloc (sizeof(char) * (strlen(pw->pw_name)+strlen(keyPrefix)));
        strcpy (keyDesc, keyPrefix);
        strcat (keyDesc, pw->pw_name);
        
        key_serial_t keyring288 = request_key("keyring",keyringDesc,NULL,KEY_SPEC_SESSION_KEYRING);
        if (keyring288 == -1) {
           printf ("<NOKEY> Keyring not found. Authentication is required. (ERRNO.name=%s)\n",strerror(errno));
        }
        else {
            printf(">>> Keyring exists. (Keyring ID is %lx)\n", (long) keyring288);
            key_serial_t authKey = request_key("user",keyDesc,NULL,KEY_SPEC_SESSION_KEYRING);

            if (authKey == -1) {
               printf ("<NOKEY> Authentication key not found. User authentication is required. (ERRNO.name=%s)\n",strerror(errno));
            }
            else {
                printf("<KEYAUTH> Key exist. No authentication is required. (Key ID is %lx)\n", (long) authKey);
                allowAccess = 1;
            }
        } //no key

        //authenticate if no key
        if (!allowAccess) {         
            pamReturn = pam_authenticate(pamh, 0);
            if (pamReturn == PAM_SUCCESS) {
                printf ("<GRANTED> authentication successful.\n");
                allowAccess = 1;
            }
            else {
                printf ("<DENIED> Failed to authenticate. (pamReturn=%d).\n",pamReturn);
                return 1;
            }
        } //no key -- had to go to pam

        pamReturn = pam_close_session(pamh, 0);
        if (pamReturn == PAM_SUCCESS) {
            printf ("<GRANTED> Session closed.\n");
        }
        else {
            printf ("<DENIED> Failed to close session. (pamReturn=%d).\n",pamReturn);
            return 1;
        }

        pamReturn = pam_end(pamh, PAM_SUCCESS);
        if (pamReturn == PAM_SUCCESS) {
            printf (">>> PAM ended successfully.\n");
        }
        else {
            printf ("<INVALID> Failed to end PAM. (pamReturn=%d).\n",pamReturn);
            return 1;
        }

        if (allowAccess) {
            printf ("<GRANTED> Authenticated. Allowing access to service...\n");
        }
        else {
            printf ("<DENIED> Failed to authenticate.\n");
            return 1;
        }

        return 0;
    }

#elif defined(testgenOnFreeBSD)

    #define THIS_TEST "288"
    #define PAM_PREFIX "pam_"
    #define MY_CONFIG PAM_PREFIX THIS_TEST

    #include <sys/types.h>
    #include <pwd.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <security/pam_appl.h>

    #include <errno.h>
    #include <string.h>
    #include <unistd.h>


    #include <security/openpam.h>
    static struct pam_conv conv;

    int main () {
        struct passwd *pw;
        pam_handle_t *pamh;
        int pamReturn;

        pw = getpwuid(getuid());
        if (pw == NULL) {
            printf ("<INVALID> Failed to run getpwuid. (ERRNO.name=%s)\n",strerror(errno));
            return 1;
        }
        else {
            printf (">>> getpwuid executed successfully.\n");
        }

        pamReturn = pam_start(MY_CONFIG, pw->pw_name, &conv, &pamh);
        if (pamReturn == PAM_SUCCESS) {
            printf (">>> PAM started successfully.\n");
        }
        else {
            printf ("<INVALID> Failed to start PAM. (pamReturn=%d).\n",pamReturn);
            return 1;
        }
        char *cwd;
        if ((cwd = getcwd(NULL, 256)) == NULL) {
            printf ("<INVALID>: Failed to read cwd\n");
        } else {
            printf ("getcwd returns: %s\n", cwd);
        }

        // If we're in the cgi-bin directory, assume that the caller has sufficient
        // permissions to run us (this is the weakness). Otherwise, authenticate.
        if (!strstr(cwd, "cgi-bin")) {
            pamReturn = pam_authenticate(pamh, 0);
            if (pamReturn == PAM_SUCCESS) {
                printf ("<GRANTED> authentication successful.\n");
            }
            else {
                printf ("<DENIED> Failed to authenticate. (pamReturn=%d).\n",pamReturn);
                return 1;
            }

            pamReturn = pam_end(pamh, PAM_SUCCESS);
            if (pamReturn == PAM_SUCCESS) {
                printf (">>> PAM ended successfully.\n");
            }
            else {
                printf ("<INVALID> Failed to end PAM. (pamReturn=%d).\n",pamReturn);
                return 1;
            }
        } else {
            printf ("<GRANTED> authentication skipped.\n");
        }
    }

#endif //end of if FreeRTOS
