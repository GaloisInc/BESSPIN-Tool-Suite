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
#define NUM_OF_TEST_PARTS 2

void wrong_shift_address_assignment(void){
    int* x = MALLOC(sizeof(int) * 5);
    if (x == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return;
    }
    x += sizeof(int);
    FREE(x);
    printf("\n<RELEASE_OF_INVALID_POINTER_PASSED_SUCCESSFULLY>\n");
}

void wrong_address_assignment(void){
    int x;
    int *p = MALLOC(sizeof(*p));
    if (p == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return;
    }
    x = 12;
    p = &x; //assign the address of x to p
    FREE(p);
    printf("\n<RELEASE_OF_INVALID_POINTER_PASSED_SUCCESSFULLY>\n");
}
void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
#if TESTGEN_TEST_PART == 1
    printf("\n---Part01: wrong_shift_address_assignment.---\n");
        wrong_shift_address_assignment();
#elif TESTGEN_TEST_PART == 2
    printf("\n---Part02: wrong_address_assignment.---\n");
        wrong_address_assignment();
#else
    printf("SCORE:763:%d:TEST ERROR\n",TESTGEN_TEST_PART);
#endif

    return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

/**
  The free() has been provided a pointer to x
  in the middle of the allocated memory block.
  This means that, free has no idea where the block
  starts or ends, therefore throwing an error.
 **/
void wrong_shift_address_assignment(void){
    int* x = malloc(sizeof(int) * 5); // Allocate space for 5 ints
    x += sizeof(int);                       // Shift the allocated memory by 1 int
    free(x);
    printf("\n<RELEASE_OF_INVALID_POINTER_ERROR>\n");
}

void wrong_address_assignment(void){
    int x;
    int *p = malloc(sizeof(*p)); /* dynamic allocation of memory */
    x = 12;
    p = &x; //assign the address of x to p
    free(p); // p no longer points to dynamically allocated memory,
            // hence it is incorrect to call free() with it.
    printf("\n<RELEASE_OF_INVALID_POINTER_ERROR>\n");
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
            printf("\n<wrong_shift_address_assignment>\n");
            wrong_shift_address_assignment();
            break;
        case 2 :
            printf("\n<wrong_address_assignment>\n");
            wrong_address_assignment();
            break;
        default :
            printf("SCORE:763:%d:TEST ERROR\n",option);
            return 1;
    }  
    return 0;
}

#endif // end of if FreeRTOS

