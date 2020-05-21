// This is the main task executed by http

#include "fettFreeRTOS.h"
#include "tcp_server.h"

void vHttp (void *pvParameters);
void Http_Worker (void);

#define configHTTP_ROOT "/"
#define configHTTP_TIMEOUT 9000 // milliseconds

// Include auto-generated data for initial state of the web-site
#include "httpAssets.h"

static const struct xSERVER_CONFIG xServerConfiguration[] =
  {
    { eSERVER_HTTP,   // Server type
      HTTP_PORT,      // port number - configured in fett/base/utils/setupEnv.json
      1,              // backlog - initially 1 for simplicity
      configHTTP_ROOT // root dir.
    },
  };


// Iterates over the data tables from httpdata.h, and writes each
// out to the filesystem with the given name, size and content.
void Initialize_HTTP_Assets (void)
{
    for (int i = 0; i < asset_files; i++)
    {
        FF_FILE *fd;
        size_t  written;
        int     r;

        const char   *this_name = asset_names[i];
        const size_t  this_size = asset_sizes[i];
        
        fettPrintf ("(Info)~  Initialize_HTTP_Assets: Creating %s to write %ld bytes\n",
                    this_name,
                    this_size);

        fd = ff_fopen (this_name, "w");
        pvERROR_IF_EQ (fd, NULL, "Initialize_HTTP_Assets: open/create");

        written = ff_fwrite ((void *) asset_data[i], 1, this_size, fd);
        if (written != this_size)
        {
            fettPrintf ("(Error)~  Initialize_HTTP_Assets: file write failed. [written=%ld, fsize=%ld].\r\n",
                        written,
                        this_size);
            // Go on to close the file anyway...
        }
        r = ff_fclose (fd);
        if (r != 0)
        {
            fettPrintf ("(Error)~  Initialize_HTTP_Assets: file close failed\n");
        }
    }
    return;
}

void Http_Worker (void)
{
    TCPServer_t *pxTCPServer = NULL;
    const TickType_t xInitialBlockTime = pdMS_TO_TICKS( 200UL );

    /* Create the servers defined by the xServerConfiguration array above. */
    pxTCPServer = FreeRTOS_CreateTCPServer
      (xServerConfiguration, sizeof( xServerConfiguration ) / sizeof( xServerConfiguration[ 0 ] ) );

    pvERROR_IF_EQ(pxTCPServer, NULL, "vHttp: Create TCP Server.");

    TickType_t xStartTime = xTaskGetTickCount();
    do {
      FreeRTOS_TCPServerWork (pxTCPServer, xInitialBlockTime);
    } while ((xTaskGetTickCount() - xStartTime) < pdMS_TO_TICKS(configHTTP_TIMEOUT));
}



void vHttp (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;

    fettPrintf("(Info)~  vHttp: Starting HTTP...\r\n");

    Http_Worker();

    fettPrintf("(Info)~  vHttp: Exitting HTTP...\r\n");

    //notify main
    pvERROR_IF_EQ(xMainTask, NULL, "vHttp: Get handle of <main:task>.");
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS_HTTP ,eSetBits);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vHttp: Notify <main:task>.");

    vTaskDelete (NULL);
}
