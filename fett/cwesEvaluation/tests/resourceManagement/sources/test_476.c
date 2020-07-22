#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef testgenOnFreeRTOS

#if (defined(testgenFPGA))
#include "FreeRTOS.h"
#endif
// ----------------- FreeRTOS Test ----------
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
        printf("SCORE:476:%d:TEST ERROR\n",TESTGEN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

#include <signal.h>
#include <setjmp.h>

static sigjmp_buf jbuf;

static void catch_segv(int signum)
{
    // Roll back to the checkpoint set by sigsetjmp().
    printf("\n<ERROR-SEGFAULT> Caught signal - segfault occurred %d\n",signum);
    siglongjmp(jbuf, 1);
}

void regular_test(int const *ptr) {
  int x = 5;
  ptr = &x;
  printf("\n<REGULAR> dereference pointer: %d\n", *ptr);
}

void malicious_test_read(int const *ptr) {
  printf("\n malicious_test_read:Null pointer dereference exception "
         "trying to read it \n");
    if (sigsetjmp(jbuf, 1) == 0) {
        int y = *ptr; //CRASH
    } else {
        printf("\n<DEREFERENCE-VIOLATION> Exception bad access."
               "handled in false branch.\n");
    }
    printf("\n After the exception handling "
           "the program continues its execution.\n");

}

void malicious_test_write(int *ptr) {
  printf("\n malicious_test_write:Null pointer dereference exception "
         "trying to write it \n");
    if (sigsetjmp(jbuf, 1) == 0) {
        *ptr = 5; //CRASH
    } else {
        printf("\n<DEREFERENCE-VIOLATION> Exception bad access."
               "handled in false branch.\n");
    }
    printf("\n After the exception handling "
           "the program continues its execution.\n");
}

int main(int argc, char *argv[]) {
  signal(SIGSEGV, catch_segv);
  int *ptr;
  printf("\n<Regular test>\n");
  regular_test(ptr);
  int *ptr1=NULL;
  printf("\n<Malicious test read>\n");
  malicious_test_read(ptr1);
  printf("\n<Malicious test write>\n");
  malicious_test_write(ptr1);
}

#endif // end of if FreeRTOS

