#include "fettFreeRTOS.h"
#include "ff_stdio.h"

/* STUB IMPLEMENTATIONS                                   */
/* To be removed then the FF library is fully implemented */

FF_FILE *ff_fopen( const char *pcFile, const char *pcMode )
{
    (void) pcFile;
    (void) pcMode;
    fettPrintf ("ff_fopen() is currently not implemented.\n");
    return NULL;
}

int ff_fclose( FF_FILE *pxStream )
{
    (void) pxStream;
    fettPrintf ("ff_fclose() is currently not implemented.\n");
    return 0;
}

size_t ff_fread( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream )
{
    (void) pvBuffer;
    (void) xSize;
    (void) xItems;
    (void) pxStream;
    fettPrintf ("ff_fread() is currently not implemented.\n");
    return 0;
}
