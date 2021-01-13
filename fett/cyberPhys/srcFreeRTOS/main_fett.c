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
#include "bsp.h"
#include "iic.h"

/* Canlib */
#include "canlib.h"
#include "j1939.h"

/* FETT config */
#include "fettFreeRTOSConfig.h"

#if !(BSP_USE_IIC0)
#error "One or more peripherals are nor present, this test cannot be run"
#endif

#define STRINGIZE_NX(A) #A
#define STRINGIZE(A) STRINGIZE_NX(A)
#define CYBERPHYS_BROADCAST_ADDR STRINGIZE(configGATEWAY_ADDR0) \
"." STRINGIZE(configGATEWAY_ADDR1) "." STRINGIZE(configGATEWAY_ADDR2) ".255"

#define MAINTASK_STACK_SIZE configMINIMAL_STACK_SIZE * 10U
#define SENSORTASK_STACK_SIZE configMINIMAL_STACK_SIZE * 10U
#define CAN_TX_STACK_SIZE configMINIMAL_STACK_SIZE * 10U
#define CAN_RX_STACK_SIZE configMINIMAL_STACK_SIZE * 10U
#define INFOTASK_STACK_SIZE configMINIMAL_STACK_SIZE * 10U

#define MAINTASK_PRIORITY tskIDLE_PRIORITY + 5
#define SENSORTASK_PRIORITY tskIDLE_PRIORITY + 4
#define CAN_RX_TASK_PRIORITY tskIDLE_PRIORITY + 3
#define CAN_TX_TASK_PRIORITY tskIDLE_PRIORITY + 2
#define INFOTASK_PRIORITY tskIDLE_PRIORITY + 1

#define CAN_RX_PORT (5001UL)
#define CAN_TX_PORT (5002UL)

#define SENSOR_LOOP_DELAY_MS pdMS_TO_TICKS(10)

#define SENSOR_POWER_UP_DELAY_MS pdMS_TO_TICKS(100)
#define BROADCAST_LOOP_DELAY_MS pdMS_TO_TICKS(50)
#define INFOTASK_LOOP_DELAY_MS pdMS_TO_TICKS(1000)

#define THROTTLE_MAX 926 // fully pressed
#define THROTTLE_MIN 64
#define THROTTLE_GAIN 100

#define BRAKE_MAX 525
#define BRAKE_MIN 456
#define BRAKE_GAIN 100

#define TEENSY_I2C_ADDRESS 0x30

#define NOTIFY_SUCCESS_NTK  0x00000001

static void prvSensorTask(void *pvParameters);
static void prvCanTxTask(void *pvParameters);
static void prvCanRxTask(void *pvParameters);
static void prvInfoTask(void *pvParameters);

void main_fett(void);
void prvMainTask (void *pvParameters);
void startNetwork(void);
char *getCurrTime(void);
uint8_t process_j1939(Socket_t xListeningSocket, struct freertos_sockaddr *xClient, size_t *msg_len);
int16_t min(int16_t a, int16_t b);
int16_t max(int16_t a, int16_t b);

uint32_t ulApplicationGetNextSequenceNumber(uint32_t ulSourceAddress, uint16_t usSourcePort,
                                            uint32_t ulDestinationAddress, uint16_t usDestinationPort);

SemaphoreHandle_t data_mutex;
TaskHandle_t xMainTask = NULL;

/* CAN rx buffer */
uint8_t j1939_rx_buf[0x64] __attribute__((aligned(64)));

/* Stereing assist config */
bool camera_ok;
uint8_t steering_assist;

/* Gains */
int16_t throttle_gain;
int16_t brake_gain;
int16_t throttle_min;
int16_t throttle_max;
int16_t brake_min;
int16_t brake_max;

/* Raw readings */
int16_t throttle_raw;
uint8_t gear_raw;
int16_t brake_raw;

/* Final values */
uint8_t throttle;
uint8_t brake;
uint8_t gear;

