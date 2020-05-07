#include "fettFreeRTOS.h"
#include <stdbool.h>
#include <SDLib.h>

FF_FILE *ff_fopen( const char *pcFile, const char *pcMode )
{
    (void) pcMode;

    FF_FILE * file;

    file = malloc(sizeof(FF_FILE));

    // Store the file size
    file->ulFileSize = sdlib_size(pcFile);

    // Store the filename in the FILE struct for later access
    // as SDLib uses file names instead of file handles
    strncpy(file->filename,pcFile,ffconfigMAX_FILENAME);

    // Null terminate the file name
    file->filename[ffconfigMAX_FILENAME] = 0;

    return file;
}

int ff_fclose( FF_FILE *pxStream )
{
    // Close the stream and free up the underlying memory
    sdlib_close(pxStream->filename);
    free(pxStream);

    return 0;
}

size_t ff_fread( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream )
{
    size_t bytes;

    bytes = xSize * xItems;
    sdlib_read_from_file(pxStream->filename,pvBuffer,bytes);

    return 0;
}
