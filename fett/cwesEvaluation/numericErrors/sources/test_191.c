#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// Test 191 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

typedef struct pkt
{ uint32_t length; // length of the whole packet, inculding the length field itself and the
                   // number of _valid_ bytes of data
  char     data[32];
} packet;

packet d[3] =
  { { 21,  {'H','E','L','L','O',':','1','9','1',':','1',':', 'h', 'e', 'l', 'l', 'o', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', '\n'} },

    // This entry is mal-formed with length=2. It should be 21.
    { 2,  {'H','E','L','L','O',':','1','9','1',':','1',':', 'H', 'E', 'L', 'L', 'O', 'z', 'z', 'z', 'z', 'z', 'z', 'z', 'z', 'z', 'z', '\n'} },

    { 34, {'\n', 'S','C','O','R','E',':','1','9','1',':','1',':', 'T', 'O', 'P', ' ', 'S', 'E', 'C', 'R', 'E', 'T', ' ', 'S', 'T', 'U', 'F', 'F', '\n'} } };



void decode_and_print (packet *y)
{
  uint32_t data_length;

  // Potential for underflow here of the subtraction which might lead to
  // data_length being very large

  // Subtract the length of the length field to get the number of bytes of
  // valid data
  data_length = (y->length - sizeof(uint32_t));

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the underflow
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("data_length is %u\n", data_length);

  // Clip data-length to a sensible upper bound to prevent megabytes
  // of undefined garbage appearing on stdout
  if (data_length > 66)
    {
      data_length = 66;
    }

  for (uint32_t i = 0; i < data_length; i++)
    {
      printf ("%c", y->data[i]);
    }
  printf ("\n");
}

int main(void) {
  printf ("TEST 191 PART P01\n");

  // This test case inspired by CVE-2004-1002 which is cited on
  // the NIST CWE page for CWE-191

  // This should print "SCORE:191:1:hello" and nothing else
  decode_and_print (&d[0]);

  // This should print "SCORE:191:1:HELLO" but mal-formed "length" field
  // can cause overflow
  decode_and_print (&d[1]);

  return 0;
}
