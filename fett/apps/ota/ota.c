// This is the main task executed by ota

#include "fettFreeRTOS.h"

void vOta (void *pvParameters);

void vOta (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;
    uint32_t recvNotification;
    xMainTask = xTaskGetCurrentTaskHandle();

    fettPrintf ("vOTA: Starting OTA...\r\n");

    funcReturn = xTaskCreate(vStartNetwork, "vOta:startNetwork", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vOta: Creating vStartNetwork task.");

    recvNotification = NOTIFY_FAIL;
    funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
    vERROR_IF_NEQ(funcReturn, pdPASS, "vOta: Receive notification from vStartNetwork.");
    vERROR_IF_NEQ(recvNotification, NOTIFY_SUCCESS, "vOta: Expected notification value from vStartNetwork.");

    vEXIT(0);
}
