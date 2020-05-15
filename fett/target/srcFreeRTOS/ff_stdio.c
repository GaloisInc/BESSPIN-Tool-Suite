#include "fettFreeRTOS.h"
#include <stdbool.h>
#include <SDLib.h>

int ff_init( void ) 
{
    return sdlib_initialize();
}

FF_FILE *ff_fopen( const char *pcFile, const char *pcMode )
{
    (void) pcMode;

    FF_FILE * file;

    if (strlen(pcFile) > ffconfigMAX_FILENAME) {
        fettPrintf("(Error)~  ff_open: Length of filename should be <= %d.\r\n",ffconfigMAX_FILENAME);
        exitFett (1);
        return NULL;
    }

    file = pvPortMalloc(sizeof(FF_FILE));

    // Crash fast if there's no memory left on the device
    if (file == NULL) {
        fettPrintf("(Error)~  ff_open: Failed to malloc.\r\n");
        exitFett (1);
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
