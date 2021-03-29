// This is the main function executed by besspin -- It is just a wrapper

#include "FreeRTOS.h"
#include "FreeRTOSIPConfig.h"

void main_besspin (void);
extern void main_netboot(void);

void main_besspin () {
    main_netboot();
}