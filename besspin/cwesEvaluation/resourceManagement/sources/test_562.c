#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA))
#include "FreeRTOS.h"
#define MALLOC pvPortMalloc
#define FREE vPortFree
#else
#define MALLOC malloc
#define FREE free
#endif

/** Address of stack memory associated with local variable 'a' returned */
int*
fill_array(int n) {
  int a[n];
  for (int i = 0; i < n; i++) {
    a[i] = i;
  }
  // Have to store as a local pointer `p` and return `p` because the compiler
  // will transform `return a` to `return NULL`, even with optimizations
  // disabled.  This is a legal transformation after all since `return a` is
  // undefined behavior.
  int *p = a;
  return p;
}

int*
fill_array_with_malloc(int n)
{
  int *a = MALLOC(n * sizeof(int));

  if (NULL == a) {
      printf("ERROR: Out of memory\n");
      return 0;
  }

  for (int i = 0; i < n; i++) {
    a[i] = i;
  }
  return a;
}

// Allocate array on the stack in a function call.
void
stack_test(int n) {
  printf("\n<BEGIN_STACK_TEST>\n");
  int *tab = fill_array(n);
  if (!tab) {
    // Compiler replaced fill_array return with `return NULL`.
    printf("\n<INVALID>\n");
    exit(1);
  }
  for (int i = 0; i < n; i++) {
    printf("%d ", tab[i]); // prints the array
  }
  printf("\n<DEREFERENCE_VIOLATION>\n");
}

// Allocate array on the heap.  Should experience no errors.
void
heap_test(int n) {
  int *tab = fill_array_with_malloc(n);
  int k = 0;
  for (int i = 0; i < n; i++) {
    printf("%d ", tab[i]); // prints the array
    if (tab[i] == i) {
      k = k + 1;
    }
  }
  FREE(tab);
  if (k == n) {
    printf("\n<VALID_ARRAY_CONTENT>\n");
  } else {
    printf("\n<NOT_VALID_ARRAY_CONTENT>\n");
  }
}

// ----------------- FreeRTOS Test ----------
#ifdef BESSPIN_FREERTOS

#define NUM_OF_TEST_PARTS 2

void main() {
  int *b;
  int *c;
  printf("\n<OSIMAGE=FreeRTOS>\n");
#if BESSPIN_TEST_PART == 1
  printf("\n---Part01: fill_array.---\n");
  stack_test(5);
#elif BESSPIN_TEST_PART == 2
  printf("\n---Part02: fill_array_with_malloc.---\n");
  heap_test(5);
#else
  printf("SCORE:562:%d:TEST ERROR\n", BESSPIN_TEST_PART);
#endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(BESSPIN_DEBIAN) || defined(BESSPIN_FREEBSD))
#include "unbufferStdout.h"

int main(int argc, char *argv[])
{
  unbufferStdout();

  int option;
  if (argc > 1) { //be safe
      option = atoi(argv[1]);
  } else {
      option = -1;
  }
  switch(option) {
    case 1 :
      printf("\n<fill_array>\n");
      stack_test(5);
      break;
    case 2 :
      printf("\n<fill_array_with_malloc>\n");
      heap_test(5);
      break;
    default :
      printf("SCORE:562:%d:TEST ERROR\n",option);
      return 1;
  }  
  return 0;
}

#endif // end of if FreeRTOS
