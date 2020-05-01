// This is the main task executed by https

#include "fettFreeRTOS.h"

void vHttps (void *pvParameters);

void vHttps (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;
    uint32_t recvNotification;
    xMainTask = xTaskGetCurrentTaskHandle();

    fettPrintf("vHTTPS: Starting HTTPS...\r\n");

    funcReturn = xTaskCreate(vStartNetwork, "vHttps:startNetwork", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vHttps: Creating vStartNetwork task.");

    recvNotification = NOTIFY_FAIL;
    funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
    vERROR_IF_NEQ(funcReturn, pdPASS, "vHttps: Receive notification from vStartNetwork.");
    vERROR_IF_NEQ(recvNotification, NOTIFY_SUCCESS, "vHttps: Expected notification value from vStartNetwork.");

    vEXIT(0);
}
