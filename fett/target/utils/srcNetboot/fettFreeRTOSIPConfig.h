/*
- This file is included in the used FreeRTOSIPConfig.h
*/

#define ipconfigUSE_HTTP 0
#define ipconfigUSE_FTP  0
#define ipconfigUSE_DHCP 0
#define ipconfigUSE_DNS 0


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
