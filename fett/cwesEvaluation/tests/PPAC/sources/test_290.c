/*
Test_290: Authentication Bypass by Spoofing
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
NONE
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

    #define NUM_OF_TEST_PARTS 2 //test_290 has 2 parts

    //from extraSources
    extern uint8_t getServicePermission (const char * xActor, const char * xIP);

    static void vTask290 (void *pvParameters);
    void main_test_290 (void);

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.
    
    void main (void) {
        BaseType_t funcReturn;
        funcReturn = xTaskCreate(vTask290, "main:task290", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task290>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task290>.\n");
        }

        vTaskStartScheduler(); //Hang the function
        return;
    }

    static void vTask290 (void *pvParameters) {
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

        // ------------------------------- START UDP Listening socket -----------------------
        Socket_t xListeningSocket = FreeRTOS_socket(FREERTOS_AF_INET, FREERTOS_SOCK_DGRAM, FREERTOS_IPPROTO_UDP);
        if (xListeningSocket == FREERTOS_INVALID_SOCKET) {
            onPrintf ("<INVALID> [target-server]: Failed to open the socket.\n");
            vEXIT(1);
        } else {
            onPrintf (">>> Socket opened!\n");
        }

        /* Set a time out so accept() will just wait for a connection. */
        const TickType_t xReceiveTimeOut = pdMS_TO_TICKS(120000); //enough time to insert the sudo password
        funcReturn = FreeRTOS_setsockopt(xListeningSocket, 0, FREERTOS_SO_RCVTIMEO, &xReceiveTimeOut, sizeof(xReceiveTimeOut));
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [target-server]: Failed to setsockopt <FREERTOS_SO_RCVTIMEO>. [ret=%d].\n",funcReturn);
            vEXIT(1);
        }

        /* Bind the socket to the port that the client task will send to */ 
        struct freertos_sockaddr xBindAddr;
        xBindAddr.sin_port = FreeRTOS_htons(TCP_PORT_NUMBER);
        funcReturn = FreeRTOS_bind(xListeningSocket, &xBindAddr, sizeof(xBindAddr));
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [target-server]: Failed to bind the socket to the port number. [ret=%d].\n",funcReturn);
            vEXIT(1);
        } else {
            onPrintf (">>> Socket bound to port <%d>!\n",TCP_PORT_NUMBER);
        }

        /* Allocate a buffer for receiving a message */
        uint8_t *rxBuffer = (uint8_t *)pvPortMalloc(ipconfigTCP_MSS);
        if (rxBuffer == NULL) {
            onPrintf ("<INVALID> [target-server]: Malloc error while allocating <rxBuffer>.\n");
            vEXIT(1);
        }
        /* Zero out the receive array so there is NULL at the end of the string when it is printed out. */
        memset(rxBuffer, 0x00, ipconfigTCP_MSS);
        struct freertos_sockaddr xClientAddr;
        socklen_t xClientSize = sizeof(xClientAddr);

        onPrintf ("\n<UDP-READY>\n");
        int32_t nBytes = FreeRTOS_recvfrom(xListeningSocket, rxBuffer, ipconfigTCP_MSS, 0, &xClientAddr, &xClientSize);
        if (nBytes <= 0) {
            onPrintf ("<INVALID> [target-server]: Failed to receive data from the connection. [nBytes=%d].\n",nBytes);
        } else {
            onPrintf (">>> [target-server]: Received [%d Bytes]:\n%s:<TARGET-RECV>\n",nBytes,rxBuffer);
        }

        // --------------------- reading the IP address --------------------------------
        char ipName[IP_NAME_SIZE];
        FreeRTOS_inet_ntoa( xClientAddr.sin_addr, ipName );
        onPrintf("[target-server]: IP address of incoming connection is: <%s>\n", ipName);

        // ----------------- Get Service permission ------------
        if (getServicePermission(rxBuffer,ipName) == uTRUE) {
            onPrintf ("<GRANTED> [target-server]: Service request accepted for <%s>\n",rxBuffer);
        } else {
            onPrintf ("<DENIED> [target-server]: Service request denied for <%s>\n",rxBuffer);
        }

        FreeRTOS_closesocket(xListeningSocket); //This function always return 0
        vPortFree (rxBuffer);
        vEXIT(0);
    } //vTask290

//---------------- Debian and FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

    #define THIS_TEST "290"

    #include <stdio.h>

    int main () {
        printf ("<Not-Implemented> This is covered by TEST-294.\n");
        return 1;
    }

#endif //end of if FreeRTOS