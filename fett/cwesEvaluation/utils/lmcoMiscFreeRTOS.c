/*
Functions used for LMCO exception handler on FreeRTOS
*/

#include <stdio.h>

void exitFett (uint8_t exitCode);

void exitFett (uint8_t exitCode) {
    printf ("EXIT: exiting fett with code <%x>\n",exitCode);
    printf ("\n>>>End of Fett<<<\n");
    return;
}
