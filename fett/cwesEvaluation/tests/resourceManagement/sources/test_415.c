#include "testsParameters.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define EXIT_FAILURE 1

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))

#include "FreeRTOS.h"
#define MALLOC pvPortMalloc
#define FREE vPortFree

#else

#define MALLOC malloc
#define FREE free

#endif

typedef struct Str_Int {
    int value;
} Str_Int;


void
double_free( char * src) {
    char* ptr = (char*)MALLOC(4);
    strcpy(ptr, src);
    FREE(ptr);
    FREE(ptr);
    printf("\n<DOUBLE_FREE_OF_STACK>\n");

    return;
}

void
double_free_str_int(int in) {
    Str_Int *mew = MALLOC(sizeof(Str_Int));
    mew->value = in;
    FREE(mew);
    FREE(mew);
    printf("\n<DOUBLE_FREE_OF_STR_INT_ON_STACK>\n");

    return;
}

// ----------------- FreeRTOS Test ----------

#ifdef testgenOnFreeRTOS

#define NUM_OF_TEST_PARTS 2

void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: double_free.---\n");
        char src[4] = "Test";
        double_free(&src[0]);
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: double_free_str_int.---\n");
        double_free_str_int(5);
    #else
        printf("SCORE:415:%d:TEST ERROR\n", TESTGEN_TEST_PART);
    #endif
    return;
}

// ----------------- FreeBSD & Debian Test ------------

#elif (defined(testgenOnFreeBSD) || defined(testgenOnDebian))


int main(int argc, char *argv[]) {
    char src[4] = "Test";
    int option;
    if (argc > 1) { //be safe
        option = atoi(argv[1]);
    } else {
        option = -1;
    }
    switch(option) {
        case 1 :
            printf("\n<double_free>\n");
            double_free(&src[0]);
            break;
        case 2 :
            printf("\n<double_free_str_int>\n");
            double_free_str_int(5);
            break;
        default :
            printf("SCORE:415:%d:TEST ERROR\n",option);
            return 1;
    }  
    return 0;
}

#endif // end of if FreeRTOS
