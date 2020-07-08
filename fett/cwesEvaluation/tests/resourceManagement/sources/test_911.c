#include "testsParameters.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))

#include "FreeRTOS.h"
#define MALLOC pvPortMalloc
#define FREE vPortFree

#else

#include <signal.h>
#define MALLOC malloc
#define FREE free
#endif
int CHUNK_SIZE=4096;
int n = 10;

struct node {struct node* next; int data; };
union unode {struct node* next; int data; };

void
correct_implicit_reference_count(){
    struct node *ptrA, *ptrB;
    ptrA = MALLOC(sizeof(struct node)); //objA RCobjA=1
    ptrB = MALLOC(sizeof(struct node)); //objA RCobjB=1
    ptrB->next = ptrA; //objA RCobjA=2
    FREE(ptrA); //objA RCobjA=2
    ptrA = MALLOC(sizeof(struct node)); //objA RCobjA=1
    printf("\n<REFERENCE_COUNTER_DECREASED_BY_ONE_FIRST_TIME>\n");
    FREE(ptrB); //objA RCobjA=0
    printf("\n<REFERENCE_COUNTER_DECREASED_BY_ONE_SECOND_TIME>\n");
}

void
unknown_implicit_reference_count(){
    char* chunk = malloc(CHUNK_SIZE);

    struct node* ptrA=MALLOC(sizeof(struct node)); //objA RCobjA=1

    // objB is not created directly from malloc, but instead a large chunk
    // of memory is located first and objB is created by setting pointer in the space
    // of the chunk. Notice that chunk is of type char.
    struct node* ptrB= (struct node*)&chunk[n*sizeof(struct node)];//objB

    // objC is of type union so the next pointer and data share the same
    // memory location.
    union unode* ptrC=MALLOC(sizeof(union unode));//objC

    ptrB->next = ptrC->next = ptrA; //objA RCobjA=3
    //object's B next pointer and object's C next pointer and pointer A
    // points to object A so the reference count is 3

    FREE(ptrA); // RCobjA = 3
    // object A is freed but the reference counter is still 3

    ptrA = NULL; // RCobjA = 2
    // pointer A is set to NULL so reference counter is decreased to 2
    printf("\n<REFERENCE_COUNTER_DECREASED_BY_ONE>\n");

    FREE(chunk);
    // chunk is freed; however chunk's type is only character array
    // so we don't know if any pointer is included in the chunk.
    printf("\n<UNKNOWN_REFERENCE_COUNTER_AFTER_CHUNK_FREE>\n");

    ptrC -> data = 1;
    // pointer C data is set to 1 and because it's a union type
    // pointer next is destroyed. From our prospective we need
    // to decrease reference count, but from the compiler's view
    // point it is just the store of the integer type, so additional
    // analysis is needed.
    printf("\n<UNKNOWN_REFERENCE_COUNTER_AFTER_UNION_DATA_SET_TO_ONE>\n");
    return;
}

// ----------------- FreeRTOS Test ----------

#ifdef testgenOnFreeRTOS

#define NUM_OF_TEST_PARTS 2
void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: correct_implicit_reference_count.---\n");
        correct_implicit_reference_count();
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: unknown_implicit_reference_count.---\n");
        unknown_implicit_reference_count();
    #else
        printf("SCORE:911:%d:TEST ERROR\n", TESTGEN_TEST_PART);
    #endif
    return;
}

#elif (defined(testgenOnFreeBSD) || defined(testgenOnDebian))
int main(int argc, char **argv) {
    printf("\n<correct_implicit_reference_count>\n");
    correct_implicit_reference_count();
    printf("\n<unknown_reference_count>\n");
    unknown_implicit_reference_count();
    return 0;
}

#endif // end of if FreeRTOS