#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#define EXIT_FAILURE 1

typedef struct SubString {
    char *str;
    unsigned int  len;
} SubStr;

#ifdef testgenOnFreeRTOS
#if (defined(testgenFPGA))
#include "FreeRTOS.h"
#endif

// ----------------- FreeRTOS Test ----------
#define MALLOC(size) pvPortMalloc(size)
#define FREE(ptr)   vPortFree(ptr)
#define NUM_OF_TEST_PARTS 2

static SubStr *
SubStr_new(char* s, unsigned int l)
{
    #if (defined(testgenFPGA))
        SubStr *r = MALLOC(sizeof(int) * 5);
    #else
        SubStr *r = malloc(sizeof(SubStr));
    #endif

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


void test_double_free(char *str, char *dest) {
  SubStr *r= SubStr_new(str, 4);
  if (r != NULL) {
    strcpy(dest, r->str); // REGULAR
    printf("\n<REGULAR_PASSED> Copied string: %s\n", dest);
    #if (defined(testgenFPGA))
        FREE(r);
    #else
        free(r);
    #endif
  } else {
    printf("Error! NUll pointer.");
    exit(EXIT_FAILURE);
  }
  // pointer being freed was not allocated
  #if (defined(testgenFPGA))
        FREE(r);
    #else
        free(r);
    #endif
}

void test_free_no_longer_valid(char *str, char *dest) {
  SubStr *r= SubStr_new(str, 4);
  if (r != NULL) {
    strcpy(dest, r->str); // REGULAR
    printf("\n<REGULAR_PASSED> Copied string: %s\n", dest);
    #if (defined(testgenFPGA))
        FREE(r);
    #else
        free(r);
    #endif
  } else {
    printf("Error! NULL pointer.");
    exit(EXIT_FAILURE);
  }
  printf("\n<POINTER_USED_IMPROPERLY> pointer being freed and used improperly. %s\n", r->str);
}

void main() {
    char dest[5];
    char test_str [] = "test";
    char *str = &test_str[0];
      printf("\n<OSIMAGE=FreeRTOS>\n");
    #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: test_double_free.---\n");
        test_double_free(str, dest);
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: test_free_no_longer_valid.---\n");
        test_free_no_longer_valid(str, dest);
    #else
        printf("SCORE:825:%d:TEST ERROR\n",TESTGEN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

static SubStr *
SubStr_new(char* s, unsigned int l)
{
  SubStr *r = malloc(sizeof(SubStr));
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

void test_double_free(char *str, char *dest) {
  SubStr *r= SubStr_new(str, 4);
  if (r != NULL) {
    strcpy(dest, r->str); // REGULAR
    printf("\n<REGULAR_PASSED> Copied string: %s\n", dest);
    free(r);
  } else {
    printf("Error! NUll pointer.");
    exit(EXIT_FAILURE);
  }

  free(r); // pointer being freed was not allocated
  printf("\n<POINTER_USED_IMPROPERLY>\n");
}

void test_free_no_longer_valid(char *str, char *dest) {
  SubStr *r= SubStr_new(str, 4);
  if (r != NULL) {
    strcpy(dest, r->str); // REGULAR
    printf("\n<REGULAR_PASSED> Copied string: %s\n", dest);
    free(r);
  } else {
    printf("Error! NULL pointer.");
    exit(EXIT_FAILURE);
  }
  printf("\n<POINTER_USED_IMPROPERLY> pointer being freed and used improperly. %s\n", r->str);
}

int main(int argc, char *argv[]) {
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
        default :
            printf("SCORE:825:%d:TEST ERROR\n",option);
            return 1;
    }  
    return 0;
}

#endif // end of if FreeRTOS
