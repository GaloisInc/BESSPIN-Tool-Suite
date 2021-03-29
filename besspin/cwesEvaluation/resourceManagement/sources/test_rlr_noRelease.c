#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_QEMU))
    #define MALLOC_SIZE_MAX 0x008F 
    #define MALLOC_SIZE_MIN 0x0000
#else
    #define MALLOC_SIZE_MAX 0xFFFF 
    #define MALLOC_SIZE_MIN 0xF000
#endif

#define N_CALLS 50
#define PERCENT_NO_FREE 5 //Do not free 1 in 5 calls

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

static void noRelease (int i); 

// --------------- FreeRTOS Test ---------------
#ifdef BESSPIN_FREERTOS
    #define NUM_OF_TEST_PARTS 1

    void main() {
        int i;
        printf("\n<OSIMAGE=FreeRTOS>\n");
        srand(RM_SEED); //RM_SEED is written in besspin/cwesEvaluation/build.py
        #if BESSPIN_TEST_PART == 1
            for (i=0;i<N_CALLS;i++) {
                noRelease(i);
            }
            printf("\n<END-OF-MAIN>\n");
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",BESSPIN_TEST_PART,NUM_OF_TEST_PARTS);
        #endif
        return;
    }

// --------------- Debian && FreeBSD test ---------------
#elif (defined(BESSPIN_DEBIAN) || defined(BESSPIN_FREEBSD))
#include "unbufferStdout.h"
    int main(void);

    int main() {
        unbufferStdout();
        int i;
        srand(RM_SEED); //RM_SEED is written in besspin/cwesEvaluation/build.py
        for (i=0;i<N_CALLS;i++) {
            noRelease(i);
        }
        printf("\n<END-OF-MAIN>\n");
        return 0;
    }

#endif //ifdef BESSPIN_FREERTOS

static void noRelease (int i) {
    char * p;
    size_t xSizeToMalloc;

    xSizeToMalloc = (size_t) ((rand() % (MALLOC_SIZE_MAX-MALLOC_SIZE_MIN+1)) + MALLOC_SIZE_MIN);
    p = (char *) MALLOC(xSizeToMalloc * sizeof(char)); 
    if (p == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return;
    }
    if (rand()%PERCENT_NO_FREE) {
        FREE(p);
        printf("<%d>: <FREE>.\n",i);
    } else {
        printf("<%d>: <NO-FREE>.\n",i);
    }

    return;
}
