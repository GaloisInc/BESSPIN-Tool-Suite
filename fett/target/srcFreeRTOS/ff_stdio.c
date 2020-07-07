#include "fettFreeRTOS.h"

// Static (persistent) state of this module.

// Mutex providing gross mutual exclusion for the facilities of this
// module. Note this is declared with static/file scope, so it cannot
// be directly accessed outside of this file.
static SemaphoreHandle_t ff_mutex;

#ifdef FETT_AWS
    FATFS FatFs; /* FatFs work area needed for each volume */
#endif

void ff_lock (void)
{
    BaseType_t r;
    r = xSemaphoreTake (ff_mutex, portMAX_DELAY);
    ASSERT_OR_WARN ((r == pdTRUE), "Taking ff_mutex");
    return;
}

void ff_release (void)
{
    BaseType_t r;
    r = xSemaphoreGive (ff_mutex);
    ASSERT_OR_WARN ((r == pdTRUE), "Releasing ff_mutex");
    return;
}

int ff_init( void )
{
    // Note that we use a dynamically allocated Mutex, since our FreeRTOSConfig.h
    // does not support static allocation.
    ff_mutex = xSemaphoreCreateMutex();
    if (ff_mutex == NULL)
      {
        fettPrintf ("(Error)~ failed to allocate memory for ff_mutex\r\n");
        exitFett (1);
        return 1; // caller responsible for handling error
      }

    // Make sure ff_mutex is in the "given" state at startup
    (void) xSemaphoreGive (ff_mutex);

    #ifdef FETT_AWS

        #ifdef FREERTOS_USE_RAMDISK
        {
          FRESULT res;
	  BYTE work[FF_MAX_SS];

	  // For RAMDisk, we need to format the disk.  FM_ANY means that a choice
	  // of FAT variant (16, 32 etc) will be automatically made based on the
	  // number of sectors and the sector size supplied by the diskio_ram.c
	  // module.
          res = f_mkfs("0:", FM_ANY, 0, work, sizeof(work));
          fettPrintf ("(Info)~ ff_init: mkfs returns %d\n", (int) res);
          res = f_mount(&FatFs, "", 0); 
          fettPrintf ("(Info)~ ff_init: mount returns %d\n", (int) res);
	  return res;
	}
        #else
        // IceBlk is already initialized upon boot,
        // check if the disk is present instead
        if (IceblkDevInstance.disk_present) {
            fettPrintf ("(Info)~ ff_init: Disk present. Mounting filesystem...\r\n");
            return f_mount(&FatFs, "", 0);
        } else {
            fettPrintf ("(Error)~ iceclk disk is not present\r\n");
            return 1;
        }
        #endif

    #else
        return sdlib_initialize();
    #endif
}

FF_FILE *ff_fopen( const char *pcFile, const char *pcMode )
{

    if (strlen(pcFile) > ffconfigMAX_FILENAME) {
        fettPrintf("(Error)~  ff_open: Length of filename should be <= %d.\r\n",ffconfigMAX_FILENAME);
        exitFett (1);
        // caller responsible for handling error
        return NULL;
    }

    FF_FILE * file;

    file = (FF_FILE *) pvPortMalloc(sizeof(FF_FILE));

    // Crash fast if there's no memory left on the device
    if (file == NULL) {
        fettPrintf("(Error)~  ff_open: Failed to malloc <FF_FILE>.\r\n");
        exitFett (1);
        // caller responsible
        return NULL;
    }

    #ifdef FETT_AWS
        uint8_t mode;
        if ((strcmp(pcMode,"r") == 0) || (strcmp(pcMode,"rb") == 0)) {
            mode = FA_READ;
        } else if (strcmp(pcMode,"w") == 0) {
            mode = FA_WRITE | FA_CREATE_ALWAYS;
        } else {
            fettPrintf ("(Error)~  ff_fopen: pcMode:<%s> is not implemented.\r\n",pcMode);
            return NULL;
        }
        int res = f_open(&(file->fatfsFile), pcFile, mode);
        if (res != FR_OK) {
            fettPrintf ("ff_fopen: Failed to open <%s>. [ret=%d]\r\n",pcFile,res);
            return NULL;
        }

        // Store the file size
        file->ulFileSize = f_size(&(file->fatfsFile));
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
        ret = f_close(&(pxStream->fatfsFile)); /* Close the file */
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
        int res = f_read(&(pxStream->fatfsFile), (uint8_t *)pvBuffer, bytes, &bytes_read);
        if (res != FR_OK) {
            fettPrintf ("(Error)~ ff_fread: failed to read from file. [ret =%d]\r\n",res);
            return 0; // 0 items read [TODO: do we check here on any error values?]
        }
    #else
        bytes_read = sdlib_read_from_file(pxStream->filename,pvBuffer,bytes);
    #endif


    items_read = bytes_read/xSize;
    // caller responsible to check items_read
    return items_read;
}

size_t ff_fwrite( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream )
{
    size_t bytes;
    size_t bytes_written;
    size_t items_written;

    bytes = xSize * xItems;
    #ifdef FETT_AWS
        int res = f_write(&(pxStream->fatfsFile), (uint8_t *)pvBuffer, bytes, &bytes_written); /* Write data to the file */
        if (res != FR_OK) {
            fettPrintf ("(Error)~ ff_fwrite: failed to write to file. [ret=%d]\r\n",res);
            return 0; // 0 items written
        }
    #else
        bytes_written = sdlib_write_to_file(pxStream->filename,pvBuffer,bytes);
    #endif

    items_written = bytes_written/xSize;
    // caller responsible to check items_written
    return items_written;
}
