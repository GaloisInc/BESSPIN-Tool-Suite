// This is the main function executed by besspin -- It is just a wrapper

#include "besspinFreeRTOS.h"

void main_besspin (void);
void vMain (void *pvParameters);

TaskHandle_t xMainTask = NULL;
UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.

// This is the entry point function
void main_besspin () {

    besspinPrintf ("\n>>>Beginning of Besspin<<<\n");

    startNetwork();

    BaseType_t funcReturn = xTaskCreate(vMain,
                                        "main:vMain",
                                        configMINIMAL_STACK_SIZE * STACKSIZEMUL,
                                        NULL, xMainPriority,
                                        NULL);

    if (funcReturn == pdPASS)
    {
        besspinPrintf ("(Info)~  main_besspin: Creating vMain task OK.\n");
    }
    else
    {
        besspinPrintf ("(Error)~  main_besspin: Creating vMain task.\n");
    }
    return;
}

//This is the entry point task
void vMain (void *pvParameters) {
    (void) pvParameters;
    uint32_t recvNotification;
    BaseType_t funcReturn;
    int r;

    xMainTask = xTaskGetCurrentTaskHandle();

    besspinPrintf("(Info)~  vMain: Main task started...\n");
    besspinPrintf("(Info)~  vMain: Main task initial SHWM is %u\n",
               (uint32_t) uxTaskGetStackHighWaterMark(NULL));

    recvNotification = 0;
    funcReturn = xTaskNotifyWait(0xffffffffUL, 0xffffffffUL, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
    besspinPrintf ("(Info)~  vMain: FIRST notification value is %08x\n", recvNotification);
    ASSERT_OR_DELETE_TASK((funcReturn == pdPASS),
                          "vMain: Receive notification from vStartNetwork.");
    ASSERT_OR_DELETE_TASK((recvNotification == NOTIFY_SUCCESS_NTK),
                          "vMain: Expected notification value from vStartNetwork.");

    besspinPrintf ("\r\n<NTK-READY>\r\n");
    vTaskDelay(pdMS_TO_TICKS(3000)); //give time to the host to ping

    // Initialize WolfSLL - this needs to be done before any other call to
    // any other WolfSSL or Wolfcrypt API
    r = wolfSSL_Init();
    ASSERT_OR_DELETE_TASK((r == SSL_SUCCESS),
                          "main_besspin: Initializing WolfSSL.");

    // Start the FAT filesystem
    funcReturn = ff_init();
    ASSERT_OR_DELETE_TASK((funcReturn == 0),
                          "main_besspin: Initializing FAT filesystem.");

    // Initialize HTTP Assets onto the FAT Filesystem.
    // Note - this is done here, BEFORE starting the HTTP and OTA tasks to avoid
    // a potential race condition between HTTP and OTA both trying to update the
    // same file(s) at the same time.
    Initialize_HTTP_Assets();

    //Start the HTTP task
    funcReturn = xTaskCreate(vHttp, "vMain:vHttp", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    ASSERT_OR_DELETE_TASK((funcReturn == pdPASS),
                          "vMain: Creating vHttp task.");

    //Start the OTA task
    funcReturn = xTaskCreate(vOta, "vMain:vOta", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    ASSERT_OR_DELETE_TASK((funcReturn == pdPASS),
                          "vMain: Creating vOta task.");

    //In dev/test mode, we time-out.
    uint8_t iNotif = 0, nTasksNotif = 2; //HTTP and OTA
    uint8_t exitCode = 0;
    TickType_t xStartTime = xTaskGetTickCount();
    do {
        recvNotification = 0;
        funcReturn = xTaskNotifyWait(0x00000000UL, 0xffffffffUL, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds arbitrary value
        if (funcReturn != pdPASS) {
            //the following should be printed in debug mode only (Not yet implemented)
            besspinPrintf("(Debug)~  vMain: <%d seconds> elapsed with <%d notification(s)> received.\r\n",pdTICKS_TO_S(xTaskGetTickCount() - xStartTime),iNotif);
        } else {
            besspinPrintf ("(Info)~  vMain: notification value is %08x\n", recvNotification);
            if (recvNotification & NOTIFY_FAIL) { //There is a fail somewhere
                if (recvNotification & NOTIFY_FAIL_HTTP) {
                    besspinPrintf("(Error)~  vMain: Received HTTP fail notification.\r\n");
                }
                if (recvNotification & NOTIFY_FAIL_OTA) {
                    besspinPrintf("(Error)~  vMain: Received OTA fail notification.\r\n");
                }

		// Only HTTP or OTA or BOTH should have notified. Any other bit set is an error
		if ((recvNotification & (NOTIFY_FAIL_HTTP | NOTIFY_FAIL_OTA)) != recvNotification) {
                    besspinPrintf("(Error)~  vMain: Received unknown fail notification. [notif=0x%lx]\r\n",recvNotification);
                }
                exitCode = 1;
            } else if (recvNotification & NOTIFY_SUCCESS) { //Success
                if (recvNotification & NOTIFY_SUCCESS_HTTP) {
                    besspinPrintf("(Success)~  vMain: Received HTTP success notification.\r\n");
                    iNotif++;
                }
                if (recvNotification & NOTIFY_SUCCESS_OTA) {
                    besspinPrintf("(Success)~  vMain: Received OTA success notification.\r\n");
                    iNotif++;
                }

		// Only HTTP or OTA or BOTH should have notified. Any other bit set is an error
		if ((recvNotification & (NOTIFY_SUCCESS_HTTP | NOTIFY_SUCCESS_OTA)) != recvNotification) {
                    besspinPrintf("(Error)~  vMain: Received unknown success notification. [notif=0x%lx]\r\n",recvNotification);
                    exitCode = 1;
                }
            } else {
                besspinPrintf("(Error)~  vMain: Received unexpected notification. [notif=0x%lx]\r\n",recvNotification);
                exitCode = 1;
            }
        } //else: notification received
    } while ((iNotif<nTasksNotif) && (exitCode==0));

    if ((exitCode==0) && (iNotif<nTasksNotif)) {
        besspinPrintf("(Error)~  vMain: Missing notifications. [received %d/%d]\r\n",iNotif,nTasksNotif);
        exitCode = 1;
    }

    besspinPrintf("(Info)~  vMain: Main task final SHWM is %u\n",
               (uint32_t) uxTaskGetStackHighWaterMark(NULL));

    exitBesspin(exitCode);
    vTaskDelete(NULL);
}
