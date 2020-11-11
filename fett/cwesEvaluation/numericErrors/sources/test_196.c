#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// Test 196 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

// pad xxx so these strings' lengths are an exact mutiple of 4,
// so word-aligned
static char secret1[] = "xxxTOP SECRET STUFF";
static char welcome_msg[] = "xxxHello there!";
static char secret2[] = "xxxTOP SECRET STUFF";

void print_secret1_fragment(void)
{
  // This call makes sure that secret1 isn't optimized away by the compiler
  printf ("%s\n", &secret1[11]);
}

void print_secret2_fragment(void)
{
  // This call makes sure that secret2 isn't optimized away by the compiler
  printf ("%s\n", &secret2[9]);
}


void print_welcome (int32_t initial_offset)
{
  printf ("%s\n", &welcome_msg[initial_offset]);
}

void print_dangerous (uint32_t offset)
{
  // Implicit conversion from unsigned to signed here

  print_welcome (offset);
  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the unsigned to signed conversion
  // before the call to memcpy()
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.
}

int main (void)
{
  uint32_t d;

  printf ("TEST 196 PART P01\n");

  // A few cases that should work OK first
  print_welcome (0);
  print_welcome (1);
  print_welcome (6);

  // A few more cases that should work OK first
  print_dangerous (0);
  print_dangerous (1);
  print_dangerous (6);

  // Do something useful with secret1 and secret2 to make sure they're
  // not optimized away by a compiler
  print_secret1_fragment();
  print_secret2_fragment();

  // Craft d so that it's very close to UINT32_MAX, and will be interpreted as a negative
  // number when passed to print_welcome()  If this happens to point to
  // secret1 or secret2, then a failure will result.
  d = UINT32_MAX - 26;
  print_dangerous (d);
  d = UINT32_MAX - 28;
  print_dangerous (d);
  d = UINT32_MAX - 30;
  print_dangerous (d);

  // If control reaches here, then we presume the platform has not mitigated
  // the potential vulnerabilities and undefined behavior, so
  printf ("SCORE:196:1:TEST FAILED\n");
  return 0;
}
