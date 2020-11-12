#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// Test 192 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian


static char *some_data = "SCORE:192:1:TOP SECRET STUFF";

int GetUntrustedInt ()
{
  return(0x0000FFFF);
}

char *GetUserInput ()
{
  return some_data;
}

int main (void) {

  // This example is adapted from "Example 2" on the NIST CWE website for
  // CWE 192 here: https://cwe.mitre.org/data/definitions/192.html

  char path[256];
  char *input;

  int32_t i;
  int16_t s;
  uint32_t sz;

  printf ("TEST 192 PART P01\n");

  i = GetUntrustedInt();

  // type coercion occurs here. If i == 0x0000FFFF, then
  // s = -1
  s = i;

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the coercion
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  /* s is sign-extended and saved in sz */
  sz = s;

  /* output: i=65535, s=-1, sz=4294967295 - your mileage may vary */
  printf("i=%d, s=%d, sz=%u\n", i, s, sz);

  input = GetUserInput();

  if (s >= 0 && s <= 256)
    {
      // More coercion occurs here as s is implicitly converted to unsigned int
      // A SSITH CPU might spot the problem above and halt the program here.
      // To PASS this test, a SSITH CPU should prevent the coercion
      // and print "<ABORT>" on stdout via whatever exception handling mechanism
      // is appropriate for that CPU and OS.
      strncpy(path, input, s);
      path[255] = '\0'; /* don't want CWE-170 */
      printf("%s\n", path);
    }
  else
    {
      // If s is negative, then coercion has occurred and gone undetected, so we
      // consider this a failure
      if (s < 0) printf ("SCORE:192:1:TEST FAILED\n");
    }

  return 0;
}
