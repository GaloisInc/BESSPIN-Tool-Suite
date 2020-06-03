#include "fettFreeRTOS.h"

// Static (persistent) state of this module.

// Mutex providing gross mutual exclusion for the facilities of this
// module. Note this is declared with static/file scope, so it cannot
// be directly accessed outside of this file.
static SemaphoreHandle_t ff_mutex;

// Exported function bodies

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

/* Return 0 if OK, 1 if Error */
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

    #ifdef FETT_AWS
        // IceBlk is already initialized upon boot,
        // check if the disk is present instead
        if (IceblkDevInstance.disk_present) {
            return 0;
        } else {
            fettPrintf ("(Error)~ iceclk disk is not present\r\n");
            return 1;
        }
    #else
        return sdlib_initialize();
    #endif
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
        fettPrintf("(Error)~  ff_open: Failed to malloc <FF_FILE>.\r\n");
        exitFett (1);
        return NULL;
    }

    #ifdef FETT_AWS
        // allocate the FIL structure too
        file->fatfsFile = pvPortMalloc(sizeof(FIL));
        if (file->fatfsFile == NULL) {
            fettPrintf("(Error)~  ff_open: Failed to malloc <FIL>.\r\n");
            exitFett (1);
            return NULL;
        }

        uint8_t mode;
        if ((strcmp(pcMode,"r") == 0) || (strcmp(pcMode,"rb") == 0)) {
            mode = FA_READ;
        } else if (strcmp(pcMode,"w") == 0) {
            mode = FA_WRITE | FA_CREATE_ALWAYS;
        } else {
            fettPrintf ("(Error)~  ff_fopen: pcMode:<%s> is not implemented.\r\n",pcMode);
            return NULL;
        }
        int res = f_open(file->fatfsFile, pcFile, mode);
        if (res != FR_OK) {
            fettPrintf ("(Error)~  ff_fopen: Failed to open <%s>. [ret=%d]\r\n",pcFile,res);
            return NULL;
        }

        // Store the file size
        file->ulFileSize = f_size(file->fatfsFile);
    #else
        if (!sdlib_open(pcFile,pcMode)) {
            fettPrintf ("ff_fopen: Failed to open <%s>.\r\n",pcFile);
            return NULL;
        }

        // Store the file size
        file->ulFileSize = sdlib_size(pcFile);
    #endif

    // Store the filename in the FILE struct for later access
    // as SDLib uses file names instead of file handles
    strcpy(file->filename,pcFile);

    return file;
}

/* Close the stream and free up the underlying memory */
int ff_fclose( FF_FILE *pxStream )
{
    int ret;
    #ifdef FETT_AWS
        ret = f_close(pxStream->fatfsFile); /* Close the file */
        vPortFree(pxStream->fatfsFile);
    #else
        ret = 0;
        sdlib_close(pxStream->filename);
    #endif
    vPortFree(pxStream);
    return ret;
}

size_t ff_fread( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream )
{
    size_t bytes;
    size_t bytes_read;
    size_t items_read;

    bytes = xSize * xItems;

    #ifdef FETT_AWS
        int res = f_read(pxStream->fatfsFile, (uint8_t *)pvBuffer, bytes, &bytes_read);
        if (res != FR_OK) {
            fettPrintf ("(Error)~ ff_fread: failed to read from file. [ret =%d]\r\n",res);
            return 0; // 0 items read [TODO: do we check here on any error values?]
        }
    #else
        bytes_read = sdlib_read_from_file(pxStream->filename,pvBuffer,bytes);
    #endif

    items_read = bytes_read/xSize;
    return items_read;
}

size_t ff_fwrite( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream )
{
    size_t bytes;
    size_t bytes_written;
    size_t items_written;

    bytes = xSize * xItems;
    #ifdef FETT_AWS
        int res = f_write(pxStream->fatfsFile, (uint8_t *)pvBuffer, bytes, &bytes_written); /* Write data to the file */
        if (res != FR_OK) {
            fettPrintf ("(Error)~ ff_fwrite: failed to write to file. [ret=%d]\r\n",res);
            return 0; // 0 items written
        }
    #else
        bytes_written = sdlib_write_to_file(pxStream->filename,pvBuffer,bytes);
    #endif

    items_written = bytes_written/xSize;
    return items_written;
}
