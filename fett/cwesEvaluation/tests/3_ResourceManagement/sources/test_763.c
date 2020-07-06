#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
#define MALLOC malloc
#define FREE free
#endif
#ifdef testgenOnFreeRTOS
// ----------------- FreeRTOS Test ----------
#define NUM_OF_TEST_PARTS 2

void wrong_shift_address_assignment(void){
    int* x = MALLOC(sizeof(int) * 5);
    x += sizeof(int);
    FREE(x);
    printf("\n<RELEASE_OF_INVALID_POINTER_PASSED_SUCCESSFULLY>\n");
}

void wrong_address_assignment(void){
    int x;
    int *p = MALLOC(sizeof(*p));
    x = 12;
    p = &x; //assign the address of x to p
    FREE(p);
    printf("\n<RELEASE_OF_INVALID_POINTER_PASSED_SUCCESSFULLY>\n");
}
void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
#if TESTGEN_TEST_PART == 1
    printf("\n---Part01: wrong_shift_address_assignment.---\n");
        wrong_shift_address_assignment();
#elif TESTGEN_TEST_PART == 2
    printf("\n---Part02: wrong_address_assignment.---\n");
        wrong_address_assignment();
#else
    printf("SCORE:763:%d:TEST ERROR\n",TESTGEN_TEST_PART);
#endif

    return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

#include <signal.h>
#include <setjmp.h>

static sigjmp_buf jbuf;

void
signal_callback_handler(int signum) {
    printf("\n<ERROR-SIGABRT> Caught signal - segfault occurred %d\n", signum);
    siglongjmp(jbuf, 1);
}

/**
  The free() has been provided a pointer to x
  in the middle of the allocated memory block.
  This means that, free has no idea where the block
  starts or ends, therefore throwing an error.
 **/
void wrong_shift_address_assignment(void){
    int* x = malloc(sizeof(int) * 5); // Allocate space for 5 ints
    x += sizeof(int);                       // Shift the allocated memory by 1 int
    if (sigsetjmp(jbuf, 1) == 0) {
        free(x);
    }else {
        printf("\n<RELEASE_OF_INVALID_POINTER_ERROR>\n");
    }
}

void wrong_address_assignment(void){
    int x;
    int *p = malloc(sizeof(*p)); /* dynamic allocation of memory */
    x = 12;
    p = &x; //assign the address of x to p
    if (sigsetjmp(jbuf, 1) == 0) {
        free(p); // p no longer points to dynamically allocated memory,
                 // hence it is incorrect to call free() with it.
    }else {
        printf("\n<RELEASE_OF_INVALID_POINTER_ERROR>\n");
    }
}
int main() {
    signal(SIGABRT, signal_callback_handler);
    printf("\n<wrong_shift_address_assignment>\n");
    wrong_shift_address_assignment();
    printf("\n<wrong_address_assignment>\n");
    wrong_address_assignment();
    return 0;
}
#endif // end of if FreeRTOS

