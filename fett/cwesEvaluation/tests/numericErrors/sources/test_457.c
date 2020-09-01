#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>
#include<unistd.h>
#include<string.h>
#include<sys/types.h>

#include "testsParameters.h"

#define NUM_OF_TEST_PARTS 2

// NOTE
//
// This code requires compilation at -O0 to preserve undefined behavior.
// Other optimization levels might cause the behavior change and the
// test to pass and/or fail unexpectedly

#define LOOKUP_SIZE 10
static int lookup[LOOKUP_SIZE] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

static int buggy (bool b)
{
  int lv2;
  int lv;
  lv2 = 3;
  if (b)
    lv = lv2 + 1;

  return lv; // lv _might_ be uninitialized here, depending on b
}

// returns a well-defined value, but leaves initialized local variables on the stack
// Note has the same formal parameters/profile as buggy() above to maximize the
// change that local variables of this function will overlap with local variables
// of buggy()
static int mock_function (bool p)
{
  int a, b, c, d;
  if (p)
    {
      a = 0;
      b = 0;
      c = 0;
      d = 0;
    } else {
      a = 48; // Arbitrary but non-zero values
      b = 48;
      c = 41;
      d = 21;
  }
  return (a + b + c + d) / 4;
}


// Test Part P01.
void p01()
{
  int l, m, i, j;

  printf ("TEST 457 PART P01\n");

  l = mock_function (false);
  m = buggy (false);

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("Uninitialized value m returned from buggy() is %d\n", m);

  i = 100;
  j = i / m;
  printf ("P01 - value of j is %d\n", j);

  // if execution reaches here, it means that CPU or OS has failed to spot
  // the uninitialized value of m, or the division by zero, so this is a FAIL
  printf ("SCORE:457:1:TEST FAILED\n");
}

// Test Part P02.
void p02()
{
  int l, m, i, j;

  printf ("\nTEST 457 PART P02\n");

  l = mock_function (true);
  m = buggy (false);

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("Uninitialized value m returned from buggy() is %d\n", m);

  printf ("SCORE:457:2:TEST FAILED\n");

  i = 100;
  j = i / m; // Potential division by zero/DoS iff m us uninitialized and ZERO

  // Most CPUs trap on divide-by-zero, but RISC-V doesn't, so we can expect an
  // undefined value in j here.
  printf ("P02 - value of j is %d\n", j);
}


#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

int main()
{
#if TESTGEN_TEST_PART == 1
  p01();
#elif TESTGEN_TEST_PART == 2
  p02();
#else
  printf ("SCORE:457:%d:TEST ERROR\n",TESTGEN_TEST_PART);
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
    p01();
  else if (testpart == 2)
    p02();
  else
    printf ("SCORE:457:%d:TEST ERROR\n",testpart);

  return 0;
}

#endif //end of ifdef testgenOnFreeRTOS
