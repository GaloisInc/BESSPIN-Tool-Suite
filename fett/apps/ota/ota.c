// This is the main task executed by ota

#include "fettFreeRTOS.h"

void vOta (void *pvParameters);

void vOta (void *pvParameters) {
    (void) pvParameters;
    xMainTask = xTaskGetCurrentTaskHandle();

    fettPrintf ("vOTA: Starting OTA...\r\n");

    vEXIT(0);
}
