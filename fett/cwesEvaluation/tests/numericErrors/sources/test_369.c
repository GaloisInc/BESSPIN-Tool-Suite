#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>

// Test 369 only has a single Part, so no special treatment is required
// here for multi-part running on FreeRTOS or Debian

// A function is declared and used to compute a divisor dynamically.
// This (hopefully) prevents optimization and potential removal of
// subsequent uses of that divisor

int32_t f (int32_t x)
{
  // note - returns 0 when x == 5
  if (x == 5)
    return 0;
  else
    return (x * 2) + 10;
}


//  Some data to be divided...
static int32_t data[10] = {100, 110, 120, 130, 140, 150, 160, 170, 180, 190};

int main (void)
{
  int32_t res;
  printf ("TEST 369 PART P01\n");

  for (int32_t i = 0; i < 10; i++)
    {
      res = data[i] / f(i);
      printf ("data[%d] / f(%d) is %d\n", i, i, res);
      // On RISC-V, divide by zero retuns "all bits set" (RISC-V ISA Spec Table 7.1)
      // so a standard RISC-V CPU will _not_ trap or raise an exception here.
      //
      // If a SSITH CPU _does_ trap and terminate the program here with <ABORT>
      // or <GDB-TRAP> then it is considered a pass
      //
      // On the other hand if the divide-by-zero goes undetected and control passes
      // here with res == -1, then that is considered a FAIL
      if (res == -1)
        printf ("SCORE:369:1:TEST FAILED\n");
    }

  return 0;
}
