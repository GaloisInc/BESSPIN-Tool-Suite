// This test is adapted from the example code
// cited in the SEI's CERT C Coding Standard
// Rule MEM07-C

#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
#endif

// Test 128 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

int main(void) {
  size_t s;
  size_t l;
  int *ptr_1;
  int *ptr_2;

  printf ("TEST 128 PART P01\n");

  printf ("Size of size_t is %d\n", sizeof(size_t));

  if (sizeof(size_t) == 4)
    {
      l = (UINT32_MAX / sizeof(int)) + 1;
      // note that printf() on FreeRTOS does not support the %zu
      // format specifier
      printf ("UINT32_MAX is %u\n", (size_t) UINT32_MAX);
      printf ("l is %u\n", l);
    }
  else // assume 8
    {
      l = (UINT64_MAX / sizeof(int)) + 1;
      printf ("UINT64_MAX is %zu\n", (size_t) UINT64_MAX);
      printf ("l is %zu\n", l);
    }

  // First, let's try a case that should work fine
  s = 1024 * sizeof(int);
  printf ("Going to malloc %u bytes\n", s);
#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
  ptr_1 = (int *) pvPortMalloc (s);
#else
  ptr_1 = (int *) malloc (s);
#endif
  if (ptr_1 != NULL)
    for (size_t j = 0; j < 1024; j++)
      ptr_1 [j] = 0;
  else
    printf ("SCORE:128:1:TEST ERROR\n");

  printf ("Alloc and init of 1024 ints successful\n");

  // Second, a case that is contrived to fail
  s = l * sizeof(int); // Overflow back to zero since size_t is unsigned

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the numeric overflow here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  if (sizeof(size_t) == 4)
    printf ("Going to malloc %u bytes\n", s);
  else
    printf ("Going to malloc %zu bytes\n", s);

  // Possibly attempt to malloc(0). Some implementations of malloc()
  // will check and fail here.
#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
  ptr_2 = (int *) pvPortMalloc (s);
#else
  ptr_2 = (int *) malloc (s);
#endif
  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the malloc(0)
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  if (ptr_2 != NULL)
    for (size_t j = 0; j < 16; j++) // Limit to first 16 bytes to ensure termination
      ptr_2 [j] = 0;
  else
    printf ("SCORE:128:1:TEST ERROR\n");

  // If still executing at this point, then we consider the test to be a FAIL
  printf ("SCORE:128:1:TEST FAILED\n");

  return 0;
}
