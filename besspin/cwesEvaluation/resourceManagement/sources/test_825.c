#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define EXIT_FAILURE 1
#define NUM_OF_TEST_PARTS 3

#if defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA)
  #include "FreeRTOS.h"
  #define MALLOC(size) pvPortMalloc(size)
  #define FREE(ptr)   vPortFree(ptr)
#else
  #define MALLOC malloc
  #define FREE free
#endif

typedef struct SubString {
  char *str;
  unsigned int  len;
} SubStr;

static SubStr *
SubStr_new(char* s, unsigned int l)
{
  SubStr *r = MALLOC(sizeof(SubStr));

  if (r != NULL) {
    printf("Memory allocation succeeded.\n");
    r->str = s;
    r->len = l;
  } else {
    printf("Memory allocation failed.\n");
    exit(EXIT_FAILURE);
  }
  return r;
}

// Erroneously return a pointer to a stack allocated SubStr
static SubStr* SubStr_new_stack(char *s, unsigned int l) {
  SubStr r = {s, l};

  // Have to store as a local pointer `p` and return `p` because the compiler
  // will transform `return &r` to `return NULL`, even with optimizations
  // disabled.  This is a legal transformation after all since `return &r` is
  // undefined behavior.
  SubStr* p = &r;
  return p;
}

void test_double_free(char *str, char *dest) {
  SubStr *r= SubStr_new(str, 4);
  if (r != NULL) {
    strcpy(dest, r->str); // REGULAR
    printf("\n<REGULAR_PASSED> Copied string: %s\n", dest);
    FREE(r);
  } else {
    printf("Error! Null pointer.");
    exit(EXIT_FAILURE);
  }
  // Double free
  FREE(r);
  printf("\n<POINTER_USED_IMPROPERLY>\n");
}

void test_free_no_longer_valid(char *str, char *dest) {
  SubStr *r= SubStr_new(str, 4);
  if (r != NULL) {
    strcpy(dest, r->str); // REGULAR
    printf("\n<REGULAR_PASSED> Copied string: %s\n", dest);
    FREE(r);
  } else {
    printf("Error! NULL pointer.");
    exit(EXIT_FAILURE);
  }
  printf("\n<POINTER_USED_IMPROPERLY> pointer being freed and used improperly. %s\n", r->str);
}

void test_stack_invalid(char *str) {
  SubStr *r = SubStr_new_stack(str, 4);

  if (!r) {
    // Compiler replaced SubStr_new_stack return with `return NULL`.
    printf("\n<INVALID>\n");
    exit(EXIT_FAILURE);
  }

  // r points to expired stack memory, so dereferencing here is undefined
  // behavior.
  printf("Length of substr is %u\n", r->len);
  printf("\n<POINTER_USED_IMPROPERLY>\n");
}

#ifdef BESSPIN_FREERTOS

// ----------------- FreeRTOS Test ----------

void main() {
  char dest[5];
  char test_str [] = "test";
  char *str = &test_str[0];
  printf("\n<OSIMAGE=FreeRTOS>\n");
#if BESSPIN_TEST_PART == 1
  printf("\n---Part01: test_double_free.---\n");
  test_double_free(str, dest);
#elif BESSPIN_TEST_PART == 2
  printf("\n---Part02: test_free_no_longer_valid.---\n");
  test_free_no_longer_valid(str, dest);
#elif BESSPIN_TEST_PART == 3
  printf("\n---Part03: test_stack_invalid.---\n");
  test_stack_invalid(str);
#else
  printf("SCORE:825:%d:TEST ERROR\n",BESSPIN_TEST_PART);
#endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#else
#include "unbufferStdout.h"

int main(int argc, char *argv[]) {
  unbufferStdout();
  char dest[5];
  char test_str [] = "test";
  char *str = &test_str[0];
  int option;
  if (argc > 1) { //be safe
    option = atoi(argv[1]);
  } else {
    option = -1;
  }
  switch(option) {
    case 1 :
      printf("\n<test-double-free>\n");
      test_double_free(str, dest);
      break;
    case 2 :
      printf("\n<test-free-no-longer-valid>\n");
      test_free_no_longer_valid(str, dest);
      break;
    case 3 :
      printf("\n<test-stack-invalid>\n");
      test_stack_invalid(str);
      break;
    default :
      printf("SCORE:825:%d:TEST ERROR\n",option);
      return 1;
  }
  return 0;
}

#endif // end of if FreeRTOS
