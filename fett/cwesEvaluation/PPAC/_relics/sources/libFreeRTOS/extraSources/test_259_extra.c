/*
Test_257: Authentication Bypass by Spoofing
--- This file has extra parts for the test
-- This file's scope should be protected; otherwise, the test will fail (i.e. CWE exists)
*/

#include "../testsParameters.h"
#include "testgenFreeRTOS.h"

/* Data structures:
usersList: A list of users.
pwList: A list of passwords.
*/

#if (TESTGEN_TEST_PART == 1) //remove the whole file in part 2
    #define USERS_LIST_LENGTH 3 //has to be >=2

    static char usersList[USERS_LIST_LENGTH][SUBJECT_CN_BUF_SIZE] = {"Yoda", "Yaddle", "Baby Yoda"}; 
    static char pwList[USERS_LIST_LENGTH][PW_SIZE] = {"jediMaster123", "IloveYoda", "theForceIsTheBest"};

    //functions declarations
    uint8_t getServicePermission (const char * xActor, const char * xPW);

    // This function receives an actor name and their password
    // returns 0 for no-login, 1 for user-login, and 2 for admin-login
    uint8_t getServicePermission (const char * xActor, const char * xPW) {
        onPrintf ("\t>>>>>> [getServicePermission]: Received request for <%s> with pw <%s>.\n",xActor,xPW);

        if ( (!strcmp(xActor,"Jedi Order CLNT")) && (!strcmp(xPW,"joy@Work_1999")) )
        {
            onPrintf ("\t>>>>>> [getServicePermission]: Admin access is granted.\n");
            return 2;
        }

        //look for users
        for (int i=0; i < USERS_LIST_LENGTH; i++) {
            if ( (!strcmp(xActor,usersList[i])) && (!strcmp(xPW,pwList[i])) ) {
                onPrintf ("\t>>>>>> [getServicePermission]: User access is granted.\n");
                return 1;
            }
        }

        onPrintf ("\t>>>>>> [getServicePermission]: Invalid username and password.\n");
        return 0;
    }
#endif