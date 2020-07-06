#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

#define MAX_SIZE 100
int a[MAX_SIZE]; //Global var
#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
#define MALLOC malloc
#define FREE free
#endif

void
correct_memory_free(void){
    int *b = (int*)malloc(MAX_SIZE*sizeof(int));
    free(b);
    
    printf("\n<MEMORY_FREE_CORRECTLY>\n");
}
#ifdef testgenOnFreeRTOS

// ----------------- FreeRTOS Test ----------
#define NUM_OF_TEST_PARTS 3

void
array_allocated_globally(void){
    FREE(a); //array is allocated globally, as part of the data segment of memory
    //and the programmer attempts to call free() on the array.
    printf("\n<INVALID_FREE_OF_MEMORY>\n");
}

void
wrong_memory_free(void){
    int b[MAX_SIZE];
    FREE(b); //array is allocated automatically on the stack as a local variable
    //and the programmer attempts to call free() on the array.
    printf("\n<INVALID_FREE_OF_STACK>\n");

}

void main() {
  printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: correct_memory_free.---\n");
        correct_memory_free();
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: wrong_memory_free.---\n");
        wrong_memory_free();
    #elif TESTGEN_TEST_PART == 3
        printf("\n---Part03: array_allocated_globally.---\n");
        array_allocated_globally();
    #else
        printf("SCORE:762:%d:TEST ERROR\n",TESTGEN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

#include <setjmp.h>

static sigjmp_buf jbuf;

void
signal_callback_handler(int signum) {
    printf("\n<ERROR-SIGABRT> Caught signal - segfault occurred %d\n", signum);
    siglongjmp(jbuf, 1);
}

void
array_allocated_globally(void){
    if (sigsetjmp(jbuf, 1) == 0) {
        free(a); //array is allocated globally, as part of the data segment of memory
        //and the programmer attempts to call free() on the array.
    }else {
        printf("\n<INVALID_FREE_OF_MEMORY>\n");
    }
}

void
wrong_memory_free(void){
    int b[MAX_SIZE];
    if (sigsetjmp(jbuf, 1) == 0) {
        free(b); //array is allocated automatically on the stack as a local variable
        //and the programmer attempts to call free() on the array.
    }else {
        printf("\n<INVALID_FREE_OF_STACK>\n");
    }
}

int main() {
    signal(SIGABRT, signal_callback_handler);
    printf("\n<correct_memory_free>\n");
    correct_memory_free();
    printf("\n<wrong_memory_free>\n");
    wrong_memory_free();
    printf("\n<array_allocated_globally>\n");
    array_allocated_globally();
    return 0;
}

#endif // end of if FreeRTOS

