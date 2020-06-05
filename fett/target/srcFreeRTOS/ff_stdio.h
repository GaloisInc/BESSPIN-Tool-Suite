/*
 * Fat filesystem library
*/

#ifndef FF_STDIO_H
#define FF_STDIO_H

#define ffconfigMAX_FILENAME    13 // 8.3 format plus a final \0 terminator

typedef struct _FF_FILE
{
    char filename[ffconfigMAX_FILENAME];
    uint32_t ulFileSize;            /* File's Size. */
} FF_FILE;

typedef struct
{
    char NotImplemented;

} FF_FindData_t;

// Allocates a global mutex and initializes the filesystem
// Returns 0 on success, or any other value on failure.
//
// This function MUST be called exactly ONCE before any of
// the other functions declared below.
extern int ff_init( void );

// Mutual exclusion
//
// An ff_lock()/ff_release() pair must surround a critical section
// when manipulating a single file.  This means the lock must be taken
// before ff_open() and released after ff_fclose() and any other intervening
// file operations.  It is up to the caller to ensure these are called.
//
// In general, a function that declarares and allocates an FF_FILE struct
// should lock and release the mutex in that block's scope.
//
// Note - in a caller, an error condition that results in an early return
// from a function MUST remember to release the lock, or deadlock may result.
extern void ff_lock (void);
extern void ff_release (void);

// File manipulation
extern FF_FILE *ff_fopen( const char *pcFile, const char *pcMode );
extern int ff_fclose( FF_FILE *pxStream );
extern size_t ff_fread( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream );
extern size_t ff_fwrite( void *pvBuffer, size_t xSize, size_t xItems, FF_FILE * pxStream );

#endif /* FF_STDIO_H */
