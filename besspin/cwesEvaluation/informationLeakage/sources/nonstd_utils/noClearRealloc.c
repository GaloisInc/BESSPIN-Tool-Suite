/* Functions for noClearRealloc */
#include "noClearRealloc.h"

static unsigned char * storeSecret(secretLocInfo_t * secretInfo, reallocSize_t option);

// Define a _manual_ realloc for FreeRTOS because heap_4 does not define a realloc
#if defined(testgenOnFreeRTOS) && defined(testgenFPGA)
    #define test_realloc(ptr, size, oldSize) manualRealloc(ptr, size, oldSize)
    static void *manualRealloc(void *ptr, size_t size, size_t oldSize);
#else
    #define test_realloc(ptr, size, oldSize) realloc(ptr,size) 
#endif

#if defined(testgenOnFreeRTOS) && defined(testgenFPGA)
    static void *manualRealloc(void *ptr, size_t size, size_t oldSize) {
        void *pReturn;

        // First, arguments exceptions
        if ((ptr == NULL) && (size == 0)) {
            return NULL;
        }
        if (size == 0) {
            vPortFree(ptr);
            return NULL;
        }
        if (ptr == NULL) {
            return pvPortMalloc(size);
        }

        //Second, the manual realloc
        pReturn = pvPortMalloc (size);
        if (pReturn == NULL) {
            puts("manualRealloc: Failed to malloc.\n TEST ERROR.\n");
            EXIT;
            return NULL;
        }
        memcpy (pReturn, ptr, size);
        vPortFree(ptr);
        return pReturn;
    }
#endif

void noClearReallocTest(reallocSize_t option) {
    unsigned char * pReallocatedSecret;
    secretLocInfo_t * secretInfo = mallocSecretInfo();

    //Create a random secret
    secretInfo->secret = createSecret();
    DEBUG_PRINTF("noClearReallocTest: secret created: <%x>\n",secretInfo->secret);

    //Store it in a random-sized block + realloc that block
    pReallocatedSecret = storeSecret(secretInfo, option);

    //Try to find the secret
    findSecret(secretInfo);

    test_free(pReallocatedSecret);
    test_free(secretInfo);
    return;
}

static unsigned char * storeSecret(secretLocInfo_t * secretInfo, reallocSize_t option) {
    unsigned char *pSecret;
    unsigned int iByte;
    size_t xSizeToMalloc;
    size_t realloc_max, realloc_min; //the range to choose from

    xSizeToMalloc = (size_t) ((rand() % (MALLOC_BLOCK_SIZE_MAX-MALLOC_BLOCK_SIZE_MIN+1)) + MALLOC_BLOCK_SIZE_MIN);
    pSecret = (unsigned char*) test_malloc(xSizeToMalloc*sizeof(unsigned char));
    if (pSecret == NULL) {
        puts("storeSecret: Failed to malloc.\n TEST ERROR.\n");
        EXIT;
    }
    // In the info, store the info of the secret
    secretInfo->pSecret = pSecret;
    secretInfo->szSecret = xSizeToMalloc;
    
    // Do not use memset without using the data, otherwise, the compiler might omit it. For loop works.
    for (iByte=0; iByte<xSizeToMalloc; iByte++) {
        pSecret[iByte] = secretInfo->secret;
    }
    DEBUG_PRINTF("storeSecret: Secret stored in <%lx> with size <%lx>!\n",
                    (unsigned long int) pSecret,(unsigned long int) xSizeToMalloc);
    
    //Now let's realloc to a new random size, and lose reference to the old pointer
    switch (option) {
        case SHRINK:
            realloc_max = xSizeToMalloc - (size_t) DELTA_SIZE_MIN;
            realloc_min = (size_t) (MALLOC_BLOCK_SIZE_MIN - DELTA_SIZE_MIN);
            break;
        case EXPAND:
            realloc_max = (size_t) (MALLOC_BLOCK_SIZE_MAX + DELTA_SIZE_MIN);
            realloc_min = xSizeToMalloc + (size_t) DELTA_SIZE_MIN;
            break;
        default:
            puts("storeSecret: Unrecognized realloc size option.\n TEST ERROR.\n");
            EXIT;
    }
    xSizeToMalloc = (size_t) ((rand() % (realloc_max-realloc_min+1)) + realloc_min);
    pSecret = (unsigned char*) test_realloc(pSecret, xSizeToMalloc*sizeof(unsigned char),
                                    secretInfo->szSecret*sizeof(unsigned char));
    if (pSecret == NULL) {
        puts("storeSecret: Failed to realloc.\n TEST ERROR.\n");
        EXIT;
    }
    DEBUG_PRINTF("storeSecret: Reallocated at <%lx> with size <%lx>!\n",
                    (unsigned long int) pSecret, (unsigned long int) xSizeToMalloc);

    return pSecret;
}