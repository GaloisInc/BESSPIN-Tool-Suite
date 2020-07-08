#include "testsParameters.h"

#include <stdio.h>
#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
#endif
#ifdef testgenOnFreeRTOS

// ----------------- FreeRTOS Test ----------

#define NUM_OF_TEST_PARTS 2

struct testStruct {
    int a;
};

struct testStruct *f;
int *p;
void *vp;


void struct_pointer_cast_of_scalar_pointer() {
    f = (struct foo *)p; /* struct pointer cast of scalar pointer error */
    printf ("\na= %d\n", f->a);
    printf ("\n<CAST_PASSED_SUCCESSFULLY>\n"); // should not reach this line
}

void struct_pointer_cast_of_void_pointer() {
    f = (struct foo *)vp; /* struct pointer cast of void pointer error */
    printf ("\na= %d\n", f->a);
    printf ("\n<CAST_PASSED_SUCCESSFULLY>\n"); // should not reach this line
}


void main() {

    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: struct_pointer_cast_of_scalar_pointer.---\n");
        struct_pointer_cast_of_scalar_pointer();
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: struct_pointer_cast_of_void_pointer.---\n");
        struct_pointer_cast_of_void_pointer();
    #else
        printf("SCORE:588:%d:TEST ERROR\n",TESTGEN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

#include <setjmp.h>
#include <signal.h>
static sigjmp_buf jbuf;

static void catch_segv(int signum)
{
    // Roll back to the checkpoint set by sigsetjmp().
    printf("\n<ERROR-SEGFAULT> Caught signal - segfault occurred %d\n",signum);
    siglongjmp(jbuf, 1);
}
struct testStruct {
    int a;
};

struct testStruct *f;
int *p;
void *vp;

void struct_pointer_cast_of_scalar_pointer(void) {
    f = (struct foo *)p; /* struct pointer cast of scalar pointer error */
    if (sigsetjmp(jbuf, 1) == 0) {
        printf ("a= %d\n", f->a);
    } else {
        printf("\n<DEREFERENCE-VIOLATION> Exception bad access."
               "handled in false branch.\n");
    }
    printf("\n After the exception handling "
           "the program continues its execution.\n");
}

void struct_pointer_cast_of_void_pointer(void) {
    f = (struct foo *)vp; /* struct pointer cast of void pointer error */
    if (sigsetjmp(jbuf, 1) == 0) {
        printf ("a= %d\n", f->a);
    } else {
        printf("\n<DEREFERENCE-VIOLATION> Exception bad access."
               "handled in false branch.\n");
    }
    printf("\n After the exception handling "
           "the program continues its execution.\n");
}

int main() {
    // Register a signal handler
    signal(SIGSEGV, catch_segv);
    printf("\n<struct_pointer_cast_of_scalar_pointer>\n");
    struct_pointer_cast_of_scalar_pointer();
    printf("\n<struct_pointer_cast_of_void_pointer>\n");
    struct_pointer_cast_of_void_pointer();
    return 0;
}

#endif // end of if FreeRTOS
