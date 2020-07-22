// This test is adapted from the example code
// cited in the SEI's CERT C Coding Standard
// Rule EXP37-C

#include <stdio.h>
#include <string.h>

// Test 686 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian


// Wrong function prototype for strchr()
char *(*fp_wrong)();

// Correct function prototype for strchr()
char *(*fp_correct)(const char *, int);

int main(void) {
  char *c;

  printf ("TEST 686 PART P01\n");

  fp_correct = strchr; // copy pointer-to-strchr
  printf ("Calling strchr() via fp_correct pointer\n");
  c = fp_correct("Hello", 'e'); // Should be OK
  printf ("Back from call 1\n");
  printf("C is now %s\n", c); // c should point to "ello"

  fp_wrong = strchr; // copy pointer-to-strchr
  printf ("Calling strchr() via fp_wrong pointer\n");
  c = fp_wrong("Hello", 'e'); // Undefined behavior

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("Back from call 2\n");

  // We are now in an undefined state.
  // Printing C here is probably unwise, since it might
  // point to undefined nonsense.

  printf ("SCORE:686:1:TEST FAILED\n");

  return 0;
}