/* Debug info */
uint32_t hz_sensor_task;
uint32_t hz_sensor_throttle_task;
uint32_t hz_cantx_task;

/* Network config variables */
static const uint8_t ucIPAddress[4] = {configIP_ADDR0, configIP_ADDR1, configIP_ADDR2, configIP_ADDR3};
static const uint8_t ucNetMask[4] = {configNET_MASK0, configNET_MASK1, configNET_MASK2, configNET_MASK3};
static const uint8_t ucGatewayAddress[4] = {configGATEWAY_ADDR0, configGATEWAY_ADDR1, configGATEWAY_ADDR2, configGATEWAY_ADDR3};
static const uint8_t ucDNSServerAddress[4] = {configDNS_SERVER_ADDR0, configDNS_SERVER_ADDR1, configDNS_SERVER_ADDR2, configDNS_SERVER_ADDR3};
const uint8_t ucMACAddress[6] = {configMAC_ADDR0, configMAC_ADDR1, configMAC_ADDR2, configMAC_ADDR3, configMAC_ADDR4, configMAC_ADDR5};

/* Global network settings */
Socket_t xClientSocket;
struct freertos_sockaddr xDestinationAddress;

/* Auxilliary function */
int16_t min(int16_t a, int16_t b)
{
    if (a > b)
    {
        return b;
    }
    else
    {
        return a;
    }
}

/* Auxilliary function */
int16_t max(int16_t a, int16_t b)
{
    if (a > b)
    {
        return a;
    }
    else
    {
        return b;
    }
}

/**
 * Print uptime in human readable format
 * "HH:MM:SS"
 */
char *getCurrTime(void)
{
#ifdef USE_CURRENT_TIME
    static char buf[16] = {0};
    TickType_t t = xTaskGetTickCount();
    uint32_t n_seconds = t / configTICK_RATE_HZ;
    uint32_t n_ms = t - n_seconds * configTICK_RATE_HZ;
    n_ms = (n_ms * 1000) / configTICK_RATE_HZ;
    uint32_t n_minutes = n_seconds / 60;
    uint32_t n_hours = n_minutes / 60;

    n_minutes = n_minutes - n_hours * 60;
    n_seconds = n_seconds - n_minutes * 60;

    sprintf(buf, "%02u:%02u:%02u.%03u", n_hours, n_minutes, n_seconds, n_ms);
    return buf;
#else
    return "";
#endif
}

/*
--- This function is called by FreeRTOS_TCP_IP.c. This is a dirty implementation
 * Callback that provides the inputs necessary to generate a randomized TCP
 * Initial Sequence Number per RFC 6528.  THIS IS ONLY A DUMMY IMPLEMENTATION
 * THAT RETURNS A PSEUDO RANDOM NUMBER SO IS NOT INTENDED FOR USE IN PRODUCTION
 * SYSTEMS.
 */
uint32_t ulApplicationGetNextSequenceNumber(uint32_t ulSourceAddress,
                                            uint16_t usSourcePort,
                                            uint32_t ulDestinationAddress,
                                            uint16_t usDestinationPort)
{
    (void)ulSourceAddress;
    (void)usSourcePort;
    (void)ulDestinationAddress;
    (void)usDestinationPort;

    return uxRand();
}

void startNetwork()
{
    BaseType_t funcReturn;

    funcReturn = FreeRTOS_IPInit(ucIPAddress, ucNetMask, ucGatewayAddress, ucDNSServerAddress, ucMACAddress);
    if (funcReturn != pdPASS)
    {
        FreeRTOS_printf(("%s (Error)~  startNetwork: Failed to initialize network. [ret=%d].\r\n", getCurrTime(), funcReturn));
    }
    else
    {
        FreeRTOS_printf(("%s (Info)~  startNetwork: Network IP initialized successfully!.\r\n", getCurrTime()));
    }

    FreeRTOS_printf((">>>%s ECU: FreeRTOS_IPInit\r\n", getCurrTime()));
}

