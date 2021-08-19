#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SUCCESS (1)
#define FAILURE (0)

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

// ----------------- FreeRTOS Test ----------

#define NUM_OF_TEST_PARTS 2

int contains_char(char c) {
    char *str;
    str = (char*)MALLOC(20*sizeof(char));
    if (str == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return FAILURE;
    }
    strcpy(str, "Search!");
    while (*str != 0) {
        if (*str == c) {
            FREE(str);
            printf("\n<MATCHED_CHAR> free string and return success\n");
            return SUCCESS;
        }
        str = str + 1;
    }
    FREE(str); //CRASH
    printf("\n<DEREFERENCE-VIOLATION>\n");
    return FAILURE;
}


#ifdef BESSPIN_FREERTOS

void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if BESSPIN_TEST_PART == 1
        printf("\n---Part01: contains_char_success.---\n");
        contains_char('S');
        printf("\nResult is %d\n",contains_char('S'));
    #elif BESSPIN_TEST_PART == 2
        printf("\n---Part02: contains_char_failure.---\n");
        printf("\nResult is %d\n",contains_char('T'));
    #else
        printf("SCORE:761:%d:TEST ERROR\n",BESSPIN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(BESSPIN_DEBIAN) || defined(BESSPIN_FREEBSD))
#include "unbufferStdout.h"

int main(int argc, char *argv[]) {
    unbufferStdout();
    int option;
    if (argc > 1) { //be safe
        option = atoi(argv[1]);
    } else {
        option = -1;
    }
    switch(option) {
        case 1 :
            printf("\n<contains_char_success> Result is %d\n",contains_char('S'));
            break;
        case 2 :
            printf("\n<contains_char_failure> Result is %d\n",contains_char('T'));
            break;
        default :
            printf("SCORE:761:%d:TEST ERROR\n",option);
            return 1;
    }  
    return 0;
}

#endif // end of if FreeRTOS
