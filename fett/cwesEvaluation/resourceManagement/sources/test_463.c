#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#define STR_SIZE_MIN 1
#define STR_SIZE_MAX 24 //For the malloc to be within 32 bits
#define SECRET_SIZE 4 //chosen arbitrary -->  4*sizeof(int) = 16 bytes (the golden keyword is 16*'A')

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
    char * targetStr;
    size_t strLen;
    int *secretInt, i;

    srand(RM_SEED); //RM_SEED is written in fett/cwesEvaluation/build.py
    strLen = (size_t) ((rand() % (STR_SIZE_MAX-STR_SIZE_MIN+1)) + STR_SIZE_MIN);
    targetStr = (char *) MALLOC (sizeof(char)*strLen);
    secretInt = (int *) MALLOC (sizeof(int)*SECRET_SIZE);

    printf("<DIFF-PTR=%x>\n",(unsigned) (secretInt)  - (unsigned) (targetStr)); //This has to be "20" for the test to work
    
    for (i=0; i<SECRET_SIZE; i++) {
        secretInt[i] = 0x41414141; //"AAAA"
    }

    memset(targetStr,'s',strLen-1); //fill string with the letter 's'
    targetStr[strLen] = 0;
    printf("len<%s>:%ld\n",targetStr,(unsigned) strLen);

    //overwrite the sentinel with 'x' and ensure all nibbles are non-zero up to the secret integer
    memset(&targetStr[strLen-1],'x',8*sizeof(int)-strLen+1);
    printf("<%s>\n",targetStr);
    
    FREE(targetStr);
    //FREE(secretInt); //To avoid the double free since the pointers areas will get confused

    return;
}