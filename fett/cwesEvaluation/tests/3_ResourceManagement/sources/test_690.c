#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define EXIT_FAILURE 1

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif


typedef struct SubString {
    char *str;
    unsigned int  len;
} SubStr;

static SubStr *
SubStr_new(char* s, unsigned int l, int i)
{
    if (i==0) {
        SubStr *r; // create NULL pointer
        return r;
    } else {
        #if(defined(testgenOnFreeRTOS) && defined(testgenFPGA))
            SubStr *r = MALLOC(sizeof(SubStr));
        #else
            SubStr *r = malloc(sizeof(SubStr));
        #endif
        if (r != NULL) {
            printf("Memory allocation succeeded.\n");
            r->str = s;
            r->len = l;
        } else {
            printf("Memory allocation failed.\n");
            exit(EXIT_FAILURE);
        }
        return r;
    }
}

void test_malicious(char *str, char *dest) {
    SubStr *r= SubStr_new(str, 4, 0);
    strcpy(dest,r->str); //CRASH
    printf("\n<DEREFERENCE_VIOLATION_PASSED_SUCCESSFULLY>\n");
}

void test_regular(char *str, char *dest) {
    SubStr *r= SubStr_new(str, 4, 1);
    if (r != NULL) {
        strcpy(dest, r->str); // REGULAR
        printf("\n<REGULAR_PASSED> Copied string: %s\n", dest);
        FREE(r);
    } else {
        printf("Error! NUll pointer.");
        exit(EXIT_FAILURE);
    }
}
#ifdef testgenOnFreeRTOS

// ----------------- FreeRTOS Test ----------
#define NUM_OF_TEST_PARTS 2

void main() {
    char dest[5];
    char test_str [] = "test";
    char *str = &test_str[0];
    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: test_regular.---\n");
        test_regular(str, dest);
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: test_malicious.---\n");
        test_malicious(str, dest);
    #else
        printf("SCORE:690:%d:TEST ERROR\n",TESTGEN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

#include <signal.h>
void
signal_callback_handler(int signum) {
  printf("\n<ERROR-SEGFAULT> Caught signal - segfault occurred %d\n", signum);
  exit(signum);
}

int main(int argc, char *argv[]) {
  // Register signal and signal handler
  signal(SIGSEGV, signal_callback_handler);
  char dest[5];
  char test_str [] = "test";
  char *str = &test_str[0];
  printf("\n<test regular>\n");
  test_regular(str, dest);
  printf("\n<test malicious>\n");
  test_malicious(str, dest);
}

#endif // end of if FreeRTOS
