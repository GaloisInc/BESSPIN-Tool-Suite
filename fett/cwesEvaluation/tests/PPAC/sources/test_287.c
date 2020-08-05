/*
Test_287: Improper Authentication
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
NONE
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

    #define NUM_OF_TEST_PARTS 3 //test_287 has 3 parts

    //from extraSources
    extern uint8_t getServicePermission (const char * xActor);

    static void vTask287 (void *pvParameters);
    void main_test_287 (void);

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.
    
    void main (void) {
        BaseType_t funcReturn;
        funcReturn = xTaskCreate(vTask287, "main:task287", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task287>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task287>.\n");
        }

        vTaskStartScheduler(); //Hang the function
        return;
    }

    static void vTask287 (void *pvParameters) {
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

        // -------------------------------- START TCP listening socket --------------------------------
        uint8_t iPart[2] = {0, 0}; //for compatibility
        funcReturn = xTaskCreate(vServerSocketTCP, "taskTest:serverSocketTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &iPart, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [target-server] Failed to create <taskTest:serverSocketTCP>. [ret=%d].\n",funcReturn);
            vEXIT(1);
        } else {
            onPrintf (">>> Created <taskTest:serverSocketTCP>.\n");
        }

        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
        if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
            onPrintf ("<INVALID> [target-server] Failed to create a listening TCP server socket. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
            vEXIT(1);
        } else {
            onPrintf (">>> A listening TCP socket is opened successfully!\n<TCP-READY>\n");
        }

        // -------------------------------- Host (client) opened a connection --------------------------------
        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(60000)); //60 seconds timeout
        if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
            onPrintf ("<INVALID> [target-server] Failed to connect to the client. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
            vEXIT(1);
        } else if (recvNotification == NOTIFY_INVALIDAUTH) {
            onPrintf ("<INVALID> [target-server]: Failed to authenticate the client.\n");
        } else { 
            onPrintf (">>> The connection with the client established successfully!\n");
        }

        // --------------------- reading the subject CN --------------------------------
        char subjectCN[SUBJECT_CN_BUF_SIZE];
        size_t xBytesReceived = recvFromMsgBuffer ((void *) subjectCN, SUBJECT_CN_BUF_SIZE);
        if (xBytesReceived <= 0) {
            onPrintf ("<INVALID> [target-server]: Failed to obtain the client subject CN. [ret=%d]\n",xBytesReceived);
            vEXIT(1);
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
    } //vTask287

//---------------- Debian test ------------------------------------------------------
#elif defined(testgenOnDebian) || defined(testgenOnFreeBSD)

    #define THIS_TEST "287"

    #include <stdio.h>

    int main () {
        printf (">>> This test is fully bash interactive.\n");
        return 0;
    }
    
#endif //end of if FreeRTOS