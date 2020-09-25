/*
Functions used for Network implementation on FreeRTOS
*/

#include "fettFreeRTOS.h"

// Declarations
void startNetwork (void);
static uint8_t isNetworkUp = uFALSE; //To know whether the network was up before

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

void startNetwork () {
    BaseType_t funcReturn;

    funcReturn = FreeRTOS_IPInit(ucIPAddress, ucNetMask, ucGatewayAddress, ucDNSServerAddress, ucMACAddress);
    if (funcReturn != pdPASS) {
        fettPrintf ("(Error)~  startNetwork: Failed to initialize network. [ret=%d].\n",funcReturn);
        exitFett(1);
    } else {
        fettPrintf ("(Info)~  startNetwork: Network IP initialized successfully!.\n");
    }
}

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

        // notify main
        if (xMainTask == NULL) {
            fettPrintf ("(Error)~  NtkHook: Unable to get the handle of <main:task>.\n");
            exitFett (1);
        }
        BaseType_t funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS_NTK ,eSetBits);
        if (funcReturn != pdPASS) {
            fettPrintf ("(Error)~  NtkHook: Failed to notify <main:task>!\n");
            exitFett (1);
        }

        isNetworkUp = uTRUE;
    } //network has just come up

    // HERE DETECTS IF THE NETWORK WENT DOWN 
    if (eNetworkEvent == eNetworkDown) {
        fettPrintf ("(Error)~ NtkHook: Network is Down!\n");
        exitFett (1);
    }

} //vApplicationIPNetworkEventHook
