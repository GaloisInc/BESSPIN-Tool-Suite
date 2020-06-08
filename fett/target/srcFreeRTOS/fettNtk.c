/*
Functions used for Network implementation on FreeRTOS
*/

#include "fettFreeRTOS.h"

// Declarations
void vStartNetwork (void *pvParameters);
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

// This task initializes the network and notify the mainTask
void vStartNetwork (void *pvParameters) {
    (void)pvParameters;
    BaseType_t funcReturn;
    xTaskStartNtk = xTaskGetCurrentTaskHandle();

    funcReturn = FreeRTOS_IPInit(ucIPAddress, ucNetMask, ucGatewayAddress, ucDNSServerAddress, ucMACAddress);
    ASSERT_OR_DELETE_TASK ((funcReturn == pdPASS), "startNetwork: Initialize Network IP.");

    // wait for NtkHook
    uint32_t recvNotification;
    funcReturn = xTaskNotifyWait(0xffffffff, 0xffffffff, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
    ASSERT_OR_DELETE_TASK ((funcReturn == pdPASS),
                           "startNetwork: Receive notification from hook.");
    ASSERT_OR_DELETE_TASK ((recvNotification == NOTIFY_SUCCESS_NTK),
                           "startNetwork: Expected notification value from hook.");

    fettPrintf ("\r\n<NTK-READY>\r\n");
    vTaskDelay(pdMS_TO_TICKS(3000)); //give time to the host to ping

    // notify main
    ASSERT_OR_DELETE_TASK((xMainTask != NULL), "startNetwork: Get handle of <main:task>.");
    funcReturn = xTaskNotify(xMainTask, NOTIFY_SUCCESS_NTK ,eSetBits);
    ASSERT_OR_DELETE_TASK((funcReturn == pdPASS), "startNetwork: Notify <main:task>.");

    vTaskDelete (NULL);
} //vStartNetwork

/* Called by FreeRTOS+TCP when the network connects or disconnects.  Disconnect
events are only received if implemented in the MAC driver. */
void vApplicationIPNetworkEventHook(eIPCallbackEvent_t eNetworkEvent) {
    fettPrintf ("(Info)~  NtkHook: A network event has been detected! (eventNum=%d).\r\n",eNetworkEvent);

    /* If the network has just come up...*/
    if ((eNetworkEvent == eNetworkUp) && (isNetworkUp == uFALSE)) //Network never was up
    {
        fettPrintf ("(Info)~  NtkHook: Network is up!\r\n");
        char cBuffer[16];
        uint32_t ulIPAddress, ulNetMask, ulGatewayAddress, ulDNSServerAddress;
        /* Print out the network configuration, which may have come from a DHCP
        server. */
        FreeRTOS_GetAddressConfiguration(&ulIPAddress, &ulNetMask, &ulGatewayAddress, &ulDNSServerAddress);
        FreeRTOS_inet_ntoa(ulIPAddress, cBuffer);
        fettPrintf("\t\tIP Address: %s\r\n", cBuffer);

        FreeRTOS_inet_ntoa(ulNetMask, cBuffer);
        fettPrintf("\t\tSubnet Mask: %s\r\n", cBuffer);

        FreeRTOS_inet_ntoa(ulGatewayAddress, cBuffer);
        fettPrintf("\t\tGateway Address: %s\r\n", cBuffer);

        FreeRTOS_inet_ntoa(ulDNSServerAddress, cBuffer);
        fettPrintf("\t\tDNS Server Address: %s\r\n\r\n", cBuffer);

        // Notify start netowork
        ASSERT_OR_DELETE_TASK ((xTaskStartNtk != NULL), "NtkHook: Get handle of <task:startNetwork>.");
        BaseType_t funcReturn = xTaskNotify(xTaskStartNtk, NOTIFY_SUCCESS_NTK ,eSetBits);
        ASSERT_OR_DELETE_TASK ((funcReturn == pdPASS), "NtkHook: Notify <task:startNetwork>.");

        isNetworkUp = uTRUE;
    } //network has just come up

    // HERE DETECTS IF THE NETWORK WENT DOWN
    ASSERT_OR_DELETE_TASK ((eNetworkEvent != eNetworkDown), "NtkHook: Check if network is down.");

} //vApplicationIPNetworkEventHook
