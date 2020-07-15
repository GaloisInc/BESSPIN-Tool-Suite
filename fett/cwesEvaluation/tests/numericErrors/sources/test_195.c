#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// Test 195 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

// This test case has been adapted from "Example 4" given of the NIST CWE
// website for this CWE.

// Correctly-formed packet. Initial two-byte length field is 6
static char packet1[8] = { 0x06, 0x00, 'h', 'e', 'l', 'l', 'o', 0x00 };

// Mal-formed packet. Initial two-byte length field is -2 when
// interpreted as a little-endian signed integer.
static char packet2[8] = { 0xfe, 0xff, 'H', 'E', 'l', 'l', 'o', 0x00 };

static char buf[512];

void process (char *b)
{
  printf ("%s", b);
}

void processNext(char* strm) {
  int16_t len = *(int16_t *) strm;
  strm += sizeof(len);
  printf ("len is %d\n", len);

  // A programming defect - fails to check for negative values
  if (len <= 512) {

    // Implicit conversion from signed int16_t to unsigned size_t here
    // can result in a negative len value being converted to a very large
    // value of type size_t being passed to the third parameter of memcpy()
    size_t len_to_copy = len;

    // A SSITH CPU might spot the problem above and halt the program here.
    // To PASS this test, a SSITH CPU should prevent the signed to unsigned conversion
    // before the call to memcpy()
    // and print "<ABORT>" on stdout via whatever exception handling mechanism
    // is appropriate for that CPU and OS.

    // Defend against totally undefined behaviour here
    if (len_to_copy <= 512)
      {
        memcpy(buf, strm, len_to_copy);
        process(buf);
      }
    else
      printf ("SCORE:195:1:TEST FAILED");

  }
}

int main(void)
{
  printf ("TEST 195 PART P01\n");

  processNext (packet1);
  printf ("\n");
  processNext (packet2);
  printf ("\n");

  return 0;
}
