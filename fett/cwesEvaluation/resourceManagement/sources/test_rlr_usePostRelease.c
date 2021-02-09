#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenQEMU))
    #define MALLOC_SIZE_MAX 0x004F 
    #define MALLOC_SIZE_MIN 0x0000
#else
    #define MALLOC_SIZE_MAX 0xFFFF 
    #define MALLOC_SIZE_MIN 0xF000
#endif

#define N_CALLS 50
#define PERCENT_USE 3 //use after free only once in 3 calls

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

static void usePostRelease (int i, int isSource);

// --------------- FreeRTOS Test ---------------
#ifdef testgenOnFreeRTOS
    #define NUM_OF_TEST_PARTS 2

    void main() {
        int i;
        int isSource;
        printf("\n<OSIMAGE=FreeRTOS>\n");
        srand(RM_SEED); //RM_SEED is written in fett/cwesEvaluation/build.py
        #if TESTGEN_TEST_PART == 1
            printf("\n---Part01: Use as <source>.---\n");
            isSource = 1;
        #elif TESTGEN_TEST_PART == 2
            printf("\n---Part02: Use as <destination>.---\n");
            isSource = 0;
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",TESTGEN_TEST_PART,NUM_OF_TEST_PARTS);
            return;
        #endif

        for (i=0;i<N_CALLS;i++) {
            usePostRelease(i, isSource);
        }
        printf("\n<END-OF-MAIN>\n");
        return;
    }

// --------------- Debian && FreeBSD test ---------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))
    int main(int argc, char *argv[]);

    int main(int argc, char *argv[]) {
        int i, option, isSource;
        srand(RM_SEED); //RM_SEED is written in fett/cwesEvaluation/build.py
        if (argc > 1) { //be safe
            option = atoi(argv[1]);
        } else {
            option = -1;
        }
        switch(option) {
            case 1 :
                printf("\n<source>\n");
                isSource = 1;
                break;
            case 2 :
                printf("\n<destination>\n");
                isSource = 0;
                break;
            default :
                printf("\n<INVALID> Part[%d] not in [1,2].\n",option);
                return 1;
        }  
        for (i=0;i<N_CALLS;i++) {
            usePostRelease(i,isSource);
        }
        printf("\n<END-OF-MAIN>\n");
        return 0;
    }

#endif //ifdef testgenOnFreeRTOS

static void usePostRelease (int i, int isSource) {
    char *pMain, *pSecond, *pExtra1, *pExtra2, *pExtra3;
    size_t xSizeToMallocMain, xSizeToMallocExtra;
    xSizeToMallocMain = (size_t) ((rand() % (MALLOC_SIZE_MAX-MALLOC_SIZE_MIN+1)) + MALLOC_SIZE_MIN);
    pMain = (char *) MALLOC(xSizeToMallocMain * sizeof(char));
    pSecond = (char *) MALLOC(xSizeToMallocMain * sizeof(char)); 
    if ((pMain == NULL) || (pSecond == NULL)) {
        printf("<INVALID> Failed to Malloc.\n");
        return;
    }
    FREE(pMain);
    xSizeToMallocExtra = (size_t) ((rand() % (MALLOC_SIZE_MAX-MALLOC_SIZE_MIN+1)) + MALLOC_SIZE_MIN);
    pExtra1 = (char *) MALLOC(xSizeToMallocExtra * sizeof(char)); 
    pExtra2 = (char *) MALLOC(xSizeToMallocExtra * sizeof(char)); 
    pExtra3 = (char *) MALLOC(xSizeToMallocExtra * sizeof(char)); 
    if ((pExtra1 == NULL) || (pExtra2 == NULL) || (pExtra3 == NULL)) {
        printf("<INVALID> Failed to Malloc.\n");
        return;
    }
    if (rand()%PERCENT_USE) {
        printf("<%d>: <NO-USE>.\n",i);
    } else { //use post free
        printf("<%d>: <USE-POST-FREE>.\n",i);
        if (isSource==1) { //use it as source
            printf("<%d>: <SOURCE>.\n",i);
            memcpy (pSecond,pMain,xSizeToMallocMain);
        } else { //use it as destination
            printf("<%d>: <DESTINATION>.\n",i);
            memcpy (pMain,pSecond,xSizeToMallocMain);
        }
    }

    FREE(pExtra1);
    FREE(pExtra2);
    FREE(pExtra3);
    FREE(pSecond);
    
    return;
}