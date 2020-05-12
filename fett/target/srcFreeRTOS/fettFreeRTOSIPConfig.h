/*
- This file is included in the used FreeRTOSIPConfig.h
*/

/* Flags for using HTTP */
#define ipconfigUSE_HTTP 1
#define ipconfigUSE_FTP  0

/* Debugging and logging flags for the TCP sources */
#if( FETT_DEBUG == 1 )
    #define ipconfigHAS_DEBUG_PRINTF 1
#endif
#define ipconfigHAS_PRINTF 1