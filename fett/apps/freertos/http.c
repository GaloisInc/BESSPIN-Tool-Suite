// This is the main task executed by http

#include "fettFreeRTOS.h"

void vHttp (void *pvParameters);

void vHttp (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;

    fettPrintf("vHttp: Starting HTTP...\r\n");

    /* Code goes here */

    fettPrintf("vHttp: Exitting HTTP...\r\n");

    //notify main
    vERROR_IF_EQ(xMainTask, NULL, "vHttp: Get handle of <main:task>.");
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS_HTTP ,eSetValueWithOverwrite);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vHttp: Notify <main:task>.");

    vTaskDelete (NULL);
}
