// This test is adapted from the example code
// cited in the SEI's CERT C Coding Standard
// Rule MEM07-C

#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "testsParameters.h"

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA))
#include "FreeRTOS.h"
#define FREE vPortFree
#define MALLOC pvPortMalloc
#else
#define FREE free
#define MALLOC malloc
#endif

#define NUM_OF_TEST_PARTS 2

void check_test_error(bool error, int part) {
  if (error) {
    printf("SCORE:128:%d:TEST ERROR\n", part);
    exit(1);
  }
}

/**
 * Overflow a size_t input to malloc to allocate a 0 byte buffer and overrun
 * the buffer
 */
void test_size_t(void) {
  size_t s;
  size_t l;
  int *ptr_1;
  int *ptr_2;

  printf ("TEST 128 PART P01\n");

  printf ("Size of size_t is %d\n", sizeof(size_t));

  if (sizeof(size_t) == 4)
    {
      l = (UINT32_MAX / sizeof(int)) + 1;
      // note that printf() on FreeRTOS does not support the %zu
      // format specifier
      printf ("UINT32_MAX is %u\n", (size_t) UINT32_MAX);
      printf ("l is %u\n", l);
    }
  else // assume 8
    {
      l = (UINT64_MAX / sizeof(int)) + 1;
      printf ("UINT64_MAX is %zu\n", (size_t) UINT64_MAX);
      printf ("l is %zu\n", l);
    }

  // First, let's try a case that should work fine
  s = 1024 * sizeof(int);
  printf ("Going to malloc %u bytes\n", s);
  ptr_1 = (int *) MALLOC(s);
  check_test_error(!ptr_1, 1);
  for (size_t j = 0; j < 1024; j++) {
    ptr_1 [j] = 0;
  }
  FREE(ptr_1);
  printf ("Alloc and init of 1024 ints successful\n");

  // Second, a case that is contrived to fail
  s = l * sizeof(int); // Overflow back to zero since size_t is unsigned

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the numeric overflow here
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  if (sizeof(size_t) == 4)
    printf ("Going to malloc %u bytes\n", s);
  else
    printf ("Going to malloc %zu bytes\n", s);

  // Possibly attempt to malloc(0). Some implementations of malloc()
  // will check and fail here.
  ptr_2 = (int *) MALLOC(s);

  // A SSITH CPU might spot the problem above and halt the program here.
  // To PASS this test, a SSITH CPU should prevent the malloc(0)
  // and print "<ABORT>" on stdout via whatever exception handling mechanism
  // is appropriate for that CPU and OS.

  check_test_error(!ptr_2, 1);
  for (size_t j = 0; j < 16; j++) {
    // Limit to first 16 elements to ensure termination
    ptr_2 [j] = 0;
  }
  FREE(ptr_2);

  // If still executing at this point, then we consider the test to be a FAIL
  printf ("SCORE:128:1:TEST FAILED\n");
}

/**
 * Overflow a uint8_t input to malloc to allocate a 0 byte buffer and overrun
 * the buffer
 */
void test_uint8_t(void) {
  // Number of elements in first buffer
  const int ELEMENTS_1 = 64;
  const int ELEMENTS_2 = 128;

  printf ("TEST 128 PART P02\n");

  // Perform an allocation that should work (128 bytes)
  uint8_t size_1 = ELEMENTS_1 * sizeof(uint16_t);
  printf("Going to malloc %u bytes\n", (unsigned int) size_1);
  uint16_t *ptr_1 = (uint16_t*) MALLOC(size_1);
  check_test_error(!ptr_1, 2);
  for (int i = 0; i < ELEMENTS_1; ++i) {
    ptr_1[i] = 0;
  }
  FREE(ptr_1);
  printf("Alloc and init of %d uint16_ts successful\n", ELEMENTS_1);

  // Overflow size_2 and malloc(0)
  uint8_t size_2 = ELEMENTS_2 * sizeof(uint16_t);  // Overflows to 0
  printf("Going to malloc %u bytes\n", (unsigned int) size_2);
  uint16_t *ptr_2 = (uint16_t*) MALLOC(size_2);
  check_test_error(!ptr_2, 2);
  for (int i = 0; i < 16; ++i) {
    // Limit to first 16 elements to avoid segfault
    ptr_2[i] = 0;
  }
  FREE(ptr_2);
  // If still executing at this point, then we consider the test to be a FAIL
  printf ("SCORE:128:2:TEST FAILED\n");
}
#ifdef BESSPIN_FREERTOS
//---------------- FreeRTOS test ------------------------------------------------------

int main()
{
#if BESSPIN_TEST_PART == 1
  test_size_t();
#elif BESSPIN_TEST_PART == 2
  test_uint8_t();
#else
  printf ("SCORE:456:%d:TEST ERROR\n",BESSPIN_TEST_PART);
#endif
  return 0;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(BESSPIN_DEBIAN) || defined(BESSPIN_FREEBSD))
#include "unbufferStdout.h"

int main(int argc, char **argv) {
  unbufferStdout();
  int testpart;
  if (argc > 1) {
    testpart = atoi(argv[1]);
  } else {
    testpart = 0;
  }

  switch (testpart) {
    case 1:
      test_size_t();
      break;
    case 2:
      test_uint8_t();
      break;
    default:
      check_test_error(true, testpart);
  }

  return 0;
}
#endif
