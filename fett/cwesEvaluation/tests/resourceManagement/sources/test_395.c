// @author Dragan Stosic <dragan@freeandfair.us>
// @reviewer Joe Kiniry <kiniry@galois.com>

// The test_395.c contains two malicious tests with read/write from/to
// null pointer dereference.
//
// The Null pointer dereference usually raises a EXC_BAD_ACCESS
// (code=1 address=0x0) exception.  The address code 0x0
// suggests a NULL pointer deference.  The C language does not provide
// direct support for error handling, also known as exception
// handling, such as try/catch clause.  In order to simulate CWE 395,
// we have provided try/catch clause using sigsetjmp() and
// siglongjmp().
//
// Notice that: Resolving a NULL pointer exception by using the
// try/catch clause is NOT RECOMMENDED!  Fixing the underlying problem
// is the proper way of handling a NULL pointer issue.
//
// The exception handling mechanism in the below code is as follows:
//
// 1) Set up a signal handler. Register a SIGSEGV signal handler.
//
//    We register signal handler in the main method, so when a SIGSEGV
//    signal raised, the handler function catch_segv() will be
//    invoked.
//
// 2) Set up a check point.
//
//    After the signal handler has finished processing the exception
//    it needs to let the program continue its execution from the
//    particular checkpoint. This checkpoint is achieved via
//    sigsetjmp(jbuf, 1) saving the context/environment in jbuf for
//    latter use by siglongjmp().  It returns 0 when the checkpoint is
//    set up, so the program will then take the true branch of the if
//    guard in the malicious test.
//
// 3) Triggering the exception
//
//    The null pointer dereference in the malicious tests (see
//    CRASH) will trigger a SIGSEGV signal. The exception will be
//    captured by the program because it has registered an exception
//    handler in the main method.

// 4) Roll back to the checkpoint.
//
//    Inside the exception handler catch_segv(), the function
//    siglongjmp(jbuf, 1) is called and the state saved in the jbuf
//    variable is copied back to the processor and computation starts
//    over from the return point of the sigsetjmp() function, but the
//    returned value of the sigsetjmp() function is the second
//    argument of the siglongjmp() function, which is 1. After the
//    exception handling the program continues its execution from the
//    else branch, i.e. false branch of the if guard in the malicious
//    test.
//
// We recognize that some teams will not support the setlongjmp()
// family of functions in program phase 2.

#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>

#ifdef testgenOnFreeRTOS

#if (defined(testgenFPGA))
#include "FreeRTOS.h"
#endif
// ----------------- FreeRTOS Test ----------

#include <string.h>

#define NUM_OF_TEST_PARTS 2

void malicious_test_read(int const *ptr) {
    int y = *ptr; //CRASH
    printf("\n<DEREFERENCE-VIOLATION_PASSED_SUCCESSFULLY>\n");
}

void malicious_test_write(int *ptr) {
    *ptr = 5; //CRASH
    printf("\n<DEREFERENCE-VIOLATION_PASSED_SUCCESSFULLY>\n");
}
void main() {
    int *p=NULL;
    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: malicious_test_read.---\n");
        malicious_test_read(p);
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: malicious_test_write.---\n");
        malicious_test_write(p);
    #else
        printf("SCORE:395:%d:TEST ERROR\n",TESTGEN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

#include <stdlib.h>

void test_read(int const *ptr) {
  int y = *ptr; //CRASH

  printf("\n<DEREFERENCE-VIOLATION>\n"); 
}

void test_write(int *ptr) {
  *ptr = 5; //CRASH

  printf("\n<DEREFERENCE-VIOLATION>\n");
}

int main(int argc, char *argv[]) {
    int *ptr1=NULL;
    int option;
    if (argc > 1) { //be safe
        option = atoi(argv[1]);
    } else {
        option = -1;
    }
    switch(option) {
      case 1 :
            printf("\n<read>\n");
            test_read(ptr1);
            break;
        case 2 :
            printf("\n<write>\n");
            test_write(ptr1);
        default :
            printf("SCORE:395:%d:TEST ERROR\n",argc);
            return 1;
    }  
    return 0;
}

#endif // end of if FreeRTOS
