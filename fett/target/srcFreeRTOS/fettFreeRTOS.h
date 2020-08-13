/*
fett header for includes, externs, and global variables
*/

/* General includes */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
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

/* WolfSSL includes */ //for TLS if needed  + for signatures
#include "fettWolfSSLsettings.h"
#include <wolfssl/wolfcrypt/settings.h>
#include <wolfssl/ssl.h>
#include <wolfssl/wolfcrypt/ed25519.h>

/* Misc includes */
#include "ff_stdio.h"

/* Macros */
#define MSGBUF_SIZE 32
#define STACKSIZEMUL 12 //For tasks. Needs to be larger on 64-bit (not for FETT)
#include "fettUserConfig.h"
/* Task notifications values */
#define NOTIFY_SUCCESS      0x0000FFFF //This allows us 16 distinct successes
#define NOTIFY_SUCCESS_NTK  0x00000001
#define NOTIFY_SUCCESS_HTTP 0x00000002
#define NOTIFY_SUCCESS_OTA  0x00000004
#define NOTIFY_FAIL      0xFFFF0000 //This allows us 16 distinct failures
#define NOTIFY_FAIL_NTK  0x00010000
#define NOTIFY_FAIL_HTTP 0x00020000
#define NOTIFY_FAIL_OTA  0x00040000
/* True and False values */
#define uTRUE 1
#define uFALSE 0

/* New error-handling macros introduced by Issue #248 */
#define ASSERT_OR_WARN(b, msg) {\
    if (b)\
        fettPrintf ("(Info)~  Assertion OK: %s\r\n",msg);\
    else\
        fettPrintf ("(Warning)~  Assertion failed: %s\r\n",msg);\
    }

#define ASSERT_OR_DELETE_TASK(b, msg) {\
    if (b)\
        fettPrintf ("(Info)~  Assertion OK: %s\r\n",msg);\
    else {\
        fettPrintf ("(Error)~  Assertion failed so deleting task: %s\r\n",msg);\
        exitFett (1);\
        vTaskDelete (NULL); }\
    }



#ifndef pdTICKS_TO_S
    #define pdTICKS_TO_S( xTicks ) ( ( TickType_t ) ( ( ( TickType_t ) ( xTicks ) ) / ( TickType_t ) configTICK_RATE_HZ ) )
#endif

/* Debug and logging */
#if (FETT_DEBUG == 1)
    #define debugFettPrintf(...) {fettPrintf("(Debug)~  "); fettPrintf (__VA_ARGS__);}
    #ifdef FreeRTOS_debug_printf
        #undef FreeRTOS_debug_printf
    #endif
    #define FreeRTOS_debug_printf(X)    debugFettPrintf X
#else
    #define debugFettPrintf(...) {do{} while(0);}
#endif

#ifdef FreeRTOS_printf
    #undef FreeRTOS_printf
#endif
#define FreeRTOS_printf(X)  fettPrintf X

// --------- fettNtk.c ---------------------------------------------------------------------------------
extern void vStartNetwork (void *pvParameters);

// --------- fettMisc.c ---------------------------------------------------------------------------------

// Termination control.
//
// A global atomic Boolean flag is declared and initialized to False.
// A task can set this to True by calling setStopRequested()
// Other tasks can test it with StopRequested()
extern void setStopRequested(void);
extern bool StopRequested(void);

// Debug printing and exit
extern void fettPrintf (const char * textToPrint, ...);
extern void exitFett (uint8_t exitCode);


extern void _open (const char * dump1, int dump2, ...); //Needed for WolfSSL to compile -- should never be called
extern void _gettimeofday (struct timeval *__p, void *__tz); //Needed for WolfSSL to compile -- should never be called
extern time_t XTIME(time_t *t); //Needed for WolfSSL to compile -- should never be called
extern void *XREALLOC(void *p, size_t n, void* heap, int type); //Not defined in FreeRTOS -- a safe not-feature-complete version is defined here
extern uint32_t ulApplicationGetNextSequenceNumber(uint32_t ulSourceAddress, uint16_t usSourcePort,
                                            uint32_t ulDestinationAddress, uint16_t usDestinationPort);
extern int fett_wc_GenerateSeed(uint8_t* seed, uint8_t sz); //Needed for WolfSSL to compile -- a temporary workaround is implemented
extern MessageBufferHandle_t globalMsgBuffer;
extern uint8_t sendToMsgBuffer (void * xData, size_t xDataSize);
extern size_t recvFromMsgBuffer (void * xBuf, size_t xBufSize);

// --------- main_fett.c ---------------------------------------------------------------------------------
extern TaskHandle_t xMainTask;
extern UBaseType_t xMainPriority;

// ----------- http.c -------------------------------------------------------------------------------------
extern void vHttp (void *pvParameters);
extern void Initialize_HTTP_Assets (void);

// ----------- ota.c --------------------------------------------------------------------------------------
extern void vOta (void *pvParameters);
