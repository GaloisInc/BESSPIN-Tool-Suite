// This is the main function executed by fett -- It is just a wrapper

#include "fettFreeRTOS.h"

void main_fett (void);
void vMain (void *pvParameters);

TaskHandle_t xMainTask = NULL;
UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.

// This is the entry point function
void main_fett () {

    fettPrintf ("\n>>>Beginning of Fett<<<\n");

    BaseType_t funcReturn = xTaskCreate(vMain,
                                        "main:vMain",
                                        configMINIMAL_STACK_SIZE * STACKSIZEMUL,
                                        NULL, xMainPriority,
                                        NULL);

    if (funcReturn == pdPASS)
    {
        fettPrintf ("(Info)~  main_fett: Creating vMain task OK.");
    }
    else
    {
        fettPrintf ("(Error)~  main_fett: Creating vMain task.");
    }
    return;
}

//This is the entry point task
void vMain (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;
    uint32_t recvNotification;
    int r;

    xMainTask = xTaskGetCurrentTaskHandle();

    fettPrintf("vMain: Main task started...\r\n");

    // Start the network task to configure the network before the hook -- has to be the first thing
    funcReturn = xTaskCreate(vStartNetwork, "vMain:startNetwork", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    ASSERT_OR_DELETE_TASK((funcReturn == pdPASS),
                          "vMain: Creating vStartNetwork task.");

    funcReturn = xTaskNotifyWait(0xffffffff, 0xffffffff, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
    ASSERT_OR_DELETE_TASK((funcReturn == pdPASS),
                          "vMain: Receive notification from vStartNetwork.");
    ASSERT_OR_DELETE_TASK((recvNotification == NOTIFY_SUCCESS_NTK),
                          "vMain: Expected notification value from vStartNetwork.");

    // Initialize WolfSLL - this needs to be done before any other call to
    // any other WolfSSL or Wolfcrypt API
    r = wolfSSL_Init();
    ASSERT_OR_DELETE_TASK((r == SSL_SUCCESS),
                          "main_fett: Initializing WolfSSL.");

    // Start the FAT filesystem
    funcReturn = ff_init();
    ASSERT_OR_DELETE_TASK((funcReturn == 0),
                          "main_fett: Initializing FAT filesystem.");

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
        funcReturn = xTaskNotifyWait(0x00000000, 0xffffffff, &recvNotification, pdMS_TO_TICKS(30000)); //30 seconds arbitrary value
        if (funcReturn != pdPASS) {
            //the following should be printed in debug mode only (Not yet implemented)
            fettPrintf("(Debug)~  vMain: <%d seconds> elapsed with <%d notification(s)> received.\r\n",pdTICKS_TO_S(xTaskGetTickCount() - xStartTime),iNotif);
        } else {
            if (recvNotification & NOTIFY_FAIL) { //There is a fail somewhere
                if (recvNotification & NOTIFY_FAIL_HTTP) {
                    fettPrintf("(Error)~  vMain: Received HTTP fail notification.\r\n");
                }
                if (recvNotification & NOTIFY_FAIL_OTA) {
                    fettPrintf("(Error)~  vMain: Received OTA fail notification.\r\n");
                }
                if (!(recvNotification & NOTIFY_FAIL_HTTP) && !(recvNotification & NOTIFY_FAIL_OTA)) {
                    fettPrintf("(Error)~  vMain: Received unknown fail notification. [notif=0x%lx]\r\n",recvNotification);
                }
                exitCode = 1;
            } else if (recvNotification & NOTIFY_SUCCESS) { //Success
                if (recvNotification & NOTIFY_SUCCESS_HTTP) {
                    fettPrintf("(Success)~  vMain: Received HTTP success notification.\r\n");
                    iNotif++;
                }
                if (recvNotification & NOTIFY_SUCCESS_OTA) {
                    fettPrintf("(Success)~  vMain: Received OTA success notification.\r\n");
                    iNotif++;
                }
                if (!(recvNotification & NOTIFY_SUCCESS_HTTP) && !(recvNotification & NOTIFY_SUCCESS_OTA)) {
                    fettPrintf("(Error)~  vMain: Received unknown success notification. [notif=0x%lx]\r\n",recvNotification);
                    exitCode = 1;
                }
            } else {
                fettPrintf("(Error)~  vMain: Received unexpected notification. [notif=0x%lx]\r\n",recvNotification);
                exitCode = 1;
            }
        } //else: notification received
    } while ((iNotif<nTasksNotif) && (exitCode==0));

    if ((exitCode==0) && (iNotif<nTasksNotif)) {
        fettPrintf("(Error)~  vMain: Missing notifications. [received %d/%d]\r\n",iNotif,nTasksNotif);
        exitCode = 1;
    }
    exitFett(exitCode);
    vTaskDelete(NULL);
}
