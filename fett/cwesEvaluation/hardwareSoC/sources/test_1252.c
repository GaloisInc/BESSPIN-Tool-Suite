/*
Test_1252: CPU Hardware Not Configured to Support Exclusivity of Write and Execute Operations
*/

#define THIS_TEST "1252"

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    #include "FreeRTOS.h"
#endif

#include <stdio.h>

int main(void);

int main () {
    printf ("<INVALID> This test is GDB interactive!\n");
    return 0;
}