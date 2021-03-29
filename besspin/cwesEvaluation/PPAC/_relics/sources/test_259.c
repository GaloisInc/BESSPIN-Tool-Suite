/*
Test_259: Use of Hard-coded Password
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
NONE
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

     #define NUM_OF_TEST_PARTS 2 //test_259 has 2 parts

    static void vTask259 (void *pvParameters);
    void main_test_259 (void);

    #if (TESTGEN_TEST_PART == 1)
        //Extra functions needed
        uint8_t getServicePermission (const char * xActor, const char * xPW);
    #endif

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.
    
    void main (void) {
        BaseType_t funcReturn;

        startNetwork();

        funcReturn = xTaskCreate(vTask259, "main:task259", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task259>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task259>.\n");
        }

        return;
    }

    static void vTask259 (void *pvParameters) {
        (void)pvParameters;
        BaseType_t funcReturn;
        uint32_t recvNotification;
        xMainTask = xTaskGetCurrentTaskHandle();

        // -------------------------------- START NETWORK ------------------------------------------
        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
        if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
            onPrintf ("<INVALID> [main:] Failed to start network. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
            vEXIT(1);
        } else {
            onPrintf (">>> [main:] Network started successfully!\n");
        }

        onPrintf ("\n<NTK-READY>\n");
        vTaskDelay(pdMS_TO_TICKS(3000)); //give time to the host to ping

        // ------------------------------- START WOLFSSL -------------------------------------------
        funcReturn = (BaseType_t) startWolfSSL();
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [target-server] Failed to start WolfSSL. [ret=%d]\n",funcReturn);
            vEXIT(1);
        } else {
            onPrintf (">>> WolfSSL started successfully!\n");
        }

        //-------------------------------- PART01: INBOUND ------------------------------------------
        #if (TESTGEN_TEST_PART == 1)
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

            for (int iAttempt=0; iAttempt<2; iAttempt++) { //just try twice

                // -------------------------------- START TCP listening socket --------------------------------
                uint8_t iPart[2] = {iAttempt, 0};
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

                // -------------------------------- CommunicateTCP is ready for the reply --------------------------------
                recvNotification = NOTIFY_FAIL;
                funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(30000)); //30 seconds timeout
                if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_SUCCESS))) {
                    onPrintf ("<INVALID> [target-server-%d] Failed to receive request. [ret=%d,notf=%lx]\n",iAttempt,funcReturn,recvNotification);
                    vEXIT(1);
                } else { 
                    onPrintf ("[%d]>>> Request received!\n",iAttempt);
                }

                // --------------------- reading the subject CN (username) --------------------------------
                char subjectCN[SUBJECT_CN_BUF_SIZE];
                size_t xBytesReceived = recvFromMsgBuffer ((void *) subjectCN, SUBJECT_CN_BUF_SIZE);
                if (xBytesReceived <= 0) {
                    onPrintf ("<INVALID> [target-server-%d]: Failed to obtain the client subject CN. [ret=%d]\n",iAttempt,xBytesReceived);
                    vEXIT(1);
                }
                subjectCN[xBytesReceived] = '\0'; //add the null termination

                // --------------------- Read the password --------------------------------
                char inPW[PW_SIZE];            
                xBytesReceived = recvFromMsgBuffer ((void *) inPW, PW_SIZE);
                if (xBytesReceived <= 0) {
                    onPrintf ("<INVALID> [target-server-%d]: Failed to obtain the client's password. [ret=%d]\n",iAttempt,xBytesReceived);
                    vEXIT(1);
                }
                inPW[xBytesReceived] = '\0'; //add the null termination

                // --------------------- Read the task handle --------------------------------
                TaskHandle_t xCommunicateTask;
                xBytesReceived = recvFromMsgBuffer ((void *) &xCommunicateTask, sizeof(TaskHandle_t *));
                if (xBytesReceived <= 0) {
                    onPrintf ("<INVALID> [target-server-%d]: Failed to obtain the xCommunicateTask handle. [ret=%d]\n",iAttempt,xBytesReceived);
                    vEXIT(1);
                }

                // --------------------- Get Service permission ------------------
                char replyToClient[7]; 
                uint8_t request = getServicePermission(subjectCN,inPW);
                if ( request == 2) {
                    onPrintf ("<GRANTED-ADMIN> [target-server-%d]: Admin service request accepted for <%s>\n",iAttempt,subjectCN);
                    strcpy (replyToClient,"ADMIN");
                } else if (request == 1) {
                    onPrintf ("<GRANTED-USER> [target-server-%d]: User service request accepted for <%s>\n",iAttempt,subjectCN);
                    strcpy (replyToClient,"USER");
                } else {
                    onPrintf ("<DENIED> [target-server-%d]: Service request denied for <%s>\n",iAttempt,subjectCN);
                    strcpy (replyToClient,"DENIED");
                }

                // --------------------- Reply message to the client ---------------------
                funcReturn = sendToMsgBuffer ((void *) replyToClient, strlen(replyToClient));
                if (funcReturn == uTRUE) {
                    onPrintf ("[%d]>>> Reply sent to msgBuf.\n",iAttempt);
                } else {
                    onPrintf ("<INVALID> [target-server-%d]: Failed to send reply to msgBuf.\n",iAttempt);
                    vEXIT(1);
                }

                // --------------------- Notify the xCommunicateTask --------------------------------
                funcReturn = xTaskNotify( xCommunicateTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
                if (funcReturn != pdPASS) {
                    onPrintf ("<INVALID> [target-server-%d]: Failed to notify <xCommunicateTask>!\n",iAttempt);
                    vEXIT(1);
                }

                // -------------------------------- Host (client) opened a connection --------------------------------
                recvNotification = NOTIFY_FAIL;
                funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(60000)); //60 seconds timeout
                if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
                    onPrintf ("<INVALID> [target-server-%d] Failed to connect to the client. [ret=%d,notf=%lx]\n",iAttempt,funcReturn,recvNotification);
                    vEXIT(1);
                } else if (recvNotification == NOTIFY_INVALIDAUTH) {
                    onPrintf ("<INVALID> [target-server-%d]: Failed to authenticate the client.\n",iAttempt);
                    vEXIT(1);
                } else { 
                    onPrintf ("[%d]>>> The connection with the client established successfully!\n",iAttempt);
                }
            } // end of attempts

        //-------------------------------- PART02: OUTBOUND ------------------------------------------
        #else
            // ------------------------------- INIT WOLFSSL CLIENT  -------------------------------------
            uint8_t useJediCert = uTRUE;
            funcReturn = xTaskCreate(vInitClientWolfSSL, "taskTest:initClientWolfSSL", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &useJediCert, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-client] Failed to create <taskTest:initClientWolfSSL>. [ret=%d].\n",funcReturn);
                vEXIT(1);
            } else {
                onPrintf (">>> Created <taskTest:initClientWolfSSL>.\n");
            }

            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-client] Failed to initialize WolfSSL client. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf (">>> WolfSSL client initialization successful!\n");
            }

            // -------------------------------- START TCP client socket --------------------------------
            uint8_t iPart[3] = {0, 0, 0}; //For compatibility
            funcReturn = xTaskCreate(vClientSocketTCP, "taskTest:clientSocketTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &iPart, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-client] Failed to create <taskTest:clientSocketTCP>. [ret=%d].\n",funcReturn);
                vEXIT(1);
            } else {
                onPrintf (">>> Created <taskTest:clientSocketTCP>.\n");
            }

            // -------------------------------- CommunicateTCP is ready for the reply --------------------------------
            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(30000)); //30 seconds timeout
            if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_SUCCESS))) {
                onPrintf ("<INVALID> [target-client] Failed to receive login prompt. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
                vEXIT(1);
            } else { 
                onPrintf (">>> Login prompt received!\n");
            }

            // --------------------- Read the task handle --------------------------------
            TaskHandle_t xCommunicateTask;
            size_t xBytesReceived = recvFromMsgBuffer ((void *) &xCommunicateTask, sizeof(TaskHandle_t *));
            if (xBytesReceived <= 0) {
                onPrintf ("<INVALID> [target-client]: Failed to obtain the xCommunicateTask handle. [ret=%d]\n",xBytesReceived);
                vEXIT(1);
            }

            // --------------------- Login Prompt ---------------------
            char adminUsername[] = "Jedi Order CLNT";
            char adminPassword[] = "joy@Work_1999";
            char loginSeparator[] = "/";
            char * loginCredentials = (char *) pvPortMalloc(strlen(adminUsername)+strlen(adminPassword)+strlen(loginSeparator)+1);
            strcpy (loginCredentials, adminUsername);
            strcat (loginCredentials, loginSeparator);
            strcat (loginCredentials, adminPassword);
            funcReturn = sendToMsgBuffer ((void *) loginCredentials, strlen(loginCredentials));
            if (funcReturn == uTRUE) {
                onPrintf (">>> Login credentials sent to msgBuf.\n");
            } else {
                onPrintf ("<INVALID> [target-client]: Failed to send login credentials to msgBuf.\n");
                vEXIT(1);
            }

            // --------------------- Notify the xCommunicateTask --------------------------------
            funcReturn = xTaskNotify( xCommunicateTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-client]: Failed to notify <xCommunicateTask>!\n");
                vEXIT(1);
            }

            // --------------------- xCommunicateTask has finished --------------------------------
            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(60000)); //60 seconds timeout
            if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
                onPrintf ("<INVALID> [target-client] Failed to connect to the server. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
                vEXIT(1);
            } else if (recvNotification == NOTIFY_INVALIDAUTH) {
                onPrintf ("<INVALID> [target-client]: Failed to authenticate the server.\n\n");
                vEXIT(1);
            } else { 
                onPrintf (">>> The connection with the server established successfully!\n");
            }        

        #endif //end of testparts

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

        vEXIT(0);
    } //vTask259


//---------------- Debian and FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

    #define THIS_TEST "259"

    #include <stdio.h>

    int main () {
        printf ("<INVALID> This test is not implemented yet.\n");
        return 1;
    }

#endif //end of if FreeRTOS