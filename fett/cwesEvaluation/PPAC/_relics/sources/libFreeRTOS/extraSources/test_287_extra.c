/*
Test_287: Improper Access Control
--- This file has extra parts for the test
-- This file's scope should be protected; otherwise, the test will fail (i.e. CWE exists)
*/

#include "../testsParameters.h"
#include "testgenFreeRTOS.h"

/* Data structures:
usersList: A list of strings. Protected and defined here pre-test.
*/
#define USERS_LIST_LENGTH 3 //has to be >=2

#if (TESTGEN_TEST_PART == 1) || (TESTGEN_TEST_PART == 3)
    static char usersList[USERS_LIST_LENGTH][SUBJECT_CN_BUF_SIZE] = {"Yoda", "Jedi Order CLNT", "Baby Yoda"}; 
#else //part 2
    static char usersList[USERS_LIST_LENGTH][SUBJECT_CN_BUF_SIZE] = {"Yoda", "Galois", "Baby Yoda"}; 
#endif

//functions declarations
uint8_t getServicePermission (const char * xActor);

// This function receives an actor name, and returns true/false to whether permission should be given
uint8_t getServicePermission (const char * xActor) {
    onPrintf ("\t>>>>>> [getServicePermission]: Received request for <%s>.\n",xActor);
    //print the list
    onPrintf ("\t>>>>>> [getServicePermission]: The allowed users are:\n");
    uint8_t authorizedUser = uFALSE;
    for (int i=0; i < USERS_LIST_LENGTH; i++) {
        onPrintf ("\t\t>>> <%s>\n",usersList[i]);
        if (!strcmp(xActor,usersList[i])) {
            authorizedUser = uTRUE;
        }
    }
    return authorizedUser;
}