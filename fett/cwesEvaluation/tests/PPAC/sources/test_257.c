/*
Test_257: Authentication Bypass by Spoofing
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
NONE
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

     #define NUM_OF_TEST_PARTS 3 //test_257 has 3 parts

    static void vTask257 (void *pvParameters);
    void main_test_257 (void);

    //Extra functions needed
    uint8_t getServicePermission (const char * xActor, const char * inPW);

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.
    
    void main (void) {
        BaseType_t funcReturn;
        funcReturn = xTaskCreate(vTask257, "main:task257", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task257>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task257>.\n");
        }

        vTaskStartScheduler(); //Hang the function
        return;
    }

    static void vTask257 (void *pvParameters) {
        (void)pvParameters;
        BaseType_t funcReturn;
        uint32_t recvNotification;
        xMainTask = xTaskGetCurrentTaskHandle();

        // -------------------------------- START NETWORK ------------------------------------------
        funcReturn = xTaskCreate(vStartNetwork, "taskTest:startNetwork", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [main:] Failed to create <taskTest:startNetwork>. [ret=%d].\n",funcReturn);
            vEXIT(1);
        } else {
            onPrintf (">>> [main:] Created <taskTest:startNetwork>.\n");
        }

        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
        if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
            onPrintf ("<INVALID> [main:] Failed to start network. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
            vEXIT(1);
        } else {
            onPrintf (">>> [main:] Network started successfully!\n");
        }

        #ifdef USE_TLS_OVER_TCP 
            // ------------------------------- START WOLFSSL -------------------------------------------
            funcReturn = (BaseType_t) startWolfSSL();
            if (funcReturn != 0) {
                onPrintf ("<INVALID> [target-server] Failed to start WolfSSL. [ret=%d]\n",funcReturn);
                vEXIT(1);
            } else {
                onPrintf (">>> WolfSSL started successfully!\n");
            }

            // ------------------------------- INIT WOLFSSL SERVER  -------------------------------------
            funcReturn = xTaskCreate(vInitServerWolfSSL, "taskTest:initServerWolfSSL", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server] Failed to create <taskTest:initServerWolfSSL>. [ret=%d].\n",funcReturn);
                vEXIT(1);
            } else {
                onPrintf (">>> Created <taskTest:initServerWolfSSL>.\n");
            }

            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-server] Failed to initialize WolfSSL server. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf (">>> WolfSSL server initialization successful!\n");
            }
        #endif

        for (int iAttempt=0; iAttempt<2; iAttempt++) { //just try twice

            // -------------------------------- START TCP listening socket --------------------------------
            uint8_t iPart[2] = {iAttempt, 0};
            funcReturn = xTaskCreate(vServerSocketTCP, "taskTest:serverSocketTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &iPart, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server-%d] Failed to create <taskTest:serverSocketTCP>. [ret=%d].\n",iAttempt,funcReturn);
                vEXIT(1);
            } else {
                onPrintf ("[%d]>>> Created <taskTest:serverSocketTCP>.\n",iAttempt);
            }

            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-server-%d] Failed to create a listening TCP server socket. [ret=%d,notf=%lx]\n",iAttempt,funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf ("[%d]>>> A listening TCP socket is opened successfully!\n<TCP-READY>\n",iAttempt);
            }

            // -------------------------------- CommunicateTCP is ready for the reply --------------------------------
            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(30000)); //30 seconds timeout
            if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_SUCCESS))) {
                onPrintf ("<INVALID> [target-server-%d] Failed to receive request. [ret=%d,notf=%lx]\n",iAttempt,funcReturn,recvNotification);
                vEXIT(1);
            } else { 
                onPrintf ("[%d]>>> Request received!\n",iAttempt);
            }

            // --------------------- reading the subject CN (username) --------------------------------
            char subjectCN[SUBJECT_CN_BUF_SIZE];
            size_t xBytesReceived = recvFromMsgBuffer ((void *) subjectCN, SUBJECT_CN_BUF_SIZE);
            if (xBytesReceived <= 0) {
                onPrintf ("<INVALID> [target-server-%d]: Failed to obtain the client subject CN. [ret=%d]\n",iAttempt,xBytesReceived);
                vEXIT(1);
            }
            subjectCN[xBytesReceived] = '\0'; //add the null termination

            // --------------------- Read the password --------------------------------
            char inPW[PW_SIZE];            
            xBytesReceived = recvFromMsgBuffer ((void *) inPW, PW_SIZE);
            if (xBytesReceived <= 0) {
                onPrintf ("<INVALID> [target-server-%d]: Failed to obtain the client's password. [ret=%d]\n",iAttempt,xBytesReceived);
                vEXIT(1);
            }
            inPW[xBytesReceived] = '\0'; //add the null termination

            // --------------------- Read the task handle --------------------------------
            TaskHandle_t xCommunicateTask;
            xBytesReceived = recvFromMsgBuffer ((void *) &xCommunicateTask, sizeof(TaskHandle_t *));
            if (xBytesReceived <= 0) {
                onPrintf ("<INVALID> [target-server-%d]: Failed to obtain the xCommunicateTask handle. [ret=%d]\n",iAttempt,xBytesReceived);
                vEXIT(1);
            }

            // --------------------- Get Service permission ------------------
            char replyToClient[8]; 
            if (getServicePermission(subjectCN,inPW) == uTRUE) {
                onPrintf ("<GRANTED> [target-server-%d]: Service request accepted for <%s>\n",iAttempt,subjectCN);
                strcpy (replyToClient,"GRANTED");
            } else {
                onPrintf ("<DENIED> [target-server-%d]: Service request denied for <%s>\n",iAttempt,subjectCN);
                strcpy (replyToClient,"DENIED");
            }

            // --------------------- Reply message to the client ---------------------
            funcReturn = sendToMsgBuffer ((void *) replyToClient, strlen(replyToClient));
            if (funcReturn == uTRUE) {
                onPrintf ("[%d]>>> Reply sent to msgBuf.\n",iAttempt);
            } else {
                onPrintf ("<INVALID> [target-server-%d]: Failed to send reply to msgBuf.\n",iAttempt);
                vEXIT(1);
            }

            // --------------------- Notify the xCommunicateTask --------------------------------
            funcReturn = xTaskNotify( xCommunicateTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server-%d]: Failed to notify <xCommunicateTask>!\n",iAttempt);
                vEXIT(1);
            }

            // -------------------------------- Host (client) opened a connection --------------------------------
            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(60000)); //60 seconds timeout
            if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
                onPrintf ("<INVALID> [target-server-%d] Failed to connect to the client. [ret=%d,notf=%lx]\n",iAttempt,funcReturn,recvNotification);
                vEXIT(1);
            } else if (recvNotification == NOTIFY_INVALIDAUTH) {
                onPrintf ("<INVALID> [target-server-%d]: Failed to authenticate the client.\n",iAttempt);
                vEXIT(1);
            } else { 
                onPrintf ("[%d]>>> The connection with the client established successfully!\n",iAttempt);
            }
        } // end of attempts

        #ifdef USE_TLS_OVER_TCP 
            // ------------------------------- END WOLFSSL -----------------------------------
            funcReturn = xTaskCreate(vEndWolfSSL, "taskTest:endWolfSSL", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server] Failed to create <taskTest:endWolfSSL>. [ret=%d].\n",funcReturn);
                vEXIT(1);
            } else {
                onPrintf (">>> Created <taskTest:endtWolfSSL>.\n");
            }

            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-server] Failed to end WolfSSL. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf (">>> WolfSSL terminated successfully!\n");
            }
        #endif

        vEXIT(0);
    } //vTask257


//---------------- Debian and FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))
#include <sys/types.h>
#include <security/pam_appl.h>
#include <security/pam_misc.h>
#ifdef testgenOnFreeBSD
#include <security/openpam.h>
#endif
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <pwd.h>

char *old_password;

char *NEW_PASSWORD = "NotMyOldPassword";

int my_conv(int num_msg,
            const struct pam_message **msg,
            struct pam_response **resp, void *appdata_ptr)
{
    printf("my_conv\n");
    struct pam_response *ret_resp = calloc(num_msg, sizeof(*ret_resp));
    for(int idx = 0; idx < num_msg; idx++) {
        printf("<%s>\n\n", msg[idx]->msg);
        if (strstr(msg[idx]->msg, "New Password:") ||
            strstr(msg[idx]->msg, "new password:") ||
            strstr(msg[idx]->msg, "New password:")) {
            // Different flavors of (Retype) new password for Linux/FreeBSD
            ret_resp[idx].resp = strdup(NEW_PASSWORD);
            ret_resp[idx].resp_retcode = 0;
            printf(" >>> Entered new password <%s>\n", ret_resp[idx].resp);
        }
        else if (strstr(msg[idx]->msg, "Password:")) {
            ret_resp[idx].resp = strdup(old_password);
            ret_resp[idx].resp_retcode = 0;
            printf(" >>> Old password is <%s>\n", ret_resp[idx].resp);
        }
    }
    printf("my_conv done\n");
    *resp = ret_resp;
    return PAM_SUCCESS;
}

int main(int argc, char **argv)
{
    pam_handle_t *pamh = NULL;
    struct pam_conv conv = { my_conv, NULL };
    int ok;
    old_password = strdup(argv[2]);
    struct passwd *pw;

    pw = getpwuid(getuid());
    if (pw == NULL) {
        printf ("<INVALID> Failed to run getpwuid. (ERRNO.name=%s)\n",strerror(errno));
        return 1;
    }
    else {
        printf (">>> getpwuid executed successfully.\n");
    }

    ok = pam_start("login", argv[1], &conv, &pamh);
    if (ok != PAM_SUCCESS) {
        printf("<INVALID> pam_start failed [%s]\n",
               pam_strerror(pamh, ok));
        return 1;
    }

    ok = pam_authenticate(pamh, 0);
    if (ok != PAM_SUCCESS) {
        printf("<INVALID> pam_authenticate failed [%s]\n",
               pam_strerror(pamh, ok));
        return 1;
    }

    ok = pam_acct_mgmt(pamh, 0);
    if (ok != PAM_SUCCESS) {
        printf("<INVALID> pam_acct_mgmt failed [%s]\n",
               pam_strerror(pamh, ok));
        return 1;
    }

    ok = pam_chauthtok(pamh, ok);
    if (ok != PAM_SUCCESS) {
        printf("<DENIED> pam_chauthtok failed [%s]\n",
               pam_strerror(pamh, ok));
        return 1;
    }

    pam_end(pamh, ok);
}
#endif //end of if FreeRTOS
