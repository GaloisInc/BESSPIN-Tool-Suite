/*
- This file is included in the used FreeRTOSIPConfig.h
*/

/* Flags for using HTTP */
#define ipconfigUSE_HTTP 1
#define ipconfigUSE_FTP  0

/* For FETT only...
   We include DHCP to offer CVE-2019-16602
   We include DNS  to offer CVE-2019-16525

   Note that the FETT application does NOT actually USE DNS or DHCP, but we
   include the code in the build to include these CVEs in the application's
   attack surface.

   See comments in FreeRTOS/Demo/RISC-V_Galois_P1/FreeRTOSIPConfig.h
*/
#define ipconfigUSE_DHCP 1
/* Short DHCP timeout so that DHCP fails fast and falls back on static IP assignment */
#define ipconfigMAXIMUM_DISCOVER_TX_PERIOD ( 2000 / portTICK_PERIOD_MS )
#define ipconfigUSE_DNS 1


/* Debugging and logging flags for the TCP sources */
#if( FETT_DEBUG == 1 )
    #define ipconfigHAS_DEBUG_PRINTF 1
#endif
#define ipconfigHAS_PRINTF 1

/* Network configuration
- These options gets filled up during the run
- The values can be set in "fett/base/utils/setupEnv.json"
- This is a list of the macros, and the settings names inside "setupEnv.json"
- ${target} can be either 'fpga' or 'aws'

//MAC Address
#define configMAC_ADDR0     <${target}MacAddrTarget>
#define configMAC_ADDR1     <${target}MacAddrTarget>
#define configMAC_ADDR2     <${target}MacAddrTarget>
#define configMAC_ADDR3     <${target}MacAddrTarget>
#define configMAC_ADDR4     <${target}MacAddrTarget>
#define configMAC_ADDR5     <${target}MacAddrTarget>

// IP address configuration
#define configIP_ADDR0      <${target}IpTarget>
#define configIP_ADDR1      <${target}IpTarget>
#define configIP_ADDR2      <${target}IpTarget>
#define configIP_ADDR3      <${target}IpTarget>

// Default gateway IP address configuration.
#define configGATEWAY_ADDR0 <${target}IpHost>
#define configGATEWAY_ADDR1 <${target}IpHost>
#define configGATEWAY_ADDR2 <${target}IpHost>
#define configGATEWAY_ADDR3 <${target}IpHost>

//Netmask
#define configNET_MASK0     <${target}NetMaskTarget>
#define configNET_MASK1     <${target}NetMaskTarget>
#define configNET_MASK2     <${target}NetMaskTarget>
#define configNET_MASK3     <${target}NetMaskTarget>
*/
