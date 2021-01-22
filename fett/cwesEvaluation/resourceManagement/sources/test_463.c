#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#define STR_SIZE_MIN 1
#define STR_SIZE_MAX 100 //Arbitrary value
#define SECRET_SIZE 4 //chosen arbitrarily -->  4*sizeof(int) = 16 bytes (the golden keyword is 16*'A')

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

static void deleteStrSentinel (void); 

// --------------- FreeRTOS Test ---------------
#ifdef testgenOnFreeRTOS
    #define NUM_OF_TEST_PARTS 1

    void main() {
        printf("\n<OSIMAGE=FreeRTOS>\n");
        #if TESTGEN_TEST_PART == 1
            deleteStrSentinel();
            printf("\n<END-OF-MAIN>\n");
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",TESTGEN_TEST_PART,NUM_OF_TEST_PARTS);
        #endif
        return;
    }

// --------------- Debian && FreeBSD test ---------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))
    int main(void);

    int main() {
        deleteStrSentinel();
        printf("\n<END-OF-MAIN>\n");
        return 0;
    }

#endif //ifdef testgenOnFreeRTOS

static void deleteStrSentinel () {
    char * pTargetStr;
    size_t szStr, szPtrDiff;
    int *pSecretInt, i;

    srand(RM_SEED); //RM_SEED is written in fett/cwesEvaluation/build.py
    szStr = (size_t) ((rand() % (STR_SIZE_MAX-STR_SIZE_MIN+1)) + STR_SIZE_MIN);
    pTargetStr = (char *) MALLOC (sizeof(char)*szStr);
    pSecretInt = (int *) MALLOC (sizeof(int)*SECRET_SIZE);

    szPtrDiff = ((size_t) pSecretInt) - ((size_t) pTargetStr);
    printf("<PTR-DIFF=%d>\n",(unsigned) szPtrDiff);
    
    for (i=0; i<SECRET_SIZE; i++) {
        pSecretInt[i] = 0x41414141; //"AAAA"
    }

    memset(pTargetStr,'s',szStr-1); //fill string with the letter 's'
    pTargetStr[szStr-1] = 0;
    printf("len<%s>:%d\n",pTargetStr,(unsigned) szStr);

    //overwrite the sentinel with 'x' and ensure all nibbles are non-zero all the way up to the secret integer
    memset(&pTargetStr[szStr-1],'x',szPtrDiff-szStr+1);
    printf("<%s>\n",pTargetStr);
    
    FREE(pTargetStr);
    //FREE(pSecretInt); //To avoid the double free since the pointers areas will get confused

    return;
}