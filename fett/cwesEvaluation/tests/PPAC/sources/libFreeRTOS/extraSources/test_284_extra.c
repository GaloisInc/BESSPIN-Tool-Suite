/*
Test_284: Improper Access Control
--- This file has extra parts for the test
-- This file's scope should be protected; otherwise, the test will fail (i.e. CWE exists)
*/

#include "../testsParameters.h"
#include "testgenFreeRTOS.h"

/* Data structures:
usersList: A list of strings. Protected and defined here pre-test.
loggingItem: a "actorName"-"accepted/rejected" pair.
log: A queue of loggingItems. Protected and defined here.
*/
#define USERS_LIST_LENGTH 3 //has to be >=2
#define LOG_QUEUE_LENGTH 3

#if (TESTGEN_TEST_PART == 2) || (TESTGEN_TEST_PART == 4)
    static char usersList[USERS_LIST_LENGTH][SUBJECT_CN_BUF_SIZE] = {"Yoda", "Jedi Order CLNT", "Baby Yoda"}; 
#elif TESTGEN_TEST_PART == 3
    char usersList[USERS_LIST_LENGTH][SUBJECT_CN_BUF_SIZE] = {"Yoda", "Galois", "Baby Yoda"}; 
#else //part 1
    static char usersList[USERS_LIST_LENGTH][SUBJECT_CN_BUF_SIZE] = {"Yoda", "Galois", "Baby Yoda"}; 
#endif

// The logItem struct
struct logItem {
    char xActor[SUBJECT_CN_BUF_SIZE];
    uint8_t reqAns;
};

// The log
#if TESTGEN_TEST_PART == 4
    QueueHandle_t logQueue = NULL;
#else
    static QueueHandle_t logQueue = NULL;
#endif

//functions declarations
uint8_t getServicePermission (const char * xActor);
static void logServiceRequest (const char * xActor, uint8_t reqAns);
void dumpLogContents (void);

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
    logServiceRequest (xActor, authorizedUser);
    return authorizedUser;
}

// This function logs the action
static void logServiceRequest (const char * xActor, uint8_t reqAns) {
    if (logQueue == NULL) { //nothing has been logged yet --> create queue
        logQueue = xQueueCreate( LOG_QUEUE_LENGTH, sizeof(struct logItem *));
        if (logQueue == NULL) {
            onPrintf ("<INVALID> [logServiceRequest]: Failed to create a log Queue.\n");
            prEXIT(1);
        }
    }

    //create an item
    struct logItem * xLogItem = (struct logItem *) pvPortMalloc (sizeof(struct logItem));
    if (xLogItem == NULL) {
        onPrintf ("<INVALID> [logServiceRequest]: Failed to create a log item for <%s>.\n",xActor);
        prEXIT(1);
    }
    strcpy (xLogItem->xActor, xActor);
    xLogItem->reqAns = reqAns;

    //add the item to the queue
    BaseType_t queueReturn = xQueueSend(logQueue, (void *) &xLogItem, 0);
    if (queueReturn != pdTRUE) {
        onPrintf ("<INVALID> [logServiceRequest]: Failed to send to the queue the log item for <%s>. [ret=%d]\n",xActor, queueReturn);
        prEXIT(1);
    }

    return;
}

// This function prints the queue log
void dumpLogContents (void) {
    onPrintf ("\nxxxxxxxxxx Dumping the log queue xxxxxxxxxx \n");
    if (logQueue == NULL) {
        onPrintf ("\n");
        return;
    }
    BaseType_t queueReturn = pdTRUE;
    while (queueReturn == pdTRUE) {
        struct logItem * xItem; 
        queueReturn = xQueueReceive(logQueue, &xItem, 0);
        if (queueReturn == pdTRUE) {
            onPrintf ("<logQueue>: <%s>:<%d>\n",xItem->xActor,xItem->reqAns);
        }
    }
    onPrintf ("\n");
    return;
}
