/*
- This file is included in the used FreeRTOSIPConfig.h
*/

/* Flags for using HTTP */
#define ipconfigUSE_HTTP 1
#define ipconfigUSE_FTP  0

/* Set ipconfigUSE_DNS to 1 to include a basic DNS client/resolver.  DNS is used
through the FreeRTOS_gethostbyname() API function. */
#define ipconfigUSE_DNS 0

/* Debugging and logging flags for the TCP sources */
#if( FETT_DEBUG == 1 )
    #define ipconfigHAS_DEBUG_PRINTF 1
#endif
#define ipconfigHAS_PRINTF 1

/* Network configuration 
- These options gets filled up during the run
- The values can be set in "fett/base/utils/setupEnv.json"
- This is a list of the macros, and the settings names inside "setupEnv.json"

//MAC Address
#define configMAC_ADDR0     <fpgaMacAddrTarget>
#define configMAC_ADDR1     <fpgaMacAddrTarget>
#define configMAC_ADDR2     <fpgaMacAddrTarget>
#define configMAC_ADDR3     <fpgaMacAddrTarget>
#define configMAC_ADDR4     <fpgaMacAddrTarget>
#define configMAC_ADDR5     <fpgaMacAddrTarget>

// IP address configuration
#define configIP_ADDR0      <fpgaIpTarget>
#define configIP_ADDR1      <fpgaIpTarget>
#define configIP_ADDR2      <fpgaIpTarget>
#define configIP_ADDR3      <fpgaIpTarget>

// Default gateway IP address configuration.
#define configGATEWAY_ADDR0 <fpgaIpHost>
#define configGATEWAY_ADDR1 <fpgaIpHost>
#define configGATEWAY_ADDR2 <fpgaIpHost>
#define configGATEWAY_ADDR3 <fpgaIpHost>

//Netmask
#define configNET_MASK0     <fpgaNetMaskTarget>
#define configNET_MASK1     <fpgaNetMaskTarget>
#define configNET_MASK2     <fpgaNetMaskTarget>
#define configNET_MASK3     <fpgaNetMaskTarget>
*/
