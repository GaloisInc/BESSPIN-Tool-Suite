// This is the main task executed by https

#include "fettFreeRTOS.h"

void vHttps (void *pvParameters);

void vHttps (void *pvParameters) {
    (void) pvParameters;
    xMainTask = xTaskGetCurrentTaskHandle();

    fettPrintf("vHTTPS: Starting HTTPS...\r\n");
    
    vEXIT(0);
}