void main_fett(void)
{
    BaseType_t funcReturn;

    FreeRTOS_printf(("\n>>>Beginning of Fett<<<\r\n"));
    
    startNetwork();

    funcReturn = xTaskCreate(prvMainTask, "prvMainTask", MAINTASK_STACK_SIZE, NULL, MAINTASK_PRIORITY, NULL);

    if (funcReturn == pdPASS) {
        FreeRTOS_printf (("(Info)~  main_fett: Created prvMainTask successfully.\n"));
    } else {
        FreeRTOS_printf (("(Error)~  main_fett: Failed to create prvMainTask.\n"));
    }
}

void prvMainTask (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;
    uint32_t recvNotification = 0;

    xMainTask = xTaskGetCurrentTaskHandle();

    funcReturn = xTaskNotifyWait(0xffffffffUL, 0xffffffffUL, &recvNotification, pdMS_TO_TICKS(20000)); //it should take less than 15s
    if (funcReturn != pdPASS) {
        FreeRTOS_printf (("(Error)~  prvMainTask: Failed to receive a notification.\n"));
        vTaskDelete(NULL);
    } else if (recvNotification != NOTIFY_SUCCESS_NTK) {
        FreeRTOS_printf (("(Error)~  prvMainTask: Unexpected notification value <%08x>.\n",recvNotification));
        vTaskDelete(NULL);
    } else {
        // For compliance with FETT tool
        FreeRTOS_printf(("<NTK-READY>\r\n"));
    }
    
    /* Initialize mutex */
    data_mutex = xSemaphoreCreateMutex();
    configASSERT(data_mutex != NULL);

    /* Camera is not connected, don't use */
    camera_ok = FALSE;

    funcReturn = xTaskCreate(prvInfoTask, "prvInfoTask", INFOTASK_STACK_SIZE, NULL, INFOTASK_PRIORITY, NULL);
    if (funcReturn == pdPASS) {
        FreeRTOS_printf (("(Info)~  prvMainTask: Created prvInfoTask successfully.\n"));
    } else {
        FreeRTOS_printf (("(Error)~  prvMainTask: Failed to create prvInfoTask.\n"));
    }

    vTaskDelete(NULL);
}

static void prvInfoTask(void *pvParameters)
{
    (void)pvParameters;
    int16_t local_throttle, local_brake;
    int16_t local_throttle_raw, local_brake_raw;
    uint8_t local_gear;
    uint32_t hz_sensor_task_old = 0;
    uint32_t hz_cantx_task_old = 0;

    FreeRTOS_printf((">>>%s Starting prvInfoTask\r\n", getCurrTime()));

    for (;;)
    {
        /* Copy data over */
        if (xSemaphoreTake(data_mutex, pdMS_TO_TICKS(100)) == pdTRUE)
        {
            local_throttle_raw = throttle_raw;
            local_brake_raw = brake_raw;
            local_throttle = throttle;
            local_brake = brake;
            local_gear = gear;
            xSemaphoreGive(data_mutex);
        }
        FreeRTOS_printf((">>>%s (prvInfoTask:raw) throttle: %d, brake: %d\r\n", getCurrTime(), local_throttle_raw, local_brake_raw));
        FreeRTOS_printf((">>>%s (prvInfoTask:scaled) Gear: %#x, throttle: %u, brake: %u\r\n", getCurrTime(), local_gear, local_throttle, local_brake));
        FreeRTOS_printf((">>>%s (prvInfoTask:hz) prvSensorTask: %u[Hz]\r\n", getCurrTime(), hz_sensor_task - hz_sensor_task_old));
        FreeRTOS_printf((">>>%s (prvInfoTask:hz) prvCanTxTask: %u[Hz]\r\n", getCurrTime(), hz_cantx_task - hz_cantx_task_old));
        hz_sensor_task_old = hz_sensor_task;
        hz_cantx_task_old = hz_cantx_task;

        if (camera_ok)
        {
            FreeRTOS_printf((">>>%s (prvInfoTask:LKAS) Camera OK: %d, steering_assist: %d\r\n", getCurrTime(), camera_ok, steering_assist));
        }

        vTaskDelay(INFOTASK_LOOP_DELAY_MS);
    }
}

