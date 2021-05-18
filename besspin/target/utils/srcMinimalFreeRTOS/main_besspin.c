// This is a minimal program that broadcasts a specific string to the UART

#include <stdio.h>
#include "besspinFreeRTOSConfig.h"

void main_besspin (void);

void main_besspin () {
    printf(BESSPIN_HWID);
    return;
}