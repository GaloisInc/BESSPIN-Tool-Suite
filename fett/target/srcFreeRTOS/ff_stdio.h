/*
Fake ff_stdio header for FAT filesystem related codes
*/

#define ffconfigMAX_FILENAME    129

typedef struct _FF_FILE
{
    char NotImplemented;

    uint32_t ulFileSize;            /* File's Size. */
} FF_FILE;

typedef struct
{
    char NotImplemented;

} FF_FindData_t;

extern FF_FILE *ff_fopen( const char *pcFile, const char *pcMode );
extern int ff_fclose( FF_FILE *pxStream );
extern size_t ff_fread( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream );
