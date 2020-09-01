#include "testsParameters.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))

#include "FreeRTOS.h"
#define MALLOC pvPortMalloc
#define FREE vPortFree

#else

#include <signal.h>
#define MALLOC malloc
#define FREE free

#endif

void
weakness_after_free(int seg_guard){
    char* p = (char*)MALLOC(10 * sizeof(char));
    // pointer to the same block of memory
    int* q = (int*)p;
    *p = 'A';
    // Everything's ok so far
    printf("TEST:  p=%c q=%d\n", *p, *q);
    // free() p allocated memory
    FREE(p);
    // q now points to de-allocated memory
    printf("q=%c\n", *q);
    printf("<POINTER_USED_IMPROPERLY>\n");
    if(seg_guard == 1){
        FREE(p);
        printf("\n<DOUBLE_FREE_OF_STACK>\n");
    }
}

// ----------------- FreeRTOS Test ----------

#ifdef testgenOnFreeRTOS

#define NUM_OF_TEST_PARTS 2
void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: weakness_after_free.---\n");
        weakness_after_free(0);
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: weakness_after_double_free.---\n");
        weakness_after_free(1);
    #else
        printf("SCORE:416:%d:TEST ERROR\n", TESTGEN_TEST_PART);
    #endif
    return;
}

#elif (defined(testgenOnFreeBSD) || defined(testgenOnDebian))
int main(int argc, char *argv[]) {
    int option;
    if (argc > 1) { //be safe
        option = atoi(argv[1]);
    } else {
        option = -1;
    }
    switch(option) {
        case 1 :
            printf("\n<weakness_after_free>\n");
            weakness_after_free(0);
            break;
        case 2 :
            printf("\n<weakness_after_double_free>\n");
            weakness_after_free(1);
            break;
        default :
            printf("SCORE:416:%d:TEST ERROR\n",option);
            return 1;
    }  
    return 0;
}

#endif // end of if FreeRTOS