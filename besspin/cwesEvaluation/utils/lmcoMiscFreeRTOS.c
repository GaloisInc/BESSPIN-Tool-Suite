/*
Functions used for LMCO exception handler on FreeRTOS
*/

#include <stdio.h>

void exitBesspin (uint8_t exitCode);

void exitBesspin (uint8_t exitCode) {
    printf ("EXIT: exiting besspin with code <%x>\n",exitCode);
    printf ("\n>>>End of Besspin<<<\n");
    return;
}
