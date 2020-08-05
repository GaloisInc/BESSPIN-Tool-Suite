/*
Test_290: Improper Access Control
--- This file has extra parts for the test
-- This file's scope should be protected; otherwise, the test will fail (i.e. CWE exists)
*/

#include "../testsParameters.h"
#include "testgenFreeRTOS.h"

/* Data structures:
ipList: A list of IPs. Protected and defined here pre-test.
*/
#define IPS_LIST_LENGTH 3 //has to be >=2

#if (TESTGEN_TEST_PART == 1)
    static char ipsList[IPS_LIST_LENGTH][IP_NAME_SIZE] = {"192.168.23.2", "10.88.88.1", "10.11.5.5"}; 
#else //part 2
    static char ipsList[IPS_LIST_LENGTH][IP_NAME_SIZE] = {"192.168.23.2", SPOOFING_IP, "10.11.5.5"}; 
#endif

//functions declarations
uint8_t getServicePermission (const char * xActor, const char * xIP);

// This function receives an actor name, and returns true/false to whether permission should be given
uint8_t getServicePermission (const char * xActor, const char * xIP) {
    onPrintf ("\t>>>>>> [getServicePermission]: Received request for <%s> from <%s>.\n",xActor,xIP);
    //print the list
    onPrintf ("\t>>>>>> [getServicePermission]: The allowed IPs are:\n");
    uint8_t authorizedIP = uFALSE;
    for (int i=0; i < IPS_LIST_LENGTH; i++) {
        onPrintf ("\t\t>>> <%s>\n",ipsList[i]);
        if (!strcmp(xIP,ipsList[i])) {
            authorizedIP = uTRUE;
        }
    }
    return authorizedIP;
}