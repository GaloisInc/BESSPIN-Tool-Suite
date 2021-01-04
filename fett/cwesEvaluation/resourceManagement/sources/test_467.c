#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#define MALLOC_SIZE_MAX 0x00FF
#define MALLOC_SIZE_MIN 0x0000

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

static void sizeofPtr (void); 

// --------------- FreeRTOS Test ---------------
#ifdef testgenOnFreeRTOS
    #define NUM_OF_TEST_PARTS 1

    void main() {
        printf("\n<OSIMAGE=FreeRTOS>\n");
        #if TESTGEN_TEST_PART == 1
            sizeofPtr();
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
        sizeofPtr();
        printf("\n<END-OF-MAIN>\n");
        return 0;
    }

#endif //ifdef testgenOnFreeRTOS

static void sizeofPtr() {
    long unsigned int xInt, *pInt;
    size_t xSizeToMalloc;
    char xChar, *pChar;

    xSizeToMalloc = (size_t) ((rand() % (MALLOC_SIZE_MAX-MALLOC_SIZE_MIN+1)) + MALLOC_SIZE_MIN);
    xChar = (char) (rand()%(256*sizeof(xChar)));
    pChar = (char *) MALLOC(xSizeToMalloc * sizeof(pChar));
    if (pChar == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return;
    }
    memset (pChar, xChar, xSizeToMalloc * sizeof(pChar));

    xSizeToMalloc = (size_t) ((rand() % (MALLOC_SIZE_MAX-MALLOC_SIZE_MIN+1)) + MALLOC_SIZE_MIN);
    xInt = (long unsigned int) (rand()%(256*sizeof(xInt)));
    pInt = (long unsigned int *) MALLOC(xSizeToMalloc * sizeof(pInt));
    if (pInt == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return;
    }
    memset (pInt, xInt, xSizeToMalloc * sizeof(pInt));

    FREE(pChar);
    FREE(pInt);
    return;
}