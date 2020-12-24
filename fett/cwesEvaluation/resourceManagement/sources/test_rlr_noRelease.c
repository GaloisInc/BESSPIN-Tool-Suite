#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>

#define MALLOC_SIZE_MAX 0xFFFF 
#define MALLOC_SIZE_MIN 0xF000
#define N_CALLS 50
#define PERCENT_NO_FREE 5 //Do not free 1 in 5 calls

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

static void noRelease (int i); 

// --------------- FreeRTOS Test ---------------
#ifdef testgenOnFreeRTOS
    #define NUM_OF_TEST_PARTS 1

    void main() {
        int i;
        printf("\n<OSIMAGE=FreeRTOS>\n");
        srand(RM_SEED); //RM_SEED is written in fett/cwesEvaluation/build.py
        #if TESTGEN_TEST_PART == 1
            for (i=0;i<N_CALLS;i++) {
                noRelease(i);
            }
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
        int i;
        srand(RM_SEED); //RM_SEED is written in fett/cwesEvaluation/build.py
        for (i=0;i<N_CALLS;i++) {
            noRelease(i);
        }
        printf("\n<END-OF-MAIN>\n");
        return 0;
    }

#endif //ifdef testgenOnFreeRTOS

static void noRelease (int i) {
    char * p;
    size_t xSizeToMalloc;

    xSizeToMalloc = (size_t) ((rand() % (MALLOC_SIZE_MAX-MALLOC_SIZE_MIN+1)) + MALLOC_SIZE_MIN);
    p = (char *) MALLOC(xSizeToMalloc * sizeof(char)); 
    if (rand()%PERCENT_NO_FREE) {
        FREE(p);
        printf("<%d>: <FREE>.\n",i);
    } else {
        printf("<%d>: <NO-FREE>.\n",i);
    }

    return;
}