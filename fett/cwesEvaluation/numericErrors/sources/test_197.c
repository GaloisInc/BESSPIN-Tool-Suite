// This test case has been adapted from "Example 1" shown
// on the CWE site for CWE 197

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>

// Test 197 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

static const char *msg = "Hello World";

int main (void)
{
  int32_t i;
  int16_t s;

  printf ("TEST 197 PART P01\n");

  printf ("msg is %s\n", msg);

  i = INT_MAX;

  // Truncation! On most implementations, this will drop the most-significant
  // bits of i, and preserve the lower 16 bits with unsigned value 0xffff,
  // signed value -1
  s = i;

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the truncation here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("i is %d\n", i);
  printf ("s is %d\n", s);

  // Attempt to use s might result in a buffer overflow or underflow, so
  // we'll try that to get a second chance to spot this problem.
  printf ("msg[s] is %c\n", msg[s]);

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the buffer overflow
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  // Print something well-defined so we know the test case has reached
  // this point.
  printf ("msg[0] is %c\n", msg[0]);

  printf ("SCORE:197:1:TEST FAILED\n");

  return 0;
}
