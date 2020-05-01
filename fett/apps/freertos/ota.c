// This is the main task executed by ota

#include "fettFreeRTOS.h"

void vOta (void *pvParameters);

void vOta (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;

    fettPrintf("(Info)~  vOta: Starting OTA...\r\n");

    /* Code goes here */

    fettPrintf("(Info)~  vOta: Exitting OTA...\r\n");

    //notify main
    vERROR_IF_EQ(xMainTask, NULL, "vOta: Get handle of <main:task>.");
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS_OTA ,eSetValueWithOverwrite);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vOta: Notify <main:task>.");

    vTaskDelete (NULL);
}