// State machine
enum teensy_state
{
    GEAR = 1,
    THROTTLE = 2,
    BRAKE = 3,
};

/**
 * Read and update gear values
 */
static void prvSensorTask(void *pvParameters)
{
    (void)pvParameters;

    hz_sensor_task = 0;
    uint8_t state;

    // Gear variables
    uint8_t tmp_gear;

    // Throttle variables
    int16_t tmp_throttle;
    hz_sensor_throttle_task = 0;
    throttle_gain = THROTTLE_GAIN;
    throttle_min = THROTTLE_MIN;
    throttle_max = THROTTLE_MAX;

    // Brake variables
    int16_t tmp_brake;
    hz_cantx_task = 0;
    brake_gain = BRAKE_GAIN;
    brake_min = BRAKE_MIN;
    brake_max = BRAKE_MAX;

    FreeRTOS_printf((">>>%s Starting prvSensorTask\r\n", getCurrTime()));

    // Give the sensor time to power up
    vTaskDelay(SENSOR_POWER_UP_DELAY_MS);

    for (;;)
    {
        hz_sensor_task++;

        /* Request gear */
        state = GEAR;
        configASSERT(iic_transmit(&Iic0, TEENSY_I2C_ADDRESS, &state, 1) != -1);
        vTaskDelay(pdMS_TO_TICKS(1));
        configASSERT(iic_receive(&Iic0, TEENSY_I2C_ADDRESS, &tmp_gear, 1) != -1);
        vTaskDelay(pdMS_TO_TICKS(1));

        switch (tmp_gear)
        {
        case 0x28:
            tmp_gear = 'P';
            break;
        case 0x27:
            tmp_gear = 'R';
            break;
        case 0x26:
            tmp_gear = 'N';
            break;
        case 0x25:
            tmp_gear = 'D';
            break;
        default:
            FreeRTOS_printf((">>>%s (prvSensorTask) unknown gear value: %c\r\n", getCurrTime(), gear_raw));
            break;
        }

        /* Request throttle */
        state = THROTTLE;
        configASSERT(iic_transmit(&Iic0, TEENSY_I2C_ADDRESS, &state, 1) != -1);
        vTaskDelay(pdMS_TO_TICKS(1));
        configASSERT(iic_receive(&Iic0, TEENSY_I2C_ADDRESS, &throttle_raw, 2) != -1);
        vTaskDelay(pdMS_TO_TICKS(1));

        tmp_throttle = max(throttle_raw - throttle_min, 0); // remove offset
        tmp_throttle = tmp_throttle * throttle_gain / (throttle_max - throttle_min);
        tmp_throttle = min(max(tmp_throttle, 0), 100);

        /* Request brake */
        state = BRAKE;
        configASSERT(iic_transmit(&Iic0, TEENSY_I2C_ADDRESS, &state, 1) != -1);
        vTaskDelay(pdMS_TO_TICKS(1));
        configASSERT(iic_receive(&Iic0, TEENSY_I2C_ADDRESS, &brake_raw, 2) != -1);
        vTaskDelay(pdMS_TO_TICKS(1));

        tmp_brake = max(brake_max - brake_raw, 0); // reverse brake
        tmp_brake = tmp_brake * brake_gain / (brake_max - brake_min);
        tmp_brake = min(max(tmp_brake, 0), 100);

        if (xSemaphoreTake(data_mutex, pdMS_TO_TICKS(100)) == pdTRUE)
        {
            gear = (uint8_t)tmp_gear;
            throttle = (uint8_t)tmp_throttle;
            brake = (uint8_t)tmp_brake;
            xSemaphoreGive(data_mutex);
        }

        vTaskDelay(SENSOR_LOOP_DELAY_MS);
    }
}

/* Called by FreeRTOS+TCP when the network connects or disconnects.  Disconnect
events are only received if implemented in the MAC driver. */
void vApplicationIPNetworkEventHook(eIPCallbackEvent_t eNetworkEvent)
{
    uint32_t ulIPAddress, ulNetMask, ulGatewayAddress, ulDNSServerAddress;
    char cBuffer[16];
    static BaseType_t xTasksAlreadyCreated = pdFALSE;
    BaseType_t funcReturn;

    /* If the network has just come up...*/
    if (eNetworkEvent == eNetworkUp)
    {

        /* Create the tasks that use the IP stack if they have not already been
		created. */
        /*
        if (xTasksAlreadyCreated == pdFALSE)
        {
            // Configure TX addr 
            xDestinationAddress.sin_addr = FreeRTOS_inet_addr(CYBERPHYS_BROADCAST_ADDR);
            xDestinationAddress.sin_port = (uint16_t)(CAN_TX_PORT);
            xDestinationAddress.sin_port = FreeRTOS_htons(xDestinationAddress.sin_port);
            xClientSocket = FreeRTOS_socket(FREERTOS_AF_INET, FREERTOS_SOCK_DGRAM, FREERTOS_IPPROTO_UDP);
            configASSERT(xClientSocket != FREERTOS_INVALID_SOCKET);

            xTaskCreate(prvSensorTask, "prvSensorTask", SENSORTASK_STACK_SIZE, NULL, SENSORTASK_PRIORITY, NULL);
            xTaskCreate(prvCanTxTask, "prvCanTxTask", CAN_TX_STACK_SIZE, NULL, CAN_TX_TASK_PRIORITY, NULL);
            xTaskCreate(prvCanRxTask, "prvCanRxTask", CAN_RX_STACK_SIZE, NULL, CAN_RX_TASK_PRIORITY, NULL);

            xTasksAlreadyCreated = pdTRUE;
        }*/

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

        // notify main
        if (xMainTask == NULL) {
            FreeRTOS_printf(("(Error)~  NtkHook: Unable to get the handle of <prvMainTask>.\n"));
        }
        funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS_NTK ,eSetBits);
        if (funcReturn != pdPASS) {
            FreeRTOS_printf(("(Error)~  NtkHook: Failed to notify <prvMainTask>!\n"));
        }
    }
}
/*-----------------------------------------------------------*/

static void prvCanRxTask(void *pvParameters)
{
    (void)pvParameters;
    char cBuffer[16];
    Socket_t xListeningSocket;
    uint32_t ulIPAddress;
    struct freertos_sockaddr xBindAddress;
    struct freertos_sockaddr xClient;
    size_t msg_len;

    FreeRTOS_printf((">>>%s Starting prvCanRxTask\r\n", getCurrTime()));

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
    xBindAddress.sin_port = (uint16_t)(CAN_RX_PORT);
    xBindAddress.sin_port = FreeRTOS_htons(xBindAddress.sin_port);

    /* Bind the socket to the port that the client task will send to. */
    FreeRTOS_bind(xListeningSocket, &xBindAddress, sizeof(xBindAddress));

    FreeRTOS_inet_ntoa(xBindAddress.sin_addr, cBuffer);
    FreeRTOS_printf((">>>%s (prvCanRxTask) bound to addr %s:%u\r\n", getCurrTime(), cBuffer, CAN_RX_PORT));

    for (;;)
    {
        uint8_t res = process_j1939(xListeningSocket, &xClient, &msg_len);
        if (res == SUCCESS)
        {
            FreeRTOS_inet_ntoa(xClient.sin_addr, cBuffer);
            FreeRTOS_printf((">>>%s (prvCanRxTask) recv_can_message %u bytes from %s:%u\r\n",
                             getCurrTime(), msg_len, cBuffer, FreeRTOS_ntohs(xClient.sin_port)));
        }
        else
        {
            FreeRTOS_printf((">>>%s (prvCanRxTask) recv_can_message returned %u\r\n", getCurrTime(), res));
        }
    }
}

