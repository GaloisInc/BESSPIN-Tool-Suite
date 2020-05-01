// This is the main task executed by ota

#include "fettFreeRTOS.h"

void vOta (void *pvParameters);

void vOta (void *pvParameters) {
    (void) pvParameters;
    xMainTask = xTaskGetCurrentTaskHandle();

    fettPrintf ("\nStarting OTA...\n");

    vEXIT(0);
}
