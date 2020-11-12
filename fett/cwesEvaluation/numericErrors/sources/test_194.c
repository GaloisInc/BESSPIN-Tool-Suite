#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// Test 194 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

// This test case has been adapted from the example given at
//   https://docs.oracle.com/cd/E19205-01/819-5265/bjamz/index.html

struct foo {
unsigned int base:8, rehash:13;
};

static int32_t table[2] = { 3, 6 };
int main(void)
{
  struct foo a;
  uint64_t addr;
  int32_t index;

  printf ("TEST 194 PART P01\n");

  // Case 1 - No sign extension owing to explicit cast

  // note a.base is an 8-bit bit-field, so this sets the "sign bit"
  // assuming 2s complement representation
  a.base = 0x80;

  // No sign extension here owing to explicit cast
  addr = (unsigned int)(a.base << 24);
  index = addr >> 32;
  printf("addr %llu, index %ld\n", addr, index);

  // index should be 0 here so this should print "3"
  printf ("table[index] is %ld\n", table[index]);


  // Case 2 - Unexpected sign extension

  // note a.base is an 8-bit bit-field, so this sets the "sign bit"
  // assuming 2s complement representation
  a.base = 0x80;

  // Non-obvious sign extension here!
  // With no explicit cast, a.base is promoted to "int" so "a.base << 24" also has
  // type "int" so is sign-extended before conversion to "unsigned long"
  addr = a.base << 24;

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the sign extension
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  index = addr >> 32;
  printf("addr %llu, index %ld\n", addr, index);

  // If index is negative, then undefined behavior here
  printf ("table[index] is %ld\n", table[index]);

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the buffer underflow
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.


  // If control-flow reaches here, then we assume the problem has gone un-noticed,
  // therefore this is a FAIL
  printf ("SCORE:194:1:TEST FAILED\n");

 return 0;
}
