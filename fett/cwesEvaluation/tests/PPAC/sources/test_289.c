/*
Test_289: Authentication Bypass by Alternate Name
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
NONE
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

    #define NUM_OF_TEST_PARTS 3 //test_289 has 3 parts

    void vBypassTheForce (void *pvParameters); //used in part 3
    //from extraSources
    extern uint8_t getServicePermission (const char * xActor);

    static void vTask289 (void *pvParameters);
    void main_test_289 (void);

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.
    
    void main (void) {
        BaseType_t funcReturn;

        startNetwork();

        funcReturn = xTaskCreate(vTask289, "main:task289", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task289>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task289>.\n");
        }

        return;
    }

    static void vTask289 (void *pvParameters) {
        (void)pvParameters;
        BaseType_t funcReturn;
        uint32_t recvNotification;
        xMainTask = xTaskGetCurrentTaskHandle();

        // -------------------------------- START NETWORK ------------------------------------------
        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(20000)); //it usually takes 10-15 seconds
        if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
            onPrintf ("<INVALID> [main:] Failed to start network. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
            vEXIT(1);
        } else {
            onPrintf (">>> [main:] Network started successfully!\n");
        }

        onPrintf ("\n<NTK-READY>\n");
        vTaskDelay(pdMS_TO_TICKS(3000)); //give time to the host to ping

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

        // -------------------------------- START TCP listening socket --------------------------------
        uint8_t iPart[2] = {0, 0}; //for compatibility
        funcReturn = xTaskCreate(vServerSocketTCP, "taskTest:serverSocketTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &iPart, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [target-server] Failed to create <taskTest:serverSocketTCP>. [ret=%d].\n",funcReturn);
            vEXIT(1);
        } else {
            onPrintf (">>> Created <taskTest:serverSocketTCP>.\n");
        }

        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
        if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
            onPrintf ("<INVALID> [target-server] Failed to create a listening TCP server socket. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
            vEXIT(1);
        } else {
            onPrintf (">>> A listening TCP socket is opened successfully!\n<TCP-READY>\n");
        }

        // -------------------------------- Host (client) opened a connection --------------------------------
        recvNotification = NOTIFY_FAIL;
        funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(60000)); //60 seconds timeout
        if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
            onPrintf ("<INVALID> [target-server] Failed to connect to the client. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
            vEXIT(1);
        } else if (recvNotification == NOTIFY_INVALIDAUTH) {
            onPrintf ("<INVALID> [target-server]: Failed to authenticate the client.\n");
        } else { 
            onPrintf (">>> The connection with the client established successfully!\n");
        }

        // --------------------- reading the subject CN --------------------------------
        char subjectCN[SUBJECT_CN_BUF_SIZE];
        size_t xBytesReceived = recvFromMsgBuffer ((void *) subjectCN, SUBJECT_CN_BUF_SIZE);
        if (xBytesReceived <= 0) {
            onPrintf ("<INVALID> [target-server]: Failed to obtain the client subject CN. [ret=%d]\n",xBytesReceived);
            vEXIT(1);
        }
        subjectCN[xBytesReceived] = '\0'; //add the null termination

        #if (TESTGEN_TEST_PART == 3) //create a task to do that
            funcReturn = xTaskCreate(vBypassTheForce, "taskTest:bypassTheForce", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &subjectCN, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server] Failed to create <taskTest:bypassTheForce>. [ret=%d].\n",funcReturn);
                vEXIT(1);
            } else {
                onPrintf (">>> Created <taskTest:bypassTheForce>.\n");
            }

            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(5000)); //5 seconds
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-server] Something went wrong with <taskTest:bypassTheForce>. [ret=%d,notf=%lx]\n",funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf (">>> [target-server] BypassTheForce executed successfully!\n");
            }
        #else //parts 1&2
            // ----------------- Get Service permission ------------
            if (getServicePermission(subjectCN) == uTRUE) {
                onPrintf ("<GRANTED> [target-server]: Service request accepted for <%s>\n",subjectCN);
            } else {
                onPrintf ("<DENIED> [target-server]: Service request denied for <%s>\n",subjectCN);
            }
        #endif

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
    } //vTask289

    //This task bypasses the task name blacklist
    void vBypassTheForce (void *pvParameters) {
        BaseType_t funcReturn;
        char * subjectCN = (char *) pvParameters;

        onPrintf ("\t>>>>>>[bypassTheForce]: Requesting service permission.\n");
        // ----------------- Get Service permission ------------
        if (getServicePermission(subjectCN) == uTRUE) {
            onPrintf ("<GRANTED> [bypassTheForce]: Service request accepted for <%s>\n",subjectCN);
        } else {
            onPrintf ("<DENIED> [bypassTheForce]: Service request denied for <%s>\n",subjectCN);
        }

        funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> [bypassTheForce]: Failed to notify <main:task>!\n");
            vEXIT(1);
        }

        vTaskDelete(NULL);
    }

//---------------- Debian test ------------------------------------------------------
#elif defined(testgenOnDebian) || defined(testgenOnFreeBSD)

    #define THIS_TEST "289"

    #define PAM_PREFIX "pam_"
    #define MY_CONFIG PAM_PREFIX THIS_TEST

    #include <sys/types.h>
    #include <pwd.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <security/pam_appl.h>

    #include <errno.h>
    #include <string.h>
    #include <unistd.h>

#ifdef testgenOnDebian
    #include <security/pam_misc.h>
    static struct pam_conv conv = { misc_conv, NULL };
#else //FreeBSD
    #include <security/openpam.h>
    static struct pam_conv conv = { openpam_ttyconv, NULL };
#endif

    int main () {

        pam_handle_t *pamh;
        int pamReturn;
        struct passwd *pw;

        pw = getpwuid(getuid());
        if (pw == NULL) {
            printf ("<INVALID> Failed to run getpwuid. (ERRNO.name=%s)\n",strerror(errno));
            return 1;
        }
        else {
            printf (">>> getpwuid executed successfully.\n");
        }

        pamReturn = pam_start(MY_CONFIG, pw->pw_name, &conv, &pamh);
        printf("Auth for %s\r\n", pw->pw_name);
        if (pamReturn == PAM_SUCCESS) {
            printf (">>> PAM started successfully.\n");
        }
        else {
            printf ("<INVALID> Failed to start PAM. (pamReturn=%d).\n",pamReturn);
            return 1;
        }

        pamReturn = pam_authenticate(pamh, 0);
        if (pamReturn == PAM_SUCCESS) {
            printf ("<GRANTED> authentication successful.\n");
        }
        else {
            printf ("<DENIED> Failed to authenticate. (pamReturn=%d).\n",pamReturn);
            return 1;
        }

        pamReturn = pam_end(pamh, PAM_SUCCESS);
        if (pamReturn == PAM_SUCCESS) {
            printf (">>> PAM ended successfully.\n");
        }
        else {
            printf ("<INVALID> Failed to end PAM. (pamReturn=%d).\n",pamReturn);
            return 1;
        }

        return 0;

    }
#endif //end of if FreeRTOS
