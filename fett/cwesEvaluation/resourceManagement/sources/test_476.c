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

void regular_test(int const *ptr) {
  int x = 5;
  ptr = &x;
  printf("\n<REGULAR> dereference pointer: %d\n", *ptr);
}

void malicious_test_read(int const *ptr) {
  printf("\n malicious_test_read:Null pointer dereference exception "
         "trying to read it \n");
    int y = *ptr; //CRASH
    printf("\n<DEREFERENCE-VIOLATION>\n");

}

void malicious_test_write(int *ptr) {
  printf("\n malicious_test_write:Null pointer dereference exception "
         "trying to write it \n");
    *ptr = 5; //CRASH
    printf("\n<DEREFERENCE-VIOLATION>\n");
}

int main(int argc, char *argv[]) {
  int option;
  int *ptr;
  int *ptr1=NULL;
  if (argc > 1) { //be safe
      option = atoi(argv[1]);
  } else {
      option = -1;
  }
  switch(option) {
      case 1 :
          printf("\n<Regular test>\n");
          regular_test(ptr);
          break;
      case 2 :
          printf("\n<Malicious test read>\n");
          malicious_test_read(ptr1);
          break;
      case 3 :
          printf("\n<Malicious test write>\n");
          malicious_test_write(ptr1);
          break;
      default :
          printf("SCORE:476:%d:TEST ERROR\n",option);
          return 1;
  }  
  return 0;
  
  
  
}

#endif // end of if FreeRTOS

