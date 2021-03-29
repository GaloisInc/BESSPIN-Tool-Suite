/*
Test_289: Improper Access Control
--- This file has extra parts for the test
-- This file's scope should be protected; otherwise, the test will fail (i.e. CWE exists)
*/

#include "../testsParameters.h"
#include "testgenFreeRTOS.h"

/* Data structures:
usersBlackList: A list of strings. Protected and defined here pre-test.
tasksBlackList: A list of strings. Protected and defined here pre-test.
*/
#define TASK_NAME_SIZE 20
#define USERS_LIST_LENGTH 3 //has to be >=2
#define TASKS_LIST_LENGTH 3 //has to be >=2

#if (TESTGEN_TEST_PART == 1) || (TESTGEN_TEST_PART == 3) 
    static char usersList[USERS_LIST_LENGTH][SUBJECT_CN_BUF_SIZE] = {"SSITH Lord", "Darth Vader", "Sheev Palpatine"}; 
#else //part 2
    static char usersList[USERS_LIST_LENGTH][SUBJECT_CN_BUF_SIZE] = {"SSITH Lord", "Jedi Order Clnt", "Sheev Palpatine"};
#endif

#if (TESTGEN_TEST_PART == 1) || (TESTGEN_TEST_PART == 2) 
    static char tasksList[TASKS_LIST_LENGTH][TASK_NAME_SIZE] = {"vKillYoda", "Viva Darth Sidious", "Destroy The Force"}; 
#else //part 3
    static char tasksList[TASKS_LIST_LENGTH][TASK_NAME_SIZE] = {"vKillYoda", "main:task289", "Destroy The Force"};
#endif

//functions declarations
uint8_t getServicePermission (const char * xActor);

// This function receives an actor name, and returns true/false to whether permission should be given
uint8_t getServicePermission (const char * xActor) {
    
    char * xTask = pcTaskGetName( xTaskGetCurrentTaskHandle() );
    onPrintf ("\t>>>>>> [getServicePermission]: Received request for <%s> from <%s>.\n",xActor,xTask);
    
    //print the list of users
    onPrintf ("\t>>>>>> [getServicePermission]: The unauthorized users are:\n");
    uint8_t authorizedUser = uTRUE;
    for (int i=0; i < USERS_LIST_LENGTH; i++) {
        onPrintf ("\t\t>>> <%s>\n",usersList[i]);
        if (!strcmp(xActor,usersList[i])) {
            authorizedUser = uFALSE;
        }
    }

    //print the list of users
    onPrintf ("\t>>>>>> [getServicePermission]: The unauthorized tasks are:\n");
    uint8_t authorizedTask = uTRUE;
    for (int i=0; i < USERS_LIST_LENGTH; i++) {
        onPrintf ("\t\t>>> <%s>\n",tasksList[i]);
        if (!strcmp(xTask,tasksList[i])) {
            authorizedTask = uFALSE;
        }
    }

    return (authorizedUser & authorizedTask);
}