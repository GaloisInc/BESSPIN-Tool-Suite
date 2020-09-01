// This test case has been adapted from "Example 1" shown
// on the CWE site for CWE 588, which is a child of CWE 704

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>

// Test 704 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

typedef struct foo
{
  int i;
} foo;

static foo *t;

int f1 (int x)
{
  return x + 1;
}

int main (void)
{
  printf ("TEST 704 PART P01\n");

  // Conversion of function pointer f1 to pointer-to-foo value...
  printf ("Cast from f1 to *foo\n");
  t = (foo *)f1;

  // Undefined behavior from here on... attempting to write to *t might
  // be impossible on some platforms.
  printf ("Assign to t->i\n");
  t->i = 2;

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the conversion or assignment
  // to t->i and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("t->i is %d\n", t->i);

  printf ("SCORE:704:1:TEST FAILED\n");

  return 0;
}
