#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include "testsParameters.h"

#if (defined(testgenOnFreeRTOS) && defined(testgenQEMU))
    #define MALLOC_BLOCK_SIZE_MAX 0x004F //Maximum allocatable size in FreeRTOS qemu
    #define MALLOC_BLOCK_SIZE_MIN 0x0020 //A block of 32 bytes
#else
    #define MALLOC_BLOCK_SIZE_MAX 0x00FF 
    #define MALLOC_BLOCK_SIZE_MIN 0x0064 //A block of 100 bytes
#endif
#define MAX_SECRET_VALUE 0xFE //Avoid all ones
#define MIN_SECRET_VALUE 0x02 //Avoid zero and one
#define N_MATCHES_TO_COUNT 4 //Have to find the byte value 4 times to avoid unfortunate coincidences

#define TEST_FAILED 0x1
#define TEST_CHECKED 0x2 

#ifdef testgenOnFreeRTOS
    #include "FreeRTOS.h"
    #include "task.h"
    #define EXIT puts(">>>End of Fett<<<\n"); vTaskDelete(NULL)   
#else
    #define EXIT exit(1)
#endif

#if defined(testgenOnFreeRTOS) && defined(testgenFPGA)
    #define test_malloc pvPortMalloc
    #define test_free   vPortFree
#else
    #define test_malloc malloc
    #define test_free   free
#endif
    
#ifdef DEBUG
    #define DEBUG_PRINTF(...) printf(__VA_ARGS__)
#else
    #define DEBUG_PRINTF(...)
#endif

typedef struct secretLocInfo_ {
    unsigned char secret;
    unsigned char *pSecret;
    size_t szSecret;
} secretLocInfo_t;

static void noClearMallocTest(void);
static unsigned char createSecret(void);
static void storeSecret(secretLocInfo_t * secretInfo);
static void findSecret(secretLocInfo_t * secretInfo);

#ifdef testgenOnFreeRTOS
    void main() {
        noClearMallocTest();
        return;
    }
#else
    int main(void);
    int main() {
        noClearMallocTest();
        return 0;
    }
#endif

static void noClearMallocTest() {
    secretLocInfo_t * secretInfo;

    //allocate the secret info struct
    secretInfo = (secretLocInfo_t*) test_malloc(sizeof(secretLocInfo_t));
    if (secretInfo == NULL) {
        puts("noClearMallocTest: Failed to malloc.\n TEST ERROR.\n");
        EXIT;
    }

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

static unsigned char createSecret () {
    srand(IEX_SEED); //IEX_SEED is written in fett/cwesEvaluation/build.py
    return (unsigned char) ((rand() % (MAX_SECRET_VALUE-MIN_SECRET_VALUE+1) + MIN_SECRET_VALUE));
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
    DEBUG_PRINTF("storeSecret: Secret stored in <%lx>!\n",(unsigned long int) pSecret);
    secretInfo->pSecret = pSecret;
    secretInfo->szSecret = xSizeToMalloc;
    
    test_free(pSecret);

    return;
}

static void findSecret(secretLocInfo_t * secretInfo) {
    unsigned char *pCheck;
    int matchCount = N_MATCHES_TO_COUNT;

    pCheck = secretInfo->pSecret;
    while ((pCheck <= (secretInfo->pSecret+secretInfo->szSecret)) && (matchCount>0)) {
        DEBUG_PRINTF("findSecret: matchCount=%d: (*pCheck=<%x>)\n",matchCount,*pCheck);
        if (*pCheck == secretInfo->secret) {
            matchCount--;
        }
        pCheck++;
    }

    if (matchCount<=0) {
        puts("TEST FAILED\n");
    } else {
        puts ("TEST PASSED\n");
    }

    return;
}
