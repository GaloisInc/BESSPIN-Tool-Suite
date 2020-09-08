#include<stdio.h>
#include<stdint.h>
#include<stdlib.h>
#include<stdbool.h>
#include<unistd.h>
#include<string.h>
#include<sys/types.h>

#include "testsParameters.h"

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
#endif

#define NUM_OF_TEST_PARTS 2

void do_secret_stuff()
{
  uint8_t secret[7] = {0x53, 0x45, 0x43, 0x52, 0x45, 0x54, 0x00};
  int sum = 0;
  // Do something with secret to avoid the compiler removing it.
  for (int i = 0; i < 7; i++)
    sum += secret[i];
  printf ("Average secret is %d\n", sum / 7);
}

// Test Part P01.
void p01()
{
  // Adapted from the example code given for CWE-665 on the MITRE CWE site.
  char str1[20]; // Not initialized therefore probably not null-terminated

  printf ("TEST 665 PART P01\n");

  strncat(str1, "hello", 5); // undefined behavior

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("strlen(str1) is now %d\n", (int) strlen(str1));

  printf ("str1 points to\n");
  for (int i = 0; i < 20; i++)
    printf ("%2X ", str1[i]);
  printf ("\n");

  printf ("SCORE:665:1:TEST FAILED\n");
}

// Test Part P02. As P01, but allocated str1 off the heap
void p02()
{
  char *str1;
  printf ("TEST 665 PART P02\n");

  #if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    str1 = (char *) pvPortMalloc (20);
  #else
    str1 = (char *) malloc (20);
  #endif
  if (str1 == NULL) {
    printf ("SCORE:665:2:TEST ERROR\n");
    return;
  }

  strncat(str1, "hello", 5);

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the undefined behavior here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  printf ("strlen(str1) is now %d\n", (int) strlen(str1));

  printf ("str1 points to\n");
  for (int i = 0; i < 20; i++)
    printf ("%2X ", str1[i]);
  printf ("\n");

  printf ("SCORE:665:2:TEST FAILED\n");
}

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

int main()
{
  do_secret_stuff();
#if TESTGEN_TEST_PART == 1
  p01();
#elif TESTGEN_TEST_PART == 2
  p02();
#else
  printf ("SCORE:665:%d:TEST ERROR\n", TESTGEN_TEST_PART);
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

  do_secret_stuff();
  if (testpart == 1)
    p01();
  else if (testpart == 2)
    p02();
  else
    printf ("SCORE:665:%d:TEST ERROR\n", testpart);

  return 0;
}

#endif //end of ifdef testgenOnFreeRTOS
