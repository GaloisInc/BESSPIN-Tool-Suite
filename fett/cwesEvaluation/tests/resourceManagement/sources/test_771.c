// Tests for CWE-771: Missing Reference to Active Allocated Resource
// @see https://cwe.mitre.org/data/definitions/771.html
// @author Joe Kiniry <kiniry@galois.com>

// # Description
// The software does not properly maintain a reference to a resource
// that has been allocated, which prevents the resource from being
// reclaimed.
// # Extended Description
// This does not necessarily apply in languages or frameworks that
// automatically perform garbage collection, since the removal of all
// references may act as a signal that the resource is ready to be
// reclaimed.

#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
#define MALLOC malloc
#define FREE free
#endif

// OS-generic test code follows.

// This sample code is derived from the SEI CERT C Coding Standard
// Sec. 9.2.1

enum { BUFFER_SIZE = 32 };

// In this non-compliant example, the object allocated by the call to
// malloc() is not freed before the end of the lifetime of the last
// pointer text_buffer referring to the object.

int f(void) {
    char *text_buffer = (char *)MALLOC(BUFFER_SIZE);
    if (text_buffer == NULL) {
        printf("\n<F_MALLOC_FAILED>\n");
    }
    printf("\n<F_MALLOC_SUCCEEDED>\n");
}
// a secure CPU should trap or flag f() when it ends due to a lack of
// free() on text_buffer

// This sample code is derived from the SEI CERT C Coding Standard
// Sec. 9.4.1

enum { MAX_ALLOCATION = 1000 };

int g(char *str) {
    char *c_str = NULL;
    size_t len;

    len = strlen(str) + 1;
    if (len > MAX_ALLOCATION) {
        /* Handle error */
    }
    c_str = (char *)MALLOC(len);
    if (c_str == NULL) {
        /* Handle error */
        printf("\n<POINTER_IS_NULL>\n");
    }
    strcpy(c_str, str);
    // This is an improper free because c_str wasn't allocated with
    // malloc.
    FREE(c_str);
    printf("\n<FREE_WAS_NOT_TRAPPED>\n");
    return 0;
}

#ifdef testgenOnFreeRTOS
// ----------------- FreeRTOS Test ----------
#define NUM_OF_TEST_PARTS 5

void main() {
  printf("\n<OSIMAGE=FreeRTOS>\n");
  #if TESTGEN_TEST_PART == 1
        printf("\n---Part01: _not_freed.---\n");
        f();
    #elif TESTGEN_TEST_PART == 2
        printf("\n---Part02: g_input_param_empty_string.---\n");
        g("");
    #elif TESTGEN_TEST_PART == 3
        printf("\n---Part03: g_input_param_space.---\n");
        g(" ");
    #elif TESTGEN_TEST_PART == 4
        printf("\n---Part04: g_first_input_param---\n");
        g("SSITH");
    #elif TESTGEN_TEST_PART == 5
        printf("\n---Part05: g_second_input_param.---\n");
        g("BESSPIN");
    #else
        printf("SCORE:771:%d:TEST ERROR\n",TESTGEN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

int main()
{
    printf("\n<f_not_freed>\n");
    f();
    printf("\n<g_input_param_empty_string>\n");
    g("");
    printf("\n<g_input_param_space>\n");
    g(" ");
    printf("\n<g_first_input_param>\n");
    g("SSITH");
    printf("\n<g_second_input_param>\n");
    g("BESSPIN");
    return 0;
}
#endif // end of if FreeRTOS
