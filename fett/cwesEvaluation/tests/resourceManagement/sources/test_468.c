#include "testsParameters.h"

#ifdef testgenOnFreeRTOS

#if (defined(testgenFPGA))
#include "FreeRTOS.h"
#endif
// ----------------- FreeRTOS Test ----------
#include <stdio.h>
#define NUM_OF_TEST_PARTS 2
#define EXIT_FAILURE 1

int example_good_scaled(int i) {
    int intArray[10] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
    int *intPointer = intArray;
    // GOOD: the offset is automatically scaled by sizeof(int).
    int p = *(intPointer + i);
    printf("\n<CORRECT_SCALED> p=%d\n", p);
    return p;
}

int example_bad_scaled(int i) {
    int intArray[10] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
    int *intPointer = intArray;
    int p= *(intPointer + (i * sizeof(int)));
    if (p <= 0) { // negative address
        printf("\n<WRONG_OFFSET> p=%d\n", p);
    } else {
        exit(EXIT_FAILURE);
    }
    return p;
}

void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: example_good_scaled.---\n");
        example_good_scaled(4);
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: example_bad_scaled.---\n");
        example_bad_scaled(4);
    #else
        printf("SCORE:468:%d:TEST ERROR\n",TESTGEN_TEST_PART);
    #endif
  //printf("<INVALID> This test is not implemented yet.\n");
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

#include <stdio.h>
#include <stdlib.h>

int example_bad_scaled(int i) {
  int intArray[10] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
  int *intPointer = intArray;
  // Usually programming mistake.
  // BAD: the offset is already automatically scaled by sizeof(int),
  // so this code will compute the wrong offset.
  int p= *(intPointer + (i * sizeof(int)));
  if (p != i+1) {
    printf("\n<WRONG_OFFSET> p=%d\n", p);
  } else {
    printf("\n<CORRECT_SCALED> p=%d\n", p);
  }
  return p;
}

int example_good_scaled(int i) {
  int intArray[10] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
  int *intPointer = intArray;
  // GOOD: the offset is automatically scaled by sizeof(int).
  int p = *(intPointer + i);
  if (p == i+1) {
    printf("\n<CORRECT_SCALED> p=%d\n", p);
  } else {
    printf("\n<WRONG_OFFSET> p=%d\n", p);
  }
  return p;
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
            printf("\n<example-good-scaled>\n");
            example_good_scaled(4);
            break;
        case 2 :
            printf("\n<example-bad-scaled>\n");
            example_bad_scaled(4);
            break;
        default :
            printf("SCORE:468:%d:TEST ERROR\n",option);
            return 1;
    }  
    return 0;
}

#endif // end of if FreeRTOS

