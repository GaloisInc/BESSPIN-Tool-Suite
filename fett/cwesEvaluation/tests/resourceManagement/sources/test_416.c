#include "testsParameters.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))

#include "FreeRTOS.h"
#define MALLOC pvPortMalloc
#define FREE vPortFree

#elif (defined(testgenOnDebian))

#include <setjmp.h>
#include <signal.h>
#define MALLOC malloc
#define FREE free
static sigjmp_buf jbuf;

#else

#include <signal.h>
#define MALLOC malloc
#define FREE free

#endif

void
signal_callback_handler(int signum) {
    printf("\n<ERROR-SIGABRT> Caught signal - segfault occurred %d\n", signum);
#if (defined(testgenOnDebian))
    siglongjmp(jbuf, 1);
#elif(defined(testgenOnFreeBSD))
    exit(signum);
#endif
}

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
    printf("<POINTER_USED_IMPROPERLY> q=%c\n", *q);
    if(seg_guard == 1){
#if (defined(testgenOnDebian))
        if (sigsetjmp(jbuf, 1) == 0) {
            // segfault occurred
            FREE(p);
        } else {
            printf("\n<DOUBLE_FREE_OF_STACK>\n");
        }
#else
        FREE(p);
        printf("\n<DOUBLE_FREE_OF_STACK>\n");
#endif
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
int main(int argc, char **argv) {
    printf("\n<weakness_after_free>\n");
    weakness_after_free(0);
    printf("\n<weakness_after_double_free>\n");
    weakness_after_free(1);
    return 0;
}

#endif // end of if FreeRTOS