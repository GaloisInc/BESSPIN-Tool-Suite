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

static void deleteStrSentinel (short testPart); 

// --------------- FreeRTOS Test ---------------
#ifdef testgenOnFreeRTOS
    #define NUM_OF_TEST_PARTS 2

    void main() {
        printf("\n<OSIMAGE=FreeRTOS>\n");
        #if TESTGEN_TEST_PART == 1
            printf("\n---Part01: Delete sentinel and printf---\n");
            deleteStrSentinel(TESTGEN_TEST_PART);
        #elif TESTGEN_TEST_PART == 2
            printf("\n---Part02: Out-of-bound memset---\n");
            deleteStrSentinel(TESTGEN_TEST_PART);
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",TESTGEN_TEST_PART,NUM_OF_TEST_PARTS);
            return;
        #endif

        printf("\n<END-OF-MAIN>\n");
        return;
    }

// --------------- Debian && FreeBSD test ---------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))
    int main(int argc, char *argv[]);

    int main(int argc, char *argv[]) {
        int option;
        if (argc > 1) { //be safe
            option = atoi(argv[1]);
        } else {
            option = -1;
        }

        switch(option) {
            case 1 :
                deleteStrSentinel(option);
                break;
            case 2 :
                deleteStrSentinel(option);
                break;
            default :
                printf("\n<INVALID> Part[%d] not in [1,2].\n",option);
                return 1;
        }
        printf("\n<END-OF-MAIN>\n");
        return 0;
    }

#endif //ifdef testgenOnFreeRTOS

static void deleteStrSentinel (short testPart) {
    char * pTargetStr;
    size_t szStr, szPtrDiff;
    int *pSecretInt, i;

    srand(RM_SEED); //RM_SEED is written in fett/cwesEvaluation/build.py
    szStr = (size_t) ((rand() % (STR_SIZE_MAX-STR_SIZE_MIN+1)) + STR_SIZE_MIN);
    pTargetStr = (char *) MALLOC (sizeof(char)*szStr);
    if (pTargetStr == NULL) {
        printf("<INVALID> Failed to Malloc the char*.\n");
        return;
    }
    
    //fill string with the letter 's'
    memset(pTargetStr,'s',szStr-1); 
    pTargetStr[szStr-1] = 0;
    printf("len<%s>:%d\n",pTargetStr,(unsigned) szStr);
    
    //Overwrite the sentinel
    pTargetStr[szStr-1] = 'x';

    if (testPart==1) { // PART01
        printf("<%s>\n",pTargetStr);
        printf("<OVERWRITTEN-STR-SENTINEL>\n");
    } else { // PART02
        pSecretInt = (int *) MALLOC (sizeof(int)*SECRET_SIZE);
        if (pSecretInt == NULL) {
            printf("<INVALID> Failed to Malloc the int*.\n");
            return;
        }

        szPtrDiff = ((size_t) pSecretInt) - ((size_t) pTargetStr);
        printf("<PTR-DIFF=%d>\n",(unsigned) szPtrDiff);

        for (i=0; i<SECRET_SIZE; i++) {
            pSecretInt[i] = 0x41414141; //"AAAA"; the secret
        }

        //Out-of-boundary and ensure all nibbles are non-zero all the way up to the secret integer
        memset(&pTargetStr[szStr],'x',szPtrDiff-szStr);
        printf("<%s>\n",pTargetStr);
    }
    
    FREE(pTargetStr);
    //FREE(pSecretInt); //To avoid the double free since the pointers areas will get confused (would have to go inside the if)
    return;
}