/*
This is used to provide an empty main function to compile FreeRTOS for tests which just need the OS to be
running, but does not need to fill the test with anything.
*/

#define THIS_TEST "FILLER"

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA))
    #include "FreeRTOS.h"
#endif

#include <stdio.h>

int main () {
    printf ("This is a filler!\n");
    #ifdef BESSPIN_UNIX
        printf ("<INVALID> Fillers are only for FreeRTOS. This should never be executed.\n");
    #endif
    return 0;
}
    


