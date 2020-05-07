// This is the main task executed by http

#include "fettFreeRTOS.h"
#include "tcp_server.h"

void vHttp (void *pvParameters);
void Http_Worker (void);

#define configHTTP_ROOT "/"

static const struct xSERVER_CONFIG xServerConfiguration[] =
  {
    { eSERVER_HTTP,   // Server type
      HTTP_PORT,      // port number - configured in fett/base/utils/setupEnv.json
      1,              // backlog - just 1 for simplicity initially
      configHTTP_ROOT // root dir.
    },
  };

void Http_Worker (void)
{
    TCPServer_t *pxTCPServer = NULL;
    const TickType_t xInitialBlockTime = pdMS_TO_TICKS( 200UL );

    /* Create the servers defined by the xServerConfiguration array above. */
    pxTCPServer = FreeRTOS_CreateTCPServer
      (xServerConfiguration, sizeof( xServerConfiguration ) / sizeof( xServerConfiguration[ 0 ] ) );

    vERROR_IF_EQ(pxTCPServer, NULL, "vHttp: Failed to create TCP Server.");

    for( ;; )
      {
        FreeRTOS_TCPServerWork( pxTCPServer, xInitialBlockTime );
      }
}



void vHttp (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;

    fettPrintf("(Info)~  vHttp: Starting HTTP...\r\n");

    Http_Worker();

    fettPrintf("(Info)~  vHttp: Exitting HTTP...\r\n");

    //notify main
    vERROR_IF_EQ(xMainTask, NULL, "vHttp: Get handle of <main:task>.");
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS_HTTP ,eSetBits);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vHttp: Notify <main:task>.");

    vTaskDelete (NULL);
}
