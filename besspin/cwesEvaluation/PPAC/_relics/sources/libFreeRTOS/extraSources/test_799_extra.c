/*
Test_799: Improper Control of Interaction Frequency
--- This file has extra parts for the test
-- This file's scope should be protected; otherwise, the test will fail (i.e. CWE exists)
*/

#include "../testsParameters.h"
#include "testgenFreeRTOS.h"

// Data structure: A singly-linked-list of "actorName"-"sempahoreHandle" pairs

// The pair struct
struct actorSemphrPair {
    char * xActor;
    SemaphoreHandle_t xSemphr;
    struct actorSemphrPair * pPrevious;
};

//The linked-list beginning
#if TESTGEN_TEST_PART == 3
    struct actorSemphrPair * requestsLL = NULL;
#else
    static struct actorSemphrPair * requestsLL = NULL;
#endif

//functions declarations
uint8_t getServicePermission (const char * xActor);
#if TESTGEN_TEST_PART == 2
    SemaphoreHandle_t getSemphrHandle (const char * xActor);
#else
    static SemaphoreHandle_t getSemphrHandle (const char * xActor);
#endif
static SemaphoreHandle_t createPairForActor (const char * xActor);

// This function receives an actor name, and returns true/false to whether permission should be given
uint8_t getServicePermission (const char * xActor) {
    //Search if the actor had already submitted a request
    SemaphoreHandle_t xSemphr = getSemphrHandle (xActor);
    if (xSemphr == NULL) { //this is the actor's first request
        onPrintf ("\t>>>>>> [getServicePermission]: <%s> has not contacted the server before.\n",xActor);
        xSemphr = createPairForActor (xActor);
        if (xSemphr == NULL) {
            exitTest (1);
            return uFALSE;
        }
    } 
    //try to take request
    UBaseType_t ithRequest = nAllowedInteractions - uxSemaphoreGetCount(xSemphr) + 1;
    onPrintf ("\t>>>>>> [getServicePermission]: This is request #%d for <%s>\n",ithRequest,xActor);
    if (xSemaphoreTake(xSemphr,0) == pdTRUE) {
        return uTRUE;
    } else {
        return uFALSE;
    }
}

// This function adds a pair for an actor
static SemaphoreHandle_t createPairForActor (const char * xActor) {
    struct actorSemphrPair * xPair = (struct actorSemphrPair *) pvPortMalloc (sizeof(struct actorSemphrPair));
    if (xPair == NULL) {
        onPrintf ("<INVALID> [createPairForActor]: Failed to malloc a pair for <%s>.\n",xActor);
        return NULL;
    }
    //initialize values
    xPair->xActor = (char *) pvPortMalloc ((strlen(xActor)+1)*sizeof(char));
    if (xPair->xActor == NULL) {
        onPrintf ("<INVALID> [createPairForActor]: Failed to malloc a char* for <%s>.\n",xActor);
        return NULL;
    }
    strcpy (xPair->xActor,xActor);
    xPair->xSemphr = xSemaphoreCreateCounting((UBaseType_t) nAllowedInteractions, (UBaseType_t) nAllowedInteractions);
    if (xPair == NULL) {
        onPrintf ("<INVALID> [createPairForActor]: Failed to create a semaphore for <%s>.\n",xActor);
        return NULL;
    }

    xPair->pPrevious = requestsLL;
    requestsLL = xPair;

    return xPair->xSemphr;
}

// This function fetches the semaphore handle for a certain actor
#if TESTGEN_TEST_PART == 2
    SemaphoreHandle_t getSemphrHandle (const char * xActor)
#else
    static SemaphoreHandle_t getSemphrHandle (const char * xActor)
#endif
{
    struct actorSemphrPair * xPair = requestsLL;
    while (xPair != NULL) {
        if (!strcmp (xActor,xPair->xActor)) {
            return xPair->xSemphr;
        }
        xPair = xPair->pPrevious;
    }
    return NULL;
}