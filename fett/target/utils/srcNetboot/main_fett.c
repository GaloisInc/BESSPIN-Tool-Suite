// This is the main function executed by fett -- It is just a wrapper

#include "FreeRTOS.h"
#include "FreeRTOSIPConfig.h"

void main_fett (void);
extern void main_netboot(void);

void main_fett () {
    main_netboot();
}