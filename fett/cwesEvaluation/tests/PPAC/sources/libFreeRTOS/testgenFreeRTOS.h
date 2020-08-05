/*
testgen header for all externs and global variables
*/

/* General includes */
#include <stdio.h>
#include <unistd.h>
#include <stdarg.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
/* FreeRTOS  includes. */
#include <FreeRTOS.h>
#include <task.h>
#include <message_buffer.h>
#include <semphr.h>
/* IP stack includes. */
#include "FreeRTOS_IP.h"
#include "FreeRTOS_Sockets.h"
/* WolfSSL includes */
#include <wolfssl/ssl.h>
#include <wolfssl/error-ssl.h>
#include <wolfssl/wolfcrypt/dh.h>
#include <wolfssl/wolfcrypt/asn.h>
/* Misc includes */
#include <malloc.h>
/* Tests Parameters Include */
#include "../testsParameters.h"

/* Macros */
#if (__riscv_xlen == 64)
    #define STACKSIZEMUL 128
#else
    #define STACKSIZEMUL 10
#endif
/* Task notifications values */
#define NOTIFY_SUCCESS 0x0000000F
#define NOTIFY_FAIL 0x00000000
#define NOTIFY_CONNECTED 0x000000F0
#define NOTIFY_TERMINATED 0x00000F00
#define NOTIFY_INVALIDAUTH 0x0000F000
/* True and False values */
#define uTRUE 1
#define uFALSE 0

/* EXIT macro sends the exit flag + delete the task if task (vEXIT) and return if void func (prEXIT) */
#define vEXIT(exitCode) ({exitTest (exitCode); vTaskDelete (NULL);})
#define prEXIT(exitCode) ({exitTest (exitCode); return;})

/* Tests specific macros */
#include "cweSpecificMacros.h"

/* Extra types */
struct testgen_parentSocket {
    Socket_t xConnectedSocket;
    TaskHandle_t xTaskParent;
    #ifdef USE_TLS_OVER_TCP
        WOLFSSL* xWolfSSL_Object;
    #endif
    uint8_t iPart[2];
    uint8_t isServer; 
};

// --------- testgenNtk.c ---------------------------------------------------------------------------------
extern void vStartNetwork (void *pvParameters);
extern void vServerSocketTCP (void *pvParameters);
extern void vClientSocketTCP (void *pvParameters);

// --------- testgenMisc.c ---------------------------------------------------------------------------------
extern void onPrintf (const char * textToPrint, ...);
extern void exitTest (uint8_t exitCode);
extern void _open (const char * dump1, int dump2, ...);
extern void _gettimeofday (struct timeval *__p, void *__tz);
extern time_t XTIME(time_t *t);
extern void *XREALLOC(void *p, size_t n, void* heap, int type);
extern uint32_t ulApplicationGetNextSequenceNumber(uint32_t ulSourceAddress, uint16_t usSourcePort, 
                                            uint32_t ulDestinationAddress, uint16_t usDestinationPort);
extern int testgen_wc_GenerateSeed(uint8_t* seed, uint8_t sz);
extern MessageBufferHandle_t globalMsgBuffer;
extern uint8_t sendToMsgBuffer (void * xData, size_t xDataSize);
extern size_t recvFromMsgBuffer (void * xBuf, size_t xBufSize);

// --------- test_XXX.c ---------------------------------------------------------------------------------
extern TaskHandle_t xMainTask;
extern UBaseType_t xMainPriority;

// --------- testgenWolfSSL.c
extern void vEndWolfSSL (void *pvParameters);
extern int startWolfSSL( void );
extern void vInitServerWolfSSL (void *pvParameters);
extern void vInitClientWolfSSL (void *pvParameters);
extern WOLFSSL_CTX* xWolfSSL_ServerContext;
extern WOLFSSL_CTX* xWolfSSL_ClientContext;


