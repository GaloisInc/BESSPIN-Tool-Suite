// This test case has been adapted from the example shown
// in the SEI's CERT C Coding Standard, rule MEM04-C
// "Beware of zero-length allocations"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
#endif

// Test 687 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

int *allocate_and_init(int nelems)
{
  int *tmp;

  #if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    tmp = (int *) pvPortMalloc (nelems * sizeof(int));
  #else
    tmp = (int *) malloc (nelems * sizeof(int));
  #endif
  if (tmp == NULL) {
    printf ("SCORE:687:1:TEST ERROR\n");
    return NULL;
  }

  for (int i = 0; i < nelems; i++)
    tmp[i] = 0xff;

  return tmp;
}

int main (void)
{
  int *a1;
  int *a2;

  printf ("TEST 687 PART P01\n");

  printf ("Test Part P01\n");
  a1 = allocate_and_init (10); // Should be OK
  if (a1 == NULL)
    {
      printf ("SCORE:687:1:TEST ERROR\n");
      return 0;
    }

  printf ("a1[0] is %d\n", a1[0]);

  a2 = allocate_and_init (0); // Unspecified behavior
  if (a2 == NULL)
    {
      printf ("SCORE:687:1:TEST ERROR\n");
      return 0;
    }

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("a2[0] is %d\n", a2[0]);

  printf ("SCORE:687:1:TEST FAILED\n");

  return 0;
}
