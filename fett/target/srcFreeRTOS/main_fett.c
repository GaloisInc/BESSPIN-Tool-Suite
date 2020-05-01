// This is the main function executed by fett -- It is just a wrapper

#include "fettFreeRTOS.h"

void main_fett (void);
void vMain (void *pvParameters);

TaskHandle_t xMainTask = NULL;
UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.

//This is the entry point function
void main_fett () {

    printf ("\n>>>Beginning of Fett<<<\n");

    BaseType_t funcReturn = xTaskCreate(vMain, "main:vMain", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    prERROR_IF_NEQ(funcReturn, pdPASS, "main_fett: Creating vMain task.");

    vTaskStartScheduler(); //Hang the function
    return;
}

//This is the entry point task
void vMain (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;
    uint32_t recvNotification;
    xMainTask = xTaskGetCurrentTaskHandle();

    fettPrintf("vMain: Main task started...\r\n");

    funcReturn = xTaskCreate(vStartNetwork, "vMain:startNetwork", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vMain: Creating vStartNetwork task.");

    recvNotification = NOTIFY_FAIL;
    funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
    vERROR_IF_NEQ(funcReturn, pdPASS, "vMain: Receive notification from vStartNetwork.");
    vERROR_IF_NEQ(recvNotification, NOTIFY_SUCCESS, "vMain: Expected notification value from vStartNetwork.");

    //Start the FAT filesystem

    //Start the HTTP task
    funcReturn = xTaskCreate(vHttp, "vMain:vHttp", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vMain: Creating vHttp task.");

    //Start the OTA task
    funcReturn = xTaskCreate(vOta, "vMain:vOta", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vMain: Creating vOta task.");

    //Wait for the tasks to finish. This will be clearer as we move forward. Probably we'll just leave it hanging and remove this part.
    uint8_t iNotif = 0, nTasksNotif = 2; //HTTP and OTA
    uint8_t exitCode = 0;
    for (iNotif=0;iNotif<nTasksNotif && exitCode==0;iNotif++) {
        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(120000)); //2 minutes arbitrary value
        vERROR_IF_NEQ(funcReturn, pdPASS, "vMain: Receive state notification.");
        if (recvNotification & NOTIFY_FAIL) { //There is a fail somewhere
            switch (recvNotification) {
                case NOTIFY_FAIL_HTTP : fettPrintf("(Error)~  vMain: Received HTTP fail notification.\r\n");
                                        break;
                case NOTIFY_FAIL_OTA  : fettPrintf("(Error)~  vMain: Received OTA fail notification.\r\n");
                                        break;             
                default               : fettPrintf("(Error)~  vMain: Received unknown fail notification. [notif=%lx]\r\n",recvNotification);
                                        break;       
            }
            exitCode = 1;
        } else if (recvNotification & NOTIFY_SUCCESS) { //Success
            switch (recvNotification) {
                case NOTIFY_SUCCESS_HTTP : fettPrintf("(Success)~  vMain: Received HTTP success notification.\r\n");
                                        break;
                case NOTIFY_SUCCESS_OTA  : fettPrintf("(Success)~  vMain: Received OTA success notification.\r\n");
                                        break;             
                default               : fettPrintf("(Error)~  vMain: Received unknown success notification. [notif=%lx]\r\n",recvNotification);  
                                        exitCode = 1;
                                        break;     
            }
        } else {
            fettPrintf("(Error)~  vMain: Received unexpected notification. [notif=%lx]\r\n",recvNotification);
            exitCode = 1;
        }
    } //for iNotif

    vEXIT(exitCode);
}