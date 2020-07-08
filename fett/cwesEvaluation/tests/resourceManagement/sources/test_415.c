#include "testsParameters.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define EXIT_FAILURE 1

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

typedef struct Str_Int {
    int value;
} Str_Int;


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
double_free( char * src) {
    char* ptr = (char*)MALLOC(4);
    strcpy(ptr, src);
    FREE(ptr);
#if (defined(testgenOnDebian))
    if (sigsetjmp(jbuf, 1) == 0) {
        FREE(ptr);
    } else {
        printf("\n<DOUBLE_FREE_OF_STACK>\n");
    }
#else
    FREE(ptr);
    printf("\n<DOUBLE_FREE_OF_STACK>\n");
#endif
    return;
}

void
double_free_str_int(int in) {
    Str_Int *mew = MALLOC(sizeof(Str_Int));
    mew->value = in;
    FREE(mew);
#if (defined(testgenOnDebian))
    if (sigsetjmp(jbuf, 1) == 0) {
        FREE(mew);
    } else {
        printf("\n<DOUBLE_FREE_OF_STR_INT_ON_STACK>\n");
    }
#else
    FREE(mew);
    printf("\n<DOUBLE_FREE_OF_STR_INT_ON_STACK>\n");
#endif
    return;
}

// ----------------- FreeRTOS Test ----------

#ifdef testgenOnFreeRTOS

#define NUM_OF_TEST_PARTS 2

void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: double_free.---\n");
        char src[4] = "Test";
        double_free(&src[0]);
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: double_free_str_int.---\n");
        double_free_str_int(5);
    #else
        printf("SCORE:415:%d:TEST ERROR\n", TESTGEN_TEST_PART);
    #endif
    return;
}

// ----------------- FreeBSD & Debian Test ------------

#elif (defined(testgenOnFreeBSD) || defined(testgenOnDebian))

int main()
{
    signal(SIGABRT, signal_callback_handler);
    char src[4] = "Test";
    printf("\n<double_free>\n");
    double_free(&src[0]);
    printf("\n<double_free_str_int>\n");
    double_free_str_int(5);
    return 0;
}

#endif // end of if FreeRTOS
