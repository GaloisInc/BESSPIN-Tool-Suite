#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>
#include<unistd.h>
#include<string.h>
#include<sys/types.h>

#include "testsParameters.h"

#define NUM_OF_TEST_PARTS 3

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
      // Values smaller than LOOKUP_SIZE
      a = 0;
      b = 0;
      c = 5;
      d = 6;
    } else {
      // Values larger than LOOKUP_SIZE
      a = 48;
      b = 48;
      c = 41;
      d = 21;
  }
  return (a + b + c + d) / 4;
}


// Test Part P01.
// function returns an uninitialized value, but (by pure luck) is happens
// to be OK for a subsequent array access
void p01()
{
  int l, m;

  printf ("TEST 456 PART P01\n");

  l = mock_function (true);
  m = buggy (false);
  printf ("Uninitialized value m returned from buggy() is %d\n", m);

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("SCORE:456:1:TEST FAILED\n");

  printf ("Lookup[m] is %d\n", lookup[m]);
}

// Test Part P02.
// function returns an uninitialized value, but it goes on to
// cause a buffer overflow
void p02()
{
  int l, m;

  printf ("\nTEST 456 PART P02\n");

  l = mock_function (false);
  m = buggy (false);
  printf ("Uninitialized value m returned from buggy() is %d\n", m);

  if ((m >= 0) && (m < LOOKUP_SIZE))
    printf ("m uninitialized, but within bounds for Lookup\n");
  else
    printf ("m uninitialized, but out of bounds for Lookup\n");

  // Possible buffer overflow here depending on value of m
  printf ("Lookup[m] is %d\n", lookup[m]);

  // If execution reaches this point, we have to assume that the hardware
  // and/or OS has NOT spotted that m is uninitialized and possibly out
  // of range for lookup[], so this is a FAIL condition.
  printf ("SCORE:456:2:TEST FAILED\n");
}

// Test Part P03.
// function returns an uninitialized value, but it goes on to
// cause sensitive data to be output
static const char *dull_data =   "This is very boring and unclassified data";
static const char *secret_data = "SECRXT data"; // X is also a secret

void p03()
{
  int l, m;

  printf ("\nTEST 456 PART P03\n");

  l = mock_function (true);
  m = buggy (false);
  printf ("Uninitialized value m returned from buggy() is %d\n", m);
  printf ("Dull data is %s\n", &dull_data[m]);

  l = mock_function (false);
  m = buggy (false);
  printf ("Uninitialized value m returned from buggy() is %d\n", m);

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  // This printf() call leaks information if m is undefined. For example,
  // here we see an attempt to print dull_data, but we might actually
  // print secret_data if m is just the wrong value.
  printf ("Dull data is %s\n", &dull_data[m]);

  // Similarly, a SSITH CPU could prevent that undefined access to offset m
  // within dull_data, so if control flow reaches here, we assume FAIL
  printf ("SCORE:456:3:TEST FAILED\n");

}

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

int main()
{
#if TESTGEN_TEST_PART == 1
  p01();
#elif TESTGEN_TEST_PART == 2
  p02();
#elif TESTGEN_TEST_PART == 3
  p03();
#else
  printf ("SCORE:456:%d:TEST ERROR\n",TESTGEN_TEST_PART);
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
  else if (testpart == 3)
    p03();
  else
    printf ("SCORE:456:%d:TEST ERROR\n",testpart);

  return 0;
}

#endif //end of ifdef testgenOnFreeRTOS
