#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
#define MALLOC pvPortMalloc
#else
#define MALLOC malloc
#endif

/** Address of stack memory associated with local variable 'a' returned */
int*
fill_array(int n) {
  int a[n];
  for (int i = 0; i < n; i++) {
    a[i] = i;
  }
  return a;
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

// ----------------- FreeRTOS Test ----------
#ifdef testgenOnFreeRTOS

#define NUM_OF_TEST_PARTS 2

void
print_array(int *tab, int n) {
  int k = 0;
  for (int i = 0; i < n; i++) {
    printf("%d ", tab[i]); // prints the array
    if (tab[i] == i) {
      k = k + 1;
    }
  }
  printf("\n<DEREFERENCE-VIOLATION>\n");
}

void
print_array_correct(int *tab, int n) {
  int k = 0;
  for (int i = 0; i < n; i++) {
    printf("%d ", tab[i]); // prints the array
    if (tab[i] == i) {
      k = k + 1;
    }
  }
  if (k == n) {
    printf("\n<VALID_ARRAY_CONTENT>\n");
  } else {
    printf("\n<NOT_VALID_ARRAY_CONTENT>\n");
  }
}


void main() {
  int *b;
  int *c;
  printf("\n<OSIMAGE=FreeRTOS>\n");
#if TESTGEN_TEST_PART == 1
  printf("\n---Part01: fill_array.---\n");
  b = fill_array(5);
  print_array(b, 5);
#elif TESTGEN_TEST_PART == 2
  printf("\n---Part02: fill_array_with_malloc.---\n");
  c = fill_array_with_malloc(5);
  print_array_correct(c, 5);
#else
  printf("SCORE:562:%d:TEST ERROR\n", TESTGEN_TEST_PART);
#endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

void
print_array(int *tab, int n) {
  printf("\n<print_array>\n");
  int k = 0;
  for (int i = 0; i < n; i++) {
    printf("%d ", tab[i]); // prints the array
    if (tab[i] == i) {
      k = k + 1;
    }
  }

  if (k == n) {
    printf("\n<VALID_ARRAY_CONTENT>\n");
  } else {
    printf("\n<NOT_VALID_ARRAY_CONTENT>\n");
  }
}

int main(int argc, char *argv[])
{
  
  int *b;
  int *c;

  int option;
  if (argc > 1) { //be safe
      option = atoi(argv[1]);
  } else {
      option = -1;
  }
  switch(option) {
      case 1 :
          printf("\n<fill_array>\n");
          b = fill_array(5);
          print_array(b, 5);
          break;
      case 2 :
          // no free here
          printf("\n<fill_array_with_malloc>\n");
          c = fill_array_with_malloc(5);
          print_array(c, 5);
          free(c);
          break;
      default :
          printf("SCORE:562:%d:TEST ERROR\n",option);
          return 1;
  }  
  return 0;
}

#endif // end of if FreeRTOS
