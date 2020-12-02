/*
Test_307: Improper Restriction of Excessive Authentication Attempts
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
    nAllowedAuthAttempts: number of allowed auth attempts before blocking
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

    #define NUM_OF_TEST_PARTS 2 //test_307 has 2 parts
    
    static void vTask307 (void *pvParameters);
    void main_test_307 (void);

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily
    
    void main (void) {
        BaseType_t funcReturn;

        startNetwork();

        funcReturn = xTaskCreate(vTask307, "main:task307", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task307>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task307>.\n");
        }

        return;
    }

    static void vTask307 (void *pvParameters) {
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

        uint8_t iSubPart;
        const char subPartNames[3][4] = {"1", "N", "N+1"};
        
        #if TESTGEN_TEST_PART==1
        //--------------------------------------------------------------------------------------------
        onPrintf ("\n\n--------------------Part01: Host is client and target is server--------------------\n\n");
        for (iSubPart=0; iSubPart<3; iSubPart++) {
            onPrintf ("\n----- <authForNofAttempts(%s)> -----\n",subPartNames[iSubPart]);

            #ifdef USE_TLS_OVER_TCP 
                // ------------------------------- START WOLFSSL -------------------------------------------
                funcReturn = (BaseType_t) startWolfSSL();
                if (funcReturn != 0) {
                    onPrintf ("<INVALID> [target-server-%d] Failed to start WolfSSL. [ret=%d]\n",iSubPart,funcReturn);
                    vEXIT(1);
                } else {
                    onPrintf ("[%d]>>> WolfSSL started successfully!\n",iSubPart);
                }

                // ------------------------------- INIT WOLFSSL SERVER  -------------------------------------
                funcReturn = xTaskCreate(vInitServerWolfSSL, "taskTest:initServerWolfSSL", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
                if (funcReturn != pdPASS) {
                    onPrintf ("<INVALID> [target-server-%d] Failed to create <taskTest:initServerWolfSSL>. [ret=%d].\n",iSubPart,funcReturn);
                    vEXIT(1);
                } else {
                    onPrintf ("[%d]>>> Created <taskTest:initServerWolfSSL>.\n",iSubPart);
                }

                recvNotification = NOTIFY_FAIL;
                funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
                if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                    onPrintf ("<INVALID> [target-server-%d] Failed to initialize WolfSSL server. [ret=%d,notf=%lx]\n",iSubPart,funcReturn,recvNotification);
                    vEXIT(1);
                } else {
                    onPrintf ("[%d]>>> WolfSSL server initialization successful!\n",iSubPart);
                }
            #endif

            // -------------------------------- START TCP listening socket --------------------------------
            uint8_t iPart[2] = {iSubPart, 0}; //0 is the added constant to the port -- nothing to add
            funcReturn = xTaskCreate(vServerSocketTCP, "taskTest:serverSocketTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &iPart, xMainPriority, NULL);
            if (funcReturn != pdPASS) {
                onPrintf ("<INVALID> [target-server-%d] Failed to create <taskTest:serverSocketTCP>. [ret=%d].\n",iSubPart,funcReturn);
                vEXIT(1);
            } else {
                onPrintf ("[%d]>>> Created <taskTest:serverSocketTCP>.\n",iSubPart);
            }

            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
            if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                onPrintf ("<INVALID> [target-server-%d] Failed to create a listening TCP server socket. [ret=%d,notf=%lx]\n",iSubPart,funcReturn,recvNotification);
                vEXIT(1);
            } else {
                onPrintf ("[%d]>>> A listening TCP socket is opened successfully!\n<TCP-READY>\n",iSubPart);
            }

            // -------------------------------- Host (client) opened a connection --------------------------------
            recvNotification = NOTIFY_FAIL;
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(90000)); //90 seconds timeout
            if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
                onPrintf ("<INVALID> [target-server-%d] Failed to connect to the client. [ret=%d,notf=%lx]\n",iSubPart,funcReturn,recvNotification);
                vEXIT(1);
            } else if (recvNotification == NOTIFY_INVALIDAUTH) {
                onPrintf ("<DENIED> [target-server-%d]: Failed to authenticate the client.\n\n",iSubPart);
            } else { 
                onPrintf ("[%d]>>> The connection with the client established successfully!\n",iSubPart);
            }
            
            #ifdef USE_TLS_OVER_TCP 
                // ------------------------------- END WOLFSSL -----------------------------------
                funcReturn = xTaskCreate(vEndWolfSSL, "taskTest:endWolfSSL", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
                if (funcReturn != pdPASS) {
                    onPrintf ("<INVALID> [target-server-%d] Failed to create <taskTest:endWolfSSL>. [ret=%d].\n",iSubPart,funcReturn);
                    vEXIT(1);
                } else {
                    onPrintf ("[%d]>>> Created <taskTest:endtWolfSSL>.\n",iSubPart);
                }

                recvNotification = NOTIFY_FAIL;
                funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
                if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                    onPrintf ("<INVALID> [target-server-%d] Failed to end WolfSSL. [ret=%d,notf=%lx]\n",iSubPart,funcReturn,recvNotification);
                    vEXIT(1);
                } else {
                    onPrintf ("[%d]>>> WolfSSL terminated successfully!\n",iSubPart);
                }
            #endif

            vTaskDelay (pdMS_TO_TICKS(1000)); //1 second -- take a breather
        } //for iSubPart (3 times)

        #elif TESTGEN_TEST_PART==2
        //--------------------------------------------------------------------------------------------
        onPrintf ("\n\n--------------------Part02: Host is server and target is client--------------------\n\n");
        uint8_t actualNAttempts[3] = {1, nAllowedAuthAttempts, nAllowedAuthAttempts+1};
        for (iSubPart=0; iSubPart<3; iSubPart++) {
            onPrintf ("\n----- <authForNofAttempts(%s)> -----\n",subPartNames[iSubPart]);
            uint8_t iAttempt=0;
            uint8_t isGranted = uFALSE;
            while ((iAttempt<actualNAttempts[iSubPart]) && (isGranted == uFALSE)) {
                #ifdef USE_TLS_OVER_TCP 
                    // ------------------------------- START WOLFSSL -------------------------------------------
                    funcReturn = (BaseType_t) startWolfSSL();
                    if (funcReturn != 0) {
                        onPrintf ("<INVALID> [target-client-%d.%d] Failed to start WolfSSL. [ret=%d]\n",iSubPart,iAttempt,funcReturn);
                        vEXIT(1);
                    } else {
                        onPrintf ("[%d.%d]>>> WolfSSL started successfully!\n",iSubPart,iAttempt);
                    }

                    // ------------------------------- INIT WOLFSSL CLIENT  -------------------------------------
                    uint8_t isThisTheLastOne = (iAttempt == actualNAttempts[iSubPart]-1);
                    funcReturn = xTaskCreate(vInitClientWolfSSL, "taskTest:initClientWolfSSL", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &isThisTheLastOne, xMainPriority, NULL);
                    if (funcReturn != pdPASS) {
                        onPrintf ("<INVALID> [target-client-%d.%d] Failed to create <taskTest:initClientWolfSSL>. [ret=%d].\n",iSubPart,iAttempt,funcReturn);
                        vEXIT(1);
                    } else {
                        onPrintf ("[%d.%d]>>> Created <taskTest:initClientWolfSSL>.\n",iSubPart,iAttempt);
                    }

                    recvNotification = NOTIFY_FAIL;
                    funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
                    if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                        onPrintf ("<INVALID> [target-client-%d.%d] Failed to initialize WolfSSL client. [ret=%d,notf=%lx]\n",iSubPart,iAttempt,funcReturn,recvNotification);
                        vEXIT(1);
                    } else {
                        onPrintf ("[%d.%d]>>> WolfSSL client initialization successful!\n",iSubPart,iAttempt);
                    }
                #endif    

                // -------------------------------- START TCP client socket --------------------------------
                uint8_t iPart[3] = {iSubPart, iAttempt, 3}; //3 is the added constant to the port for 3 subparts of P01 
                funcReturn = xTaskCreate(vClientSocketTCP, "taskTest:clientSocketTCP", configMINIMAL_STACK_SIZE * STACKSIZEMUL, (void *) &iPart, xMainPriority, NULL);
                if (funcReturn != pdPASS) {
                    onPrintf ("<INVALID> [target-client-%d.%d] Failed to create <taskTest:clientSocketTCP>. [ret=%d].\n",iSubPart,iAttempt,funcReturn);
                    vEXIT(1);
                } else {
                    onPrintf ("[%d.%d]>>> Created <taskTest:clientSocketTCP>.\n",iSubPart,iAttempt);
                }

                recvNotification = NOTIFY_FAIL;
                funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(60000)); //60 seconds timeout
                if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
                    onPrintf ("<INVALID> [target-client-%d.%d] Failed to connect to the server. [ret=%d,notf=%lx]\n",iSubPart,iAttempt,funcReturn,recvNotification);
                    vEXIT(1);
                } else if (recvNotification == NOTIFY_INVALIDAUTH) {
                    onPrintf ("<DENIED> [target-client-%d.%d]: Failed to authenticate the server.\n\n",iSubPart,iAttempt);
                    //try again ...
                } else { 
                    onPrintf ("[%d.%d]>>> The connection with the server established successfully!\n",iSubPart,iAttempt);
                    isGranted = uTRUE; //break
                }        

                #ifdef USE_TLS_OVER_TCP 
                    // ------------------------------- END WOLFSSL -----------------------------------
                    funcReturn = xTaskCreate(vEndWolfSSL, "taskTest:endWolfSSL", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
                    if (funcReturn != pdPASS) {
                        onPrintf ("<INVALID> [target-client-%d.%d] Failed to create <taskTest:endWolfSSL>. [ret=%d].\n",iSubPart,iAttempt,funcReturn);
                        vEXIT(1);
                    } else {
                        onPrintf ("[%d.%d]>>> Created <taskTest:endtWolfSSL>.\n",iSubPart,iAttempt);
                    }

                    recvNotification = NOTIFY_FAIL;
                    funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(10000)); //10 seconds timeout
                    if ((funcReturn != pdPASS) || (recvNotification != NOTIFY_SUCCESS)) {
                        onPrintf ("<INVALID> [target-client-%d.%d] Failed to end WolfSSL. [ret=%d,notf=%lx]\n",iSubPart,iAttempt,funcReturn,recvNotification);
                        vEXIT(1);
                    } else {
                        onPrintf ("[%d.%d]>>> WolfSSL terminated successfully!\n",iSubPart,iAttempt);
                    }
                #endif
                iAttempt++;
            } //for each subPart, do this for the right amount
        } //for iSubPart (3 times)
        #endif

        vEXIT(0);
    }

//---------------- Debian test ------------------------------------------------------
#elif defined(testgenOnDebian)
    #define THIS_TEST "307"
    #define PAM_PREFIX "pam_"
    #define MY_CONFIG PAM_PREFIX THIS_TEST

    #include <sys/types.h>
    #include <pwd.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <security/pam_appl.h>
    #include <security/pam_misc.h>

    #include <errno.h>
    #include <string.h>
    #include <unistd.h>

    static struct pam_conv conv = { misc_conv, NULL };

    int main() {

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

#elif defined(testgenOnFreeBSD)

    #define THIS_TEST "307"

    #include <stdio.h>

    int main () {
        printf (">>> This test is fully bash interactive.\n");
        return 0;
    }

#endif //end of if FreeRTOS