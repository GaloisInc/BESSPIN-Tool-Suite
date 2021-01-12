/* This has the common functions for nonstandard tests */
#include "nonstdCommon.h"

secretLocInfo_t * mallocSecretInfo () {
    secretLocInfo_t * secretInfo = (secretLocInfo_t*) test_malloc(sizeof(secretLocInfo_t));
    if (secretInfo == NULL) {
        puts("allocSecretInfo: Failed to malloc.\n TEST ERROR.\n");
        EXIT;
    }
    return secretInfo;
}

unsigned char createSecret () {
    srand(IEX_SEED); //IEX_SEED is written in fett/cwesEvaluation/build.py
    return (unsigned char) ((rand() % (MAX_SECRET_VALUE-MIN_SECRET_VALUE+1) + MIN_SECRET_VALUE));
}

void findSecret(secretLocInfo_t * secretInfo) {
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