#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SUCCESS (1)
#define FAILURE (0)

#ifdef testgenOnFreeRTOS

#if (defined(testgenFPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

// ----------------- FreeRTOS Test ----------

#define NUM_OF_TEST_PARTS 4

int contains_char_malicious(char c) {
    char *str;
    str = (char*)MALLOC(20*sizeof(char));
    if (str == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return FAILURE;
    }
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
    if (str == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return FAILURE;
    }
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

int contains_char_valid(char c) {
    char *str;
    int i = 0;
    str = (char*)malloc(20*sizeof(char));
    if (str == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return FAILURE;
    }
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
    if (str == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return FAILURE;
    }
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
    free(str); //CRASH
    printf("\n<DEREFERENCE-VIOLATION>\n");

    return FAILURE;
}

int main(int argc, char *argv[]) {
    int option;
    if (argc > 1) { //be safe
        option = atoi(argv[1]);
    } else {
        option = -1;
    }
    switch(option) {
        case 1 :
            printf("\n<contains_char_valid_success> Result is %d\n",contains_char_valid('S'));
            break;
        case 2 :
            printf("\n<contains_char_valid_failure>Result is %d\n",contains_char_valid('T'));
            break;
        case 3 :
            printf("\n<contains_char_malicious_success> Result is %d\n",contains_char_malicious('S'));
            break;
        case 4 :
            printf("\n<contains_char_malicious_failure> Result is %d\n",contains_char_malicious('G'));
            break;
        default :
            printf("SCORE:761:%d:TEST ERROR\n",option);
            return 1;
    }  
    return 0;
}

#endif // end of if FreeRTOS
