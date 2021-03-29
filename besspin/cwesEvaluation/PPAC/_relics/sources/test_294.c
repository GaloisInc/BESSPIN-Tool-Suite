/*
Test_294: Authentication Bypass by Spoofing
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
NONE
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

    #define NUM_OF_TEST_PARTS 2 //test_294 has 2 parts

    //from extraSources
    extern uint8_t getServicePermission (const char * xIP);

    static void vTask294 (void *pvParameters);
    void main_test_294 (void);
    void vCommunicateTCPdiffMessages (void *pvParameters);

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.
    
    void main (void) {
        BaseType_t funcReturn;

        startNetwork();

        funcReturn = xTaskCreate(vTask294, "main:task294", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task294>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task294>.\n");
        }

        return;
    }

    static void vTask294 (void *pvParameters) {
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

        // --------------------- reading the IP address --------------------------------
        char ipName[IP_NAME_SIZE];
        size_t xBytesReceived = recvFromMsgBuffer ((void *) ipName, IP_NAME_SIZE);
        if (xBytesReceived <= 0) {
            onPrintf ("<INVALID> [target-server]: Failed to obtain the client IP. [ret=%d]\n",xBytesReceived);
            vEXIT(1);
        }
        ipName[xBytesReceived] = '\0'; //add the null termination

        // ----------------- Get Service permission ------------
        if (getServicePermission(ipName) == uTRUE) {
            onPrintf ("<GRANTED> [target-server]: Service request accepted for <%s>\n",ipName);
        } else {
            onPrintf ("<DENIED> [target-server]: Service request denied for <%s>\n",ipName);
        }

        vEXIT(0);
    } //vTask294

    void vCommunicateTCPdiffMessages (void *pvParameters) {
        BaseType_t funcReturn;

        onPrintf ("<NOMSG-PATH> [vCommunicateTCPnoMessages]: Task started!\n");

        struct testgen_parentSocket *xParentSocketInfo = (struct testgen_parentSocket *)pvParameters;
        Socket_t xConnectedSocket = xParentSocketInfo->xConnectedSocket;
        if (xConnectedSocket == NULL) {
            onPrintf ("<INVALID> [vCommunicateTCPnoMessages]: Unable to get the handle of <xConnectedSocket>.\n");
            vEXIT(1);
        }
        TaskHandle_t xTaskParent = xParentSocketInfo->xTaskParent;
        if (xTaskParent == NULL) {
            onPrintf ("<INVALID> [vCommunicateTCPnoMessages]: Unable to get the handle of parent task.\n");
            vEXIT(1);
        }

        //notify parent task
        funcReturn = xTaskNotify( xTaskParent,  NOTIFY_CONNECTED ,eSetValueWithOverwrite);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [vCommunicateTCPnoMessages]: Failed to notify the parent task!\n");
            vEXIT(1);
        }

        /* Set a time out so that shutdown does not cause the task to block indefinitely. */
        const TickType_t xSndRecTimeOut = pdMS_TO_TICKS(1000); //1 seconds timeout
        funcReturn = FreeRTOS_setsockopt(xConnectedSocket, 0, FREERTOS_SO_RCVTIMEO, &xSndRecTimeOut, sizeof(xSndRecTimeOut));
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [vCommunicateTCPnoMessages]: Failed to setsockopt <FREERTOS_SO_RCVTIMEO>. [ret=%d].\n",funcReturn);
            vEXIT(1);
        }

        /* Initiate a shutdown */
        funcReturn = FreeRTOS_shutdown(xConnectedSocket, FREERTOS_SHUT_RDWR);
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [vCommunicateTCPnoMessages]: Failed to request socket shutdown. [ret=%d].\n",funcReturn);
            vEXIT(1);
        }

        /* Wait for the shutdown to take effect, indicated by FreeRTOS_recv() returning an error. */
        TickType_t xTimeOnShutdown = xTaskGetTickCount();
        do
        {
            vTaskDelay (pdMS_TO_TICKS(1000));
            funcReturn = FreeRTOS_recv(xConnectedSocket, NULL, ipconfigTCP_MSS, 0);
        } while ( (funcReturn >= 0) && ((xTaskGetTickCount() - xTimeOnShutdown) < pdMS_TO_TICKS(3000)));
        if (funcReturn > 0) {
            onPrintf ("<INVALID> [vCommunicateTCPnoMessages]: Failed to shutdown socket. [ret=%d].\n",funcReturn);
            vEXIT(1);
        } else if (funcReturn == 0) {
            onPrintf ("<WARNING> [vCommunicateTCPnoMessages]: Failed to properly shutdown socket.\n");
        }

        FreeRTOS_closesocket(xConnectedSocket); //This function always return 0

        vTaskDelete (NULL);
    } //vCommunicateTCPnoMessages

//---------------- Debian and FreeBSD test ------------------------------------------------------

#elif defined(testgenOnDebian) || defined(testgenOnFreeBSD)

    #define THIS_TEST "294"

    #include <stdio.h>

    int main () {
        printf (">>> This test is fully bash interactive.\n");
        return 0;
    }

#endif //end of if FreeRTOS