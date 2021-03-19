#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#ifdef testgenOnFreeRTOS
    #define ALLOC_SIZE_MAX 0x004F
    #define ALLOC_SIZE_MIN 0x0000
#else
    #define ALLOC_SIZE_MAX 0xFFFF
    #define ALLOC_SIZE_MIN 0xF000
#endif

#define N_CALLS 50
#define PERCENT_USE 3 //use after free only once in 3 calls

static void usePostRelease (int i, int isSource);

// --------------- FreeRTOS Test ---------------
#ifdef testgenOnFreeRTOS
    #define NUM_OF_TEST_PARTS 2

    void main() {
        int i;
        int isSource;
        printf("\n<OSIMAGE=FreeRTOS>\n");
        srand(RM_SEED); //RM_SEED is written in besspin/cwesEvaluation/build.py
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
#include "unbufferStdout.h"
    int main(int argc, char *argv[]);

    int main(int argc, char *argv[]) {
        unbufferStdout();
        int i, option, isSource;
        srand(RM_SEED); //RM_SEED is written in besspin/cwesEvaluation/build.py
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

static char* stackAlloc(size_t elements) {
    char buf[elements];
    char *ret = buf;
    return ret;
}

static size_t getSize() {
    return (size_t) ((rand() % (ALLOC_SIZE_MAX-ALLOC_SIZE_MIN+1)) + ALLOC_SIZE_MIN);
}

static void usePostRelease(int i, int isSource) {
    size_t xSizeToAllocMain = getSize();
    char* pMain = stackAlloc(xSizeToAllocMain * sizeof(char));
    if (!pMain) {
        // Compiler replaced SubStr_new_stack return with `return NULL`.
        printf("<INVALID> Null pMain.\n");
        exit(1);
    }
    char aSecond[xSizeToAllocMain];
    memset(aSecond, 0, xSizeToAllocMain);
    size_t xSizeToAllocExtra = getSize();
    char aExtra1[xSizeToAllocExtra] __attribute__((unused));
    char aExtra2[xSizeToAllocExtra] __attribute__((unused));
    char aExtra3[xSizeToAllocExtra] __attribute__((unused));

    if (rand()%PERCENT_USE) {
        printf("<%d>: <NO-USE>.\n",i);
    } else { //use post free
        printf("<%d>: <USE-POST-FREE>.\n",i);
        if (isSource==1) { //use it as source
            printf("<%d>: <SOURCE>.\n",i);
            memcpy (aSecond,pMain,xSizeToAllocMain);
        } else { //use it as destination
            printf("<%d>: <DESTINATION>.\n",i);
            memcpy (pMain,aSecond,xSizeToAllocMain);
        }
    }
}
