/* Standard includes. */
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

/* Kernel includes. */
#include "FreeRTOS.h"
#include "task.h"

/* IP stack includes. */
#include "FreeRTOS_IP.h"
#include "FreeRTOS_Sockets.h"

/* Drivers */
#include "iic.h"
#include "ads1015.h"

/* Canlib */
#include "canlib.h"
#include "j1939.h"

/* FETT config */
#include "fettFreeRTOSConfig.h"

#if !(BSP_USE_IIC0)
#error "One or more peripherals are nor present, this test cannot be run"
#endif

void main_fett(void);

#define CYBERPHYS_BROADCAST_ADDR "10.88.88.255"

#define SENSORTASK_STACK_SIZE configMINIMAL_STACK_SIZE * 10U
#define CAN_TX_STACK_SIZE configMINIMAL_STACK_SIZE * 10U
#define CAN_RX_STACK_SIZE configMINIMAL_STACK_SIZE * 10U

#define SENSORTASK_PRIORITY tskIDLE_PRIORITY + 5
#define CAN_RX_TASK_PRIORITY tskIDLE_PRIORITY + 5
#define CAN_TX_TASK_PRIORITY tskIDLE_PRIORITY + 5

#define CAN_RX_PORT (5001UL)
#define CAN_TX_PORT (5002UL)

#define SENSOR_LOOP_DELAY_MS pdMS_TO_TICKS(1000)

#define THROTTLE_ADC_CHANNEL 0
#define BRAKE_ADC_CHANNEL 1

#define THROTTLE_MAX 925 // fully pressed
#define THROTTLE_MIN 109

#define BRAKE_MAX 923
#define BRAKE_MIN 109

#define SHIFTER_I2C_ADDRESS 0x30

static void prvSensorTask(void *pvParameters);
static void prvCanTxTask(void *pvParameters);
static void prvCanRxTask(void *pvParameters);

uint8_t throttle;
uint16_t throttle_raw;
uint16_t throttle_scaling_factor;
uint8_t brake;
uint16_t brake_raw;
uint16_t brake_scaling_factor;
uint8_t gear;

static const uint8_t ucIPAddress[4] = {configIP_ADDR0, configIP_ADDR1, configIP_ADDR2, configIP_ADDR3};
static const uint8_t ucNetMask[4] = {configNET_MASK0, configNET_MASK1, configNET_MASK2, configNET_MASK3};
static const uint8_t ucGatewayAddress[4] = {configGATEWAY_ADDR0, configGATEWAY_ADDR1, configGATEWAY_ADDR2, configGATEWAY_ADDR3};
static const uint8_t ucDNSServerAddress[4] = {configDNS_SERVER_ADDR0, configDNS_SERVER_ADDR1, configDNS_SERVER_ADDR2, configDNS_SERVER_ADDR3};
const uint8_t ucMACAddress[6] = {configMAC_ADDR0, configMAC_ADDR1, configMAC_ADDR2, configMAC_ADDR3, configMAC_ADDR4, configMAC_ADDR5};

void main_fett(void)
{
    xTaskCreate(prvSensorTask, "prvSensorTask", SENSORTASK_STACK_SIZE, NULL, SENSORTASK_PRIORITY, NULL);

    FreeRTOS_printf((">>> ECU: FreeRTOS_IPInit\r\n"));
    FreeRTOS_IPInit(ucIPAddress, ucNetMask, ucGatewayAddress, ucDNSServerAddress, ucMACAddress);
}

static void prvSensorTask(void *pvParameters)
{
    (void)pvParameters;

    printf(">>> ECU: Starting prvSensorTask\r\n");

    // Give the sensor time to power up
    vTaskDelay(pdMS_TO_TICKS(100));

    for (;;)
    {
        throttle_raw = ads1015_get_channel(THROTTLE_ADC_CHANNEL);
        brake_raw = ads1015_get_channel(BRAKE_ADC_CHANNEL);

        throttle = (uint8_t)((throttle_raw - THROTTLE_MIN) * 255 / (THROTTLE_MAX - THROTTLE_MIN));
        brake = (uint8_t)((brake_raw - BRAKE_MIN) * 255 / (BRAKE_MAX - BRAKE_MIN));

        configASSERT(iic_receive(&Iic0, SHIFTER_I2C_ADDRESS, &gear, 1) != -1);

        FreeRTOS_printf((">>> ECU Gear: %#x, throttle: %u, brake: %u\r\n", gear, throttle, brake));

        /* Place this task in the blocked state until it is time to run again. */
        vTaskDelay(SENSOR_LOOP_DELAY_MS);
    }
}

