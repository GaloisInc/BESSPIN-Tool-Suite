// This is a minimal program that broadcasts a specific string to the UART

#include <stdio.h>
#include "fettFreeRTOSConfig.h"

void main_fett (void);

void main_fett () {
    printf(FETT_HWID);
    return;
}