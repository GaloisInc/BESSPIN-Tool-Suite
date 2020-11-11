#include<stdio.h>
#include<string.h>

// Test 475 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

int main(void)
{
  char secret1[7] = {0x53, 0x45, 0x43, 0x52, 0x45, 0x54, 0x00};

  // c is an an array of char, but NOT zero-terminated
  char c[3] = { 0x41, 0x42, 0x43 };

  char secret2[7] = {0x53, 0x45, 0x43, 0x52, 0x45, 0x54, 0x00};

  // Three strings which ARE zero-terminated
  char secret3[7] = {0x53, 0x45, 0x43, 0x52, 0x45, 0x54, 0x00};
  char *s = "Hello";
  char secret4[7] = {0x53, 0x45, 0x43, 0x52, 0x45, 0x54, 0x00};

  // Do something with secret1 .. secret4 to stop the compiler
  // removing them
  printf ("TEST 475 PART P01\n");
  printf ("secret1 is %s\n", secret1);
  printf ("secret2 is %s\n", secret2);
  printf ("secret3 is %s\n", secret3);
  printf ("secret4 is %s\n", secret4);

  // If the next call to strcat() does a SEGFAULT, then it will be scored
  // as such. If it does not SEGFAULT, then whetever score is logged below
  // will take precedence.

  // Undefined behavior, since c is not terminated properly
  // and s is too small to hold any sort of concatenation of
  // s and c anyway.
  char *s2 = strcat (s, c);

  printf ("Trying to get length of s\n");

  size_t l = strlen (s); // SEGFAULT on RISC-V/Debian here

  printf ("Length of s is now %u\n", l);

  // If we reach this far, then the platform (either the CPU or the OS)
  // has failed to spot the undefined behavior in either of the
  // calls to strcat() or strlen() above, so we rate this as a FAIL
  printf ("SCORE:475:1:TEST FAILED\n");
  return 0;
}