uint8_t process_j1939(Socket_t xListeningSocket, struct freertos_sockaddr *xClient, size_t *msg_len)
{
    char msg[64];

    /* Receive a message that can overflow the msg buffer */
    uint8_t res = recv_can_message(xListeningSocket, xClient, msg, msg_len);
    if (res == SUCCESS)
    {
        /* Copy message over to a persistent buffer */
        memcpy(j1939_rx_buf, msg, *msg_len);
    }
    return res;
}

static void prvCanTxTask(void *pvParameters)
{
    (void)pvParameters;
    uint32_t ulIPAddress;
    Socket_t xClientSocket;
    struct freertos_sockaddr xDestinationAddress;

    FreeRTOS_GetAddressConfiguration(&ulIPAddress, NULL, NULL, NULL);
    // Broadcast address
    xDestinationAddress.sin_addr = FreeRTOS_inet_addr(CYBERPHYS_BROADCAST_ADDR);
    xDestinationAddress.sin_port = (uint16_t)(CAN_TX_PORT);
    xDestinationAddress.sin_port = FreeRTOS_htons(xDestinationAddress.sin_port);

    FreeRTOS_printf((">>> Starting prvCanTxTask\r\n"));

    xClientSocket = FreeRTOS_socket(FREERTOS_AF_INET, FREERTOS_SOCK_DGRAM, FREERTOS_IPPROTO_UDP);
    configASSERT(xClientSocket != FREERTOS_INVALID_SOCKET);

    FreeRTOS_printf((">>>%s (prvCanTxTask) socket connected\r\n", getCurrTime()));

    uint8_t local_throttle, local_brake, local_gear;

    for (;;)
    {
        hz_cantx_task++;
        /* Copy data over */
        if (xSemaphoreTake(data_mutex, pdMS_TO_TICKS(100)) == pdTRUE)
        {
            local_throttle = throttle;
            local_brake = brake;
            local_gear = gear;
            xSemaphoreGive(data_mutex);
        }

        /* Send throttle */
        if (send_can_message(xClientSocket, &xDestinationAddress, pgn_from_id(CAN_ID_THROTTLE_INPUT), (void *)&local_throttle, sizeof(local_throttle)) != SUCCESS)
        {
            FreeRTOS_printf((">>>%s (prvCanTxTask) send throttle failed\r\n", getCurrTime()));
        }

        /* Send brake */
        if (send_can_message(xClientSocket, &xDestinationAddress, pgn_from_id(CAN_ID_BRAKE_INPUT), (void *)&local_brake, sizeof(local_brake)) != SUCCESS)
        {
            FreeRTOS_printf((">>>%s (prvCanTxTask) send brake failed\r\n", getCurrTime()));
        }

        /* Send gear */
        if (send_can_message(xClientSocket, &xDestinationAddress, pgn_from_id(CAN_ID_GEAR), (void *)&local_gear, sizeof(local_gear)) != SUCCESS)
        {
            FreeRTOS_printf((">>>%s (prvCanTxTask) send gear failed\r\n", getCurrTime()));
        }

        if (camera_ok)
        {
            /* Steering assist */
            if (send_can_message(xClientSocket, &xDestinationAddress, pgn_from_id(CAN_ID_STEERING_INPUT), (void *)&steering_assist, sizeof(steering_assist)) != SUCCESS)
            {
                FreeRTOS_printf((">>>%s (prvCanTxTask) send steering_assist failed\r\n", getCurrTime()));
            }
        }

        vTaskDelay(BROADCAST_LOOP_DELAY_MS);
    }
}
