// This is the main task executed by ota

#include "fettFreeRTOS.h"
#include "ota_tests.h"

void vOta (void *pvParameters);

void vOta (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;

    fettPrintf("(Info)~  vOta: Starting OTA...\r\n");

    /* Code goes here */
    test_ed25519_verify();

    fettPrintf("(Info)~  vOta: Exitting OTA...\r\n");

    //notify main
    vERROR_IF_EQ(xMainTask, NULL, "vOta: Get handle of <main:task>.");
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS_OTA ,eSetBits);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vOta: Notify <main:task>.");

    vTaskDelete (NULL);
}