/* Called by FreeRTOS+TCP when the network connects or disconnects.  Disconnect
events are only received if implemented in the MAC driver. */
void vApplicationIPNetworkEventHook(eIPCallbackEvent_t eNetworkEvent)
{
    uint32_t ulIPAddress, ulNetMask, ulGatewayAddress, ulDNSServerAddress;
    char cBuffer[16];
    uint64_t ulsPort;
    static BaseType_t xTasksAlreadyCreated = pdFALSE;

    /* If the network has just come up...*/
    if (eNetworkEvent == eNetworkUp)
    {
        /* Create the tasks that use the IP stack if they have not already been
		created. */
        if (xTasksAlreadyCreated == pdFALSE)
        {
            ulsPort = CAN_TX_PORT;
            xTaskCreate(prvCanTxTask, "prvCanTxTask", CAN_TX_STACK_SIZE, (void *)ulsPort, CAN_TX_TASK_PRIORITY, NULL);
            ulsPort = CAN_RX_PORT;
            xTaskCreate(prvCanRxTask, "prvCanRxTask", CAN_RX_STACK_SIZE, (void *)ulsPort, CAN_RX_TASK_PRIORITY, NULL);
            xTasksAlreadyCreated = pdTRUE;
        }

        /* Print out the network configuration, which may have come from a DHCP
		server. */
        FreeRTOS_GetAddressConfiguration(&ulIPAddress, &ulNetMask, &ulGatewayAddress, &ulDNSServerAddress);
        FreeRTOS_inet_ntoa(ulIPAddress, cBuffer);
        FreeRTOS_printf(("\r\n\r\n>>> ECIU: IP Address: %s\r\n", cBuffer));

        FreeRTOS_inet_ntoa(ulNetMask, cBuffer);
        FreeRTOS_printf((">>> ECU: Subnet Mask: %s\r\n", cBuffer));

        FreeRTOS_inet_ntoa(ulGatewayAddress, cBuffer);
        FreeRTOS_printf((">>> ECU: Gateway Address: %s\r\n", cBuffer));

        FreeRTOS_inet_ntoa(ulDNSServerAddress, cBuffer);
        FreeRTOS_printf((">>> ECU: DNS Server Address: %s\r\n\r\n\r\n", cBuffer));

        // For compliance with FETT tool
        FreeRTOS_printf((">>>Beginning of Fett<<<\r\n"));
        FreeRTOS_printf(("<NTK-READY>\r\n"));
    }
}
/*-----------------------------------------------------------*/

static void prvCanRxTask(void *pvParameters)
{
    Socket_t xListeningSocket;
    uint32_t ulIPAddress;
    struct freertos_sockaddr xClient, xBindAddress;
    char msg[128];
    memset(msg, 0xEE, sizeof(msg));
    size_t msg_len;
    char cBuffer[16];

    FreeRTOS_printf((">>> ECU: Starting prvCanRxTask\r\n"));

    /* Attempt to open the socket. */
    xListeningSocket = FreeRTOS_socket(FREERTOS_AF_INET, FREERTOS_SOCK_DGRAM, FREERTOS_IPPROTO_UDP);
    configASSERT(xListeningSocket != FREERTOS_INVALID_SOCKET);

    /* This test receives data sent from a different port on the same IP address.
	Obtain the nodes IP address.  Configure the freertos_sockaddr structure with
	the address being bound to.  The strange casting is to try and remove
	compiler warnings on 32 bit machines.  Note that this task is only created
	after the network is up, so the IP address is valid here. */
    FreeRTOS_GetAddressConfiguration(&ulIPAddress, NULL, NULL, NULL);
    xBindAddress.sin_addr = ulIPAddress;
    xBindAddress.sin_port = (uint16_t)((uint64_t)pvParameters) & 0xffffUL;
    xBindAddress.sin_port = FreeRTOS_htons(xBindAddress.sin_port);

    /* Bind the socket to the port that the client task will send to. */
    FreeRTOS_bind(xListeningSocket, &xBindAddress, sizeof(xBindAddress));

    FreeRTOS_inet_ntoa(xBindAddress.sin_addr, cBuffer);
    FreeRTOS_printf((">>> ECU bound to addr %s:%u\r\n", cBuffer, pvParameters));

    for (;;)
    {
        uint8_t res = recv_can_message(xListeningSocket, &xClient, msg, &msg_len);
        if (res == SUCCESS)
        {
            FreeRTOS_inet_ntoa(xClient.sin_addr, cBuffer);
            FreeRTOS_printf((">>> ECU recv_can_message %u bytes from %s:%u\r\n", msg_len, cBuffer, FreeRTOS_ntohs(xClient.sin_port)));
        }
        else
        {
            FreeRTOS_printf((">>> ECU recv_can_message returned %u\r\n", res));
        }
    }
}

static void prvCanTxTask(void *pvParameters)
{
    uint32_t ulIPAddress;
    Socket_t xClientSocket;
    struct freertos_sockaddr xDestinationAddress;
    FreeRTOS_GetAddressConfiguration(&ulIPAddress, NULL, NULL, NULL);
    // Broadcast address
    xDestinationAddress.sin_addr = FreeRTOS_inet_addr(CYBERPHYS_BROADCAST_ADDR);
    xDestinationAddress.sin_port = (uint16_t)((uint64_t)pvParameters) & 0xffffUL;
    xDestinationAddress.sin_port = FreeRTOS_htons(xDestinationAddress.sin_port);

    FreeRTOS_printf((">>> ECU: Starting prvCanTxTask\r\n"));

    xClientSocket = FreeRTOS_socket(FREERTOS_AF_INET, FREERTOS_SOCK_DGRAM, FREERTOS_IPPROTO_UDP);
    configASSERT(xClientSocket != FREERTOS_INVALID_SOCKET);

    FreeRTOS_printf((">>> ECU prvCanTxTask socket connected\r\n"));

    for (;;)
    {
        // Send throttle
        if (send_can_message(xClientSocket, &xDestinationAddress, PGN_THROTTLE_INPUT, (void *)&throttle, sizeof(throttle)) != SUCCESS)
        {
            FreeRTOS_printf((">>> ECU sent throttle failed\r\n"));
        }
        // Send brake
        if (send_can_message(xClientSocket, &xDestinationAddress, PGN_BRAKE_INTPUT, (void *)&brake, sizeof(brake)) != SUCCESS)
        {
            FreeRTOS_printf((">>> ECU sent brake failed\r\n"));
        }
        // Send gear
        if (send_can_message(xClientSocket, &xDestinationAddress, PGN_GEAR, (void *)&gear, sizeof(gear)) != SUCCESS)
        {
            FreeRTOS_printf((">>> ECU sent gear failed\r\n"));
        }
        vTaskDelay(SENSOR_LOOP_DELAY_MS);
    }
}

