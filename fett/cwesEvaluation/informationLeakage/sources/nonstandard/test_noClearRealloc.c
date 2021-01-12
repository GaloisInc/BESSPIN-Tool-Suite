/* Test noClearRealloc */
#include "nonstdCommon.h"

static void noClearReallocTest(void);
static unsigned char * storeSecret(secretLocInfo_t * secretInfo);

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
        if ((ptr == NULL) && (size = 0)) {
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

#ifdef testgenOnFreeRTOS
    void main() {
        noClearReallocTest();
        return;
    }
#else
    int main() {
        noClearReallocTest();
        return 0;
    }
#endif

static void noClearReallocTest() {
    unsigned char * pReallocatedSecret;
    secretLocInfo_t * secretInfo = mallocSecretInfo();

    //Create a random secret
    secretInfo->secret = createSecret();
    DEBUG_PRINTF("noClearReallocTest: secret created: <%x>\n",secretInfo->secret);

    //Store it in a random-sized block + realloc that block
    pReallocatedSecret = storeSecret(secretInfo);

    //Try to find the secret
    findSecret(secretInfo);

    test_free(pReallocatedSecret);
    test_free(secretInfo);
    return;
}

static unsigned char * storeSecret(secretLocInfo_t * secretInfo) {
    unsigned char *pSecret;
    unsigned int iByte;
    size_t xSizeToMalloc;

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
    xSizeToMalloc = (size_t) ((rand() % (MALLOC_BLOCK_SIZE_MAX-MALLOC_BLOCK_SIZE_MIN+1)) + MALLOC_BLOCK_SIZE_MIN);
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