#include<stdio.h>
#include<stdarg.h>
#include<stdlib.h>

#include "testsParameters.h"

#define NUM_OF_TEST_PARTS 1 //test_234 has 1 part

// Return arithmetic average of the varargs parameters,
// but is coded wrong, assuming there are always exactly
// three such parameters
int f2 (int one, ...)
{
  int a[3], i;
  va_list ap;
  va_start (ap, one);
  for (i = 0; i < sizeof(a) / sizeof(int); i++)
    a[i] = va_arg(ap, int);
  va_end (ap);

  return (a[0] + a[1] + a[2]) / 3;
}

void do_p1 ()
{
  int a = 33;
  int b = 101;
  int c = 56;

  int d;

  printf ("TEST 234 PART P01\n");

  // Sanity check - call f2 with the correct number of args
  // to make sure it works OK.
  d = f2 (12, 10, 20, 30);

  printf ("function f returns %d\n", d);
  // d should be 20
  if (d == 20)
    {
      // OK... all is well so far
      d = f2 (12, 8, 10); // No compilation error here, but undefined

      // A SSITH CPU might spot the problem above and halt the program here.
      // To PASS this test, a SSITH CPU should prevent the undefined behavior here
      // and print "<ABORT>" on stdout via whatever exception handling mechanism
      // is appropriate for that CPU and OS.

      // If the program keeps running from here on, then we are into the realm
      // of undefined behavior.
      printf ("function f returns %d\n", d);
      
      // If control reaches here, then the undefined behavior has not been spotted
      // or prevented, so this is a FAIL
      printf ("SCORE:234:1:TEST FAILED\n");
    }
  else
    {
      // Something has gone wrong, even with a well-defined test case
      printf ("SCORE:234:1:TEST ERROR\n");
    }
}

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

int main()
{
#if TESTGEN_TEST_PART == 1
  do_p1();
#else
  printf ("SCORE:234:1:TEST ERROR\n");
#endif
  return 0;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

int main (int argc, char *argv[]) {
  int testpart;
  if (argc > 1) {
    testpart = atoi(argv[1]);
  } else {
    testpart = 0;
  }

  if (testpart == 1)
    do_p1();
  else
    printf ("SCORE:234:1:TEST ERROR\n");

  return 0;
}

#endif //end of ifdef testgenOnFreeRTOS

