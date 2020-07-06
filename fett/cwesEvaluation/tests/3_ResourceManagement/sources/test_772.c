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

#define  LOOPS    100
#define  MAXSIZE  256
#define  SIZE     32

void
leaked_block(char* str)
{
    char *s;
    s = (char *)MALLOC(SIZE);

    strcpy(s, str);
    printf("\n<LEAKED_BLOCK>\n");
    // no free of s. Once leaked_block returns, there is no
    // pointer pointing to the malloc'ed block,
    // so that block is leaked.
}

void
unrecoverable_allocation_block(void){
    int count = 0;
    char *pointer = NULL;

    for(count=0; count<LOOPS; count++) {
        pointer = (char *)MALLOC(sizeof(char) * MAXSIZE);
    }
    // In this example, we have 10 allocations of size MAXSIZE.
    // Every allocation, with the exception of the last, is lost.
    // If no pointer is pointed to the allocated block, it is
    // unrecoverable during program execution. A simple fix to this
    // trivial example is to place the free() call inside of the ‘for’ loop.

    FREE(pointer);
    printf("\n<EVERY_ALLOCATION_EXCEPT_THE_LAST_IS_LOST>\n");
}

#define NUM_OF_TEST_PARTS 2

void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
    char str[5]="Test";
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: leaked_block.---\n");
        leaked_block(&str[0]);
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: unrecoverable_allocation_block.---\n");
        unrecoverable_allocation_block();
    #else
        printf("SCORE:772:%d:TEST ERROR\n", TESTGEN_TEST_PART);
    #endif
    return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

#include <errno.h>
#include <sys/resource.h>
#include <fcntl.h>
#include <unistd.h>

// @design dragan The number of files at which the test will stop
// disregarding the limits.
// @note kiniry This artificial limit interacts with the user-limit
// set by the Python wrapper in `test_772.py`.  This number must be
// greater than the limit set in that script, but neither should be
// very large so as to help test performance.
#define MAX_NUM_OF_FILES 20 

//functions declarations
int main();
static void checkingFunctionA();
static void testingFunctionB();

int main() {
  printf("\n<Function A1>\n");
  checkingFunctionA();
  printf("\n<Function B>\n");
  testingFunctionB();
  printf("\n<Function A2>\n");
  checkingFunctionA();

  return 0;
}

//Function A: opens one file and closes it.
void checkingFunctionA(void) {
  printf("[A]: Opening one file...\n");
  int fd = open("check_file", O_RDWR | O_CREAT, 0666);
  if (fd<0) {
    printf("[A]: Failed to open a file! \n");
    if(errno == EMFILE) {
      printf("\n<DOS-ACHIEVED>\n");
    } else {
      printf("\n<INVALID> Unrecognized error. [errno=%d]\n",errno);
      return;
    }
  } else {
    printf("\n<FILE-OPENED>\n");
  }
  close(fd);
  return;
}

//Function B: keeps opening files until it is not able to anymore, then hangs.
void testingFunctionB(void) {
  int fd;
        
  //Keep opening files (until the higher limit)
  for(int i = 0; i<MAX_NUM_OF_FILES; i++) {
    printf("[B]: Opening file #%d ...\n",i);
    fd = open("test_file", O_RDWR | O_CREAT, 0666);
    if (fd<0) { //failed
      printf("[B]: Failed to open the file! \n");
      if(errno == EMFILE) {
        printf("\n<LIMIT-REACHED>\n");
      } else {
        printf("\n<INVALID> Unrecognized error. [errno=%d]\n",errno);
      }
      break;
    }
  }

  if (fd >= 0) {
    printf("\n<INVALID> The limit was not reached.\n");
  }

  return;
}

#endif // end of if FreeRTOS
