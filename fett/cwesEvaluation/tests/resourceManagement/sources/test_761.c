#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SUCCESS (1)
#define FAILURE (0)

#ifdef testgenOnFreeRTOS

#if (defined(testgenFPGA))
#include "FreeRTOS.h"
#endif

// ----------------- FreeRTOS Test ----------
#define MALLOC(size) pvPortMalloc(size)
#define FREE(ptr)   vPortFree(ptr)
#define NUM_OF_TEST_PARTS 4

int contains_char_malicious(char c) {
    char *str;
    str = (char*)MALLOC(20*sizeof(char));
    strcpy(str, "Search!");
    while (*str != NULL) {
        if (*str == c) {
            FREE(str);
            printf("\n<MATCHED_CHAR> free string and return success\n");
            return SUCCESS;
        }
        str = str + 1;
    }
    if (*str != NULL) {
    FREE(str); //CRASH
    printf("\n<DEREFERENCE_VIOLATION_PASSED_SUCCESSFULLY>\n");
    }else {
        printf("\n<DEREFERENCE_VIOLATION_PASSED_SUCCESSFULLY>\n");
    }
    return FAILURE;
}

int contains_char_valid(char c) {
    char *str;
    int i = 0;
    str = (char*)MALLOC(20*sizeof(char));
    strcpy(str, "Search!");
    while (i < strlen(str)) {
        if (str[i] == c) {
            FREE(str);
            printf("\n<MATCHED_CHAR> free string and return success\n");
            return SUCCESS;
        }
        i = i + 1;
    }
    FREE(str);
    printf("\n<VALID_RETURN_FAILURE> free string and return success\n");
    return FAILURE;
}

void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: contains_char_valid_success.---\n");
        contains_char_valid('S');
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: contains_char_valid_failure.---\n");
        contains_char_valid('T');
    #elif TESTGEN_TEST_PART == 3
        printf("\n---Part03: contains_char_malicious_success.---\n");
        contains_char_malicious('S');
    #elif TESTGEN_TEST_PART == 4
        printf("\n---Part04: contains_char_malicious_success.---\n");
        contains_char_malicious('G');
    #else
        printf("SCORE:761:%d:TEST ERROR\n",TESTGEN_TEST_PART);
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
    signal (signum, SIG_DFL);
    printf("\n<ERROR-SEGFAULT> Caught signal - segfault occurred %d\n",signum);
    siglongjmp(jbuf, 1);
}

int contains_char_valid(char c) {
    char *str;
    int i = 0;
    str = (char*)malloc(20*sizeof(char));
    strcpy(str, "Search!");
    while (i < strlen(str)) {
        if (str[i] == c) {
            // matched char, free string and return success
            free(str);
            printf("\n<MATCHED_CHAR> free string and return success\n");
            return SUCCESS;
        }
        // didn't match yet, increment pointer and try next char.
        i = i + 1;
    }
    // we did not match the char in the string, free mem and return failure.
    free(str);
    printf("\n<VALID_RETURN_FAILURE> free string and return success\n");
    return FAILURE;
}

int contains_char_malicious(char c) {
    char *str;
    str = (char*)malloc(20*sizeof(char));
    strcpy(str, "Search!");
    while (*str != NULL) {
        if (*str == c) {
            // matched char, free string and return success.
            free(str);
            printf("\n<MATCHED_CHAR> free string and return success\n");
            return SUCCESS;
        }
        // didn't match yet, increment pointer and try next char.
        str = str + 1;
    }
    // we did not match the char in the string, free mem and return failure.
    if (sigsetjmp(jbuf, 1) == 0) {
        signal(SIGABRT, &catch_segv);
        free(str); //CRASH
        signal (SIGABRT, SIG_DFL);
    } else {
        printf("\n<DEREFERENCE-VIOLATION> Exception bad access."
               "handled in false branch.\n");
    }
    printf("\n After the exception handling "
           "the program continues its execution.\n");
    return FAILURE;
}

int main(int argc, char *argv[]) {
    // Register signal and signal handler
    signal(SIGABRT, catch_segv);
    printf("\n<contains_char_valid_success> Result is %d\n",contains_char_valid('S'));
    printf("\n<contains_char_valid_failure>Result is %d\n",contains_char_valid('T'));
    printf("\n<contains_char_malicious_success> Result is %d\n",contains_char_malicious('S'));
    printf("\n<contains_char_malicious_failure> Result is %d\n",contains_char_malicious('G'));
}

#endif // end of if FreeRTOS
