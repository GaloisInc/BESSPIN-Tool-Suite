#include<stdio.h>
#include<stdint.h>
#include<stdlib.h>
#include<string.h>

#include "testsParameters.h"

#define NUM_OF_TEST_PARTS 2

static const char *secret_stuff = "SECRET STUFF";
static const char *safe_stuff = "SAFE STUFF";

void setup_data()
{
  const char *p1 = secret_stuff;
  const char *p2 = safe_stuff;

  printf ("Well-defined p1 points to %s\n", p1);
  printf ("Well-defined p2 points to %s\n", p2);
}

void safe_leak()
{
  printf ("%s\n", safe_stuff);
}

void secret_leak()
{
  printf ("%s\n", secret_stuff);
}


void setup_leaks()
{
  // Initialize two pointers-to-functions, use them and
  // leave their values lying around on the stack for later
  void (*f2)(void) = &secret_leak;
  void (*f1)(void) = &safe_leak;

  (*f1)();
  (*f2)();
}


// Test Part P01.
void p01()
{
  char *u1; // uninitialized...

  printf ("TEST 824 PART P01\n");

  printf ("Undefined pointer u1 points to %s\n", u1); // Undefined behavior

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  if (strcmp (u1, secret_stuff) == 0)
    printf ("SCORE:824:1:TEST FAILED\n");

}

// Test Part P02.
void p02()
{
  void (*f1)(void) ; // uninitialized...

  printf ("TEST 824 PART P02\n");

  printf ("SCORE:824:2:TOP ");
  (*f1)(); // call it... undefined behavior

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  // If this results in "TOP SECRET STUFF" appearing in the log,
  // then this will be scored as HIGH.
}


#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

int main()
{
#if TESTGEN_TEST_PART == 1
  setup_data();
  p01();
#elif TESTGEN_TEST_PART == 2 
  setup_leaks();
  p02();
#else
  printf ("SCORE:824:%d:TEST ERROR\n",TESTGEN_TEST_PART);
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
    {
      setup_data();
      p01();
    }
  else if (testpart == 2)
    {
      setup_leaks();
      p02();
    }
  else
    printf ("SCORE:824:%d:TEST ERROR\n",testpart);

  return 0;
}

#endif //end of ifdef testgenOnFreeRTOS

