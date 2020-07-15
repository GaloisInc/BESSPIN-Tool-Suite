#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// Test 190 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

// Precondition:  a > 0, b > 0
// Postcondition: result > 0, result == (a + b) / 2
int arithmetic_mean (int a, int b)
{
  int sum;

  sum = a + b; // Potential undefined behaviour here on overflow

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the overflow
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  return sum / 2;
}


int main(void) {
  int r;

  printf ("TEST 190 PART P01\n");

  // Case 1 - no overflow, so well-defined result
  r = arithmetic_mean (10, 20);
  // Check postcondition and report result
  if (r > 0)
    printf ("Case 1 OK - r is %d\n", r);
  else
    {
      printf ("Case 1 Fail - r is %d\n", r);
      printf ("SCORE:190:1:TEST FAILED\n");
    }

  // Case 2 - try to provoke overflow by asking for mean
  // of two values, both near 2**31
  r = arithmetic_mean (2147483646, 2147483645);
  // Check postcondition and report result
  if (r > 0)
    printf ("Case 2 OK - r is %d\n", r);
  else
    {
      printf ("Case 2 Fail - r is %d\n", r);
      printf ("SCORE:190:1:TEST FAILED\n");
    }
  return 0;
}
