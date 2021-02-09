/* Test noClearMalloc */
#include "nonstdCommon.h"

static void noClearMallocTest(void);
static void storeSecret(secretLocInfo_t * secretInfo);

#ifdef testgenOnFreeRTOS
    void main() {
        noClearMallocTest();
        return;
    }
#else
    int main() {
        noClearMallocTest();
        return 0;
    }
#endif

static void noClearMallocTest() {
    secretLocInfo_t * secretInfo = mallocSecretInfo();

    //Create a random secret
    secretInfo->secret = createSecret();
    DEBUG_PRINTF("noClearMallocTest: secret created: <%x>\n",secretInfo->secret);
    
    //Store it in a random-sized block + free that block
    storeSecret(secretInfo);
    //Try to find the secret
    findSecret(secretInfo);

    test_free(secretInfo);
    return;
}

static void storeSecret(secretLocInfo_t * secretInfo) {
    unsigned char *pSecret;
    unsigned int iByte;
    size_t xSizeToMalloc;

    xSizeToMalloc = (size_t) ((rand() % (MALLOC_BLOCK_SIZE_MAX-MALLOC_BLOCK_SIZE_MIN+1)) + MALLOC_BLOCK_SIZE_MIN);
    pSecret = (unsigned char*) test_malloc(xSizeToMalloc*sizeof(unsigned char));
    if (pSecret == NULL) {
        puts("storeSecret: Failed to malloc.\n TEST ERROR.\n");
        EXIT;
    }
    
    // Do not use memset without using the data, otherwise, the compiler might omit it. For loop works.
    for (iByte=0; iByte<xSizeToMalloc; iByte++) {
        pSecret[iByte] = secretInfo->secret;
    }
    DEBUG_PRINTF("storeSecret: Secret stored in <%lx> with size <%lx>!\n",
                    (unsigned long int) pSecret, (unsigned long int) xSizeToMalloc);
    secretInfo->pSecret = pSecret;
    secretInfo->szSecret = xSizeToMalloc;
    
    test_free(pSecret);

    return;
}
