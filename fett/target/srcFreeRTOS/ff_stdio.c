#include "fettFreeRTOS.h"
#include <stdbool.h>
#include <SDLib.h>

// Static (persistent) state of this module.

// Mutex providing gross mutual exclusion for the facilities of this
// module. Note this is declared with static/file scope, so it cannot
// be directly accessed outside of this file.
static SemaphoreHandle_t ff_mutex;


// Exported function bodies

int ff_init( void ) 
{
    // Note that we use a dynamically allocated Mutex, since our FreeRTOSConfig.h
    // does not support static allocation.
    ff_mutex = xSemaphoreCreateMutex();
    if (ff_mutex == NULL)
      {
        fettPrintf ("(Error)~ failed to allocate memory for ff_mutex\r\n");
        exitFett (1);
        return 1; // error
      }

    // Make sure ff_mutex is in the "given" state at startup
    (void) xSemaphoreGive (ff_mutex);

    return sdlib_initialize();
}

void ff_lock (void)
{
    BaseType_t r;
    r = xSemaphoreTake (ff_mutex, portMAX_DELAY);
    prERROR_IF_EQ (r, pdFALSE, "Taking ff_mutex");
    return;
}

void ff_release (void)
{
    BaseType_t r;
    r = xSemaphoreGive (ff_mutex);
    prERROR_IF_EQ (r, pdFALSE, "Releasing ff_mutex");
    return;
}

FF_FILE *ff_fopen( const char *pcFile, const char *pcMode )
{

    if (strlen(pcFile) > ffconfigMAX_FILENAME) {
        fettPrintf("(Error)~  ff_open: Length of filename should be <= %d.\r\n",ffconfigMAX_FILENAME);
        exitFett (1);
        return NULL;
    }

    FF_FILE * file;

    file = pvPortMalloc(sizeof(FF_FILE));

    // Crash fast if there's no memory left on the device
    if (file == NULL) {
        fettPrintf("(Error)~  ff_open: Failed to malloc.\r\n");
        exitFett (1);
        return NULL;
    }

    if (!sdlib_open(pcFile,pcMode)) {
        fettPrintf ("ff_fopen: Failed to open <%s>.\r\n",pcFile);
        return NULL;
    }

    // Store the file size
    file->ulFileSize = sdlib_size(pcFile);

    // Store the filename in the FILE struct for later access
    // as SDLib uses file names instead of file handles
    strcpy(file->filename,pcFile);

    return file;
}

int ff_fclose( FF_FILE *pxStream )
{
    // Close the stream and free up the underlying memory
    sdlib_close(pxStream->filename);
    vPortFree(pxStream);

    return 0;
}

size_t ff_fread( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream )
{
    size_t bytes;
    size_t bytes_read;
    size_t items_read;

    bytes = xSize * xItems;
    bytes_read = sdlib_read_from_file(pxStream->filename,pvBuffer,bytes);

    items_read = bytes_read/xSize;

    return items_read;
}

size_t ff_fwrite( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream )
{
    size_t bytes;
    size_t bytes_written;
    size_t items_written;

    bytes = xSize * xItems;
    bytes_written = sdlib_write_to_file(pxStream->filename,pvBuffer,bytes);

    items_written = bytes_written/xSize;

    return items_written;
}
