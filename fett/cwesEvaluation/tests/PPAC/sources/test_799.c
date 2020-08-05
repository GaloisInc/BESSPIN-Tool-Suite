/*
Test_799: Improper Control of Interaction Frequency
*/

#include "testsParameters.h"

/* Parameters used from testsParameters.h:
nAllowedInteractions
*/

#ifdef testgenOnFreeRTOS
//---------------- FreeRTOS test ------------------------------------------------------

    #include "testgenFreeRTOS.h"

    #define NUM_OF_TEST_PARTS 3 //test_799 has 3 parts
    #define SUBJECT_CN_BUF_SIZE 20

    //from extraSources
    extern uint8_t getServicePermission (const char * xActor);
    #if TESTGEN_TEST_PART == 2
        extern SemaphoreHandle_t getSemphrHandle (const char * xActor);
    #endif
    #if TESTGEN_TEST_PART == 3
        extern struct actorSemphrPair * requestsLL;
    #endif

    static void vTask799 (void *pvParameters);
    void main_test_799 (void);

    TaskHandle_t xMainTask = NULL;
    UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.
    
    void main (void) {
        BaseType_t funcReturn;
        funcReturn = xTaskCreate(vTask799, "main:task799", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
        if (funcReturn != pdPASS) {
            onPrintf ("<INVALID> Failed to create <main:task799>. [ret=%d].\n",funcReturn);
            return;
        } else {
            onPrintf (">>> [main:] Created <main:task799>.\n");
        }

        vTaskStartScheduler(); //Hang the function
        return;
    }

    static void vTask799 (void *pvParameters) {
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

        uint8_t iSubPart;
        for (iSubPart=0; iSubPart<nAllowedInteractions+1; iSubPart++) { //go until N+1
            onPrintf ("\n----- <request(N%+d)> -----\n",iSubPart-nAllowedInteractions+1);

            // -------------------------------- START TCP listening socket --------------------------------
            uint8_t iPart[2] = {iSubPart, 0}; //0 is the extra added constant to the port -- nothing to add
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
            funcReturn = xTaskNotifyWait(0xffffffff, 0, &recvNotification, pdMS_TO_TICKS(80000)); //80 seconds timeout
            if ((funcReturn != pdPASS) || ((recvNotification != NOTIFY_CONNECTED) && (recvNotification != NOTIFY_INVALIDAUTH))) {
                onPrintf ("<INVALID> [target-server-%d] Failed to connect to the client. [ret=%d,notf=%lx]\n",iSubPart,funcReturn,recvNotification);
                vEXIT(1);
            } else if (recvNotification == NOTIFY_INVALIDAUTH) {
                onPrintf ("<INVALID> [target-server-%d]: Failed to authenticate the client.\n",iSubPart);
            } else { 
                onPrintf ("[%d]>>> The connection with the client established successfully!\n",iSubPart);
            }

            // --------------------- reading the subject CN --------------------------------
            char subjectCN[SUBJECT_CN_BUF_SIZE];
            size_t xBytesReceived = recvFromMsgBuffer ((void *) subjectCN, SUBJECT_CN_BUF_SIZE);
            if (xBytesReceived <= 0) {
                onPrintf ("<INVALID> [target-server-%d]: Failed to obtain the client subject CN. [ret=%d]\n",iSubPart,xBytesReceived);
                vEXIT(1);
            }
            subjectCN[xBytesReceived] = '\0'; //add the null termination

            if (getServicePermission(subjectCN) == uTRUE) {
                onPrintf ("<GRANTED> [target-server-%d]: Service request accepted for <%s>\n",iSubPart,subjectCN);
            } else {
                onPrintf ("<DENIED> [target-server-%d]: Service request denied for <%s>\n",iSubPart,subjectCN);
            }

            #if TESTGEN_TEST_PART == 2
                if (iSubPart==nAllowedInteractions-1) { //before the breaching subpart
                    SemaphoreHandle_t xSemphr = getSemphrHandle (subjectCN);
                    if (xSemphr == NULL) {
                        onPrintf ("<DENIED> [target-server-%d]: Failed to get the semaphore handle for <%s>\n",iSubPart,subjectCN);
                        continue;
                    } else {
                        onPrintf ("<BREACHED-HANDLE> [target-server-%d]: Obtained the semaphore handle!\n",iSubPart);
                    }
                    if (xSemaphoreGive(xSemphr) != pdTRUE) {
                        onPrintf ("<DENIED> [target-server-%d]: Failed to give a token to the semaphore for <%s>\n",iSubPart,subjectCN);
                    } else {
                        onPrintf ("<BREACHED-TOKEN> [target-server-%d]: Token granted to the semaphore!\n",iSubPart);
                    }
                }
            #endif //part-2

            #if TESTGEN_TEST_PART == 3
                if (iSubPart==nAllowedInteractions-1) { //before the breaching subpart
                    if (requestsLL == NULL) {
                        onPrintf ("<DENIED> [target-server-%d]: Failed to get the structure pointer.\n",iSubPart);
                    } else {
                        onPrintf ("<BREACHED-STRUCT> [target-server-%d]: Got the structure pointer!\n",iSubPart);
                        requestsLL = NULL; //that's bad
                    }
                }
            #endif //part-3

        } //for subParts

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
        
        vEXIT(0);
    } //vTask799


//---------------- Debian test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

    #define THIS_TEST "799"

    #define PAM_PREFIX "pam_"
    #define MY_CONFIG PAM_PREFIX THIS_TEST
    
    //special for this test
    #define qUSER_MSGLEN 2 //one character + null termination ==> represents a token
    #define qROOT_MSGLEN 32 //current limit of user name length = 32 
    #define qTimeout 30 //timeout to finish the program if nothing happens

    #include <sys/types.h>
    #include <pwd.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <security/pam_appl.h>

    #include <fcntl.h>
    #include <sys/stat.h>
    #include <time.h>
    #include <mqueue.h>

    #include <errno.h>
    #include <string.h>
    #include <unistd.h>

    #ifdef testgenOnDebian
        #include <security/pam_misc.h>
        static struct pam_conv conv = { misc_conv, NULL };
    #else //FreeBSD
        #include <security/openpam.h>
        static struct pam_conv conv; //no need for tty
    #endif

    //root queue name
    const char * qNameRoot = "/Qroot"; //has to start with a forward slash. <This name is used in cweTests.py too>

    //functions declarations
    int main (int argc, char *argv[]);
    static void cleanQueue (int option, mqd_t qd, const char * qName);
    static int test799OnRoot (int argc);
    static int shutdownRootQueue ();
    static int test799OnUser (int option, const char * userName);

    //This function {close, unlink} the given queue
    static void cleanQueue (int option, mqd_t qd, const char * qName) {
        //option: bit0-> close? , bit1-> unlink?
        if (option&1) { //close
            int retMq = mq_close (qd);
            printf (">>> Closing <%s> queue. (return=%d).\n",qName,retMq);
        }
        if (option&2) { //unlink
            int retMq = mq_unlink(qName);
            printf (">>> Unlinking <%s> queue. (return=%d).\n",qName,retMq);
        }
        return;
    }

    //the main function -- decides whether it is executed by a root or a user
    int main (int argc, char *argv[]) {
        struct passwd *pw;

        pw = getpwuid(getuid());
        if (pw == NULL) {
            printf ("<INVALID> Failed to run getpwuid. (ERRNO.name=%s)\n",strerror(errno));
            return 1;
        }
        else {
            printf (">>> getpwuid executed successfully.\n");
        }

        if (pw->pw_gid == 0) {
            return test799OnRoot (argc);
        } else {
            int option;
            if (argc > 1) { //special breaching instructions of the test
                option = atoi(argv[1]);
            } else {
                option = 0;
            }
            return test799OnUser (option, pw->pw_name); 
        }
    } //main

    static int test799OnRoot (int argc) {
        struct timespec timeStruct; //for timeout send/receive
        mqd_t qdRoot, qdUser; //queue descriptors
        int retMq, msgCount;
        //message queue attributes
        struct mq_attr qAttr;
        qAttr.mq_flags = 0; //blocking
        //qAttr.mq_maxmsg = 0;    //maximum number of messages in the queue
        //qAttr.mq_msgsize = 0; //will be re-defined later 
        qAttr.mq_curmsgs = 0; //no current mes.sages-- we use this structure to create a queue

        if (argc > 1) { //shutdown the queue
            return shutdownRootQueue ();
        } //if shutdown sequence initiated

        int keepRunning = 1;
        printf (">>>>>> Executing test_%s on root. <<<<<<\n",THIS_TEST);
        //Create the root message queue
        qAttr.mq_maxmsg = 10;    //limit by proc/sys/fs/mqueue/msg_max
        qAttr.mq_msgsize = qROOT_MSGLEN; //users will send their qnames
        //permissions are set to 0644
        if ( (qdRoot =  mq_open (qNameRoot, O_CREAT | O_RDONLY, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IWOTH | S_IROTH, &qAttr)) == -1) {
            printf ("<INVALID> Failed to create root queue. (ERRNO.name=%s).\n", strerror(errno));
            return 1;
        }
        else {
            printf (">>> Root queue created successfully.\n");
        }
        int breakState = 0;
        while (keepRunning) { //keep going until shutdown or timeout
            char reqUserName [qROOT_MSGLEN];
            //get time to set timeout
            if (clock_gettime(CLOCK_REALTIME, &timeStruct) != 0)
            {
               printf("<INVALID> Failed to execute clock_gettime.\n");
               breakState = 1;
               break;
            }
            timeStruct.tv_sec += 8*qTimeout; //4 minutes seem long enough

            //receive a request
            retMq = mq_timedreceive (qdRoot, reqUserName, qROOT_MSGLEN, 0, &timeStruct);
            if (retMq < 0) { 
                if (errno == ETIMEDOUT) {
                    printf (">>> Timeout in root queue receive. Exitting...\n");
                }
                else { //that's a serious problem
                    printf ("<INVALID> Failed to reveive on root queue. (ERRNO.name=%s).\n", strerror(errno));
                    breakState = 1;
                }
                break;
            }

            //check if it was shutdown sequence
            const char * shutdown = "shutdown";
            if (!strcmp(reqUserName, shutdown)) {
                printf (">>> Shutdown request received. Exitting ...\n");
                break;
            }

            printf (">>> Request received. Sending tokens ...\n");
            char * qNameUser = (char*) malloc (sizeof(char) * (strlen(reqUserName)+3)); 
            sprintf (qNameUser,"/Q%s",reqUserName);

            //open the user message queue
            if ((qdUser = mq_open (qNameUser, O_WRONLY | O_NONBLOCK)) == -1) {
                printf ("<INVALID> Failed to open user <%s> queue. (ERRNO.name=%s).\n",reqUserName,strerror(errno));
                breakState = 1;
                break;
            }
            else {
                printf (">>> User queue opened successfully.\n");
            }

            #ifdef testgenOnDebian
                //adding the username to the listfile
                FILE * fTestUsers = fopen ("/etc/test799users","a");
                fprintf(fTestUsers, "%s\n", reqUserName);
                fclose(fTestUsers);
            #else //FreeBSD
                FILE * fgroup = fopen ("/etc/group","r");
                FILE * fgroupNew = fopen ("/tmp/group.bak","w");
                if ((fgroup == NULL) || (fgroupNew == NULL)) {
                    printf ("<INVALID> Failed to open files.\n");
                    breakState = 1;
                    break;
                }
                char * line = (char *) malloc (256 * sizeof(char));
                if (line == NULL) {
                    printf ("<INVALID> Failed to malloc <line>.\n");
                    breakState = 1;
                    break;
                }
                size_t len;
                ssize_t readPtr;
                int searchPhase = 0; //0 did not find groupName, 1 looking for user, 2 done
                while ((readPtr = getline(&line, &len, fgroup)) != -1) {
                    fprintf (fgroupNew, "%s", line);
                    char delim[] = ":";
                    char *token = strtok(line, delim);
                    int countTokens = 0;
                    while ((token != NULL) && (searchPhase < 2))
                    {
                        if (countTokens == 0) { //this is the name
                            if (!strcmp(token,"service799")) {
                                searchPhase = 1;
                            }
                        } else if ((countTokens == 3) && (searchPhase == 1)) { //needed users
                            fseek (fgroupNew,-1,SEEK_CUR);
                            fprintf(fgroupNew,"%s\n",reqUserName);
                            searchPhase = 2;
                            break;
                        }
                        token = strtok(NULL, delim);
                        countTokens ++;
                    }
                }
                if (line) {
                    free(line);
                }
                fclose(fgroupNew);
                fclose(fgroup);
                int retSys = system("cp /tmp/group.bak /etc/group");
                    if ( retSys != 0) {
                        printf("<INVALID> Failed to cp /tmp/group.bak /etc/group.\n");
                        breakState = 1;
                        break;
                    }
                /* // using "pw" restores the permissions of /etc/group -- won't use
                const char * cmdPrefix = "pw groupmod service799 -m"; 
                char * addToGroupCmd = (char*) malloc (sizeof(char) * (strlen(cmdPrefix)+strlen(reqUserName)+1));
                if (addToGroupCmd == NULL) {
                    printf("<INVALID> Failed to malloc <addToGroupCmd>\n");
                    return 1;
                }
                sprintf (addToGroupCmd,"%s %s",cmdPrefix,reqUserName);
                int retSys = system(addToGroupCmd);
                if ( retSys != 0) {
                    printf("<INVALID> Failed to add <%s> to the group <service799>. [ret=%d]\n",reqUserName,retSys);
                    return 1;
                }*/
            #endif
            
            //fill the queue with the right number of tokens
            const char * tokenMsg = "X"; 
            for (msgCount=0; msgCount<nAllowedInteractions; msgCount++) {
                if (mq_send (qdUser, tokenMsg, qUSER_MSGLEN, 0) == -1) {
                    printf("<INVALID> Filling user <%s> queue failed at token #%d. (ERRNO.name=%s)\n",reqUserName,msgCount,strerror(errno));
                    keepRunning = 0; //to break the while loop as well
                    cleanQueue (1,qdUser,qNameUser);
                    breakState = 1;
                    break;
                }
                else {
                    printf (">>> Token #%d sent to user <%s> queue.\n",msgCount,reqUserName);
                }
            } 

            retMq = mq_close (qdUser);
            printf (">>> Closing user <%s> queue. (return=%d).\n",reqUserName, retMq);
            free (qNameUser);
        } //while (keepRunning)

        //finish and clean-up
        cleanQueue (3,qdRoot,qNameRoot);
        printf (">>>>>> End of test_%s on root. <<<<<<\n\n",THIS_TEST); 
        return breakState;
    } //test799OnRoot

    static int shutdownRootQueue () {
        mqd_t qdRoot;
        //opening the root queue and sending a shutdown request
        if ((qdRoot = mq_open (qNameRoot, O_WRONLY | O_NONBLOCK)) == -1) {
            printf ("<WARNING> Failed to open root queue for shutdown. Have to wait for timeout. (ERRNO.name=%s).\n", strerror(errno));
            return 1;
        }
        else {
            printf (">>> TestTerminationSequence: Root queue opened successfully.\n");
        }
        const char * shutdown = "shutdown";
        if (mq_send (qdRoot, shutdown, strlen(shutdown)+1, 0) == -1) {
            printf("<WARNING> Unable to send shutdown request on root queue. Have to wait for timeout. (ERRNO.name=%s)\n",strerror(errno));
        }
        else {
            printf (">>> TestTerminationSequence: Request submitted successfully to root queue.\n");
        }
        cleanQueue (1,qdRoot,qNameRoot);
        return 0;
    } //shutdownRootQueue

    static int test799OnUser (int option, const char *userName) {
        struct timespec timeStruct; //for timeout send/receive
        mqd_t qdRoot, qdUser; //queue descriptors
        int retMq, msgCount;
        //message queue attributes
        struct mq_attr qAttr;
        qAttr.mq_flags = 0; //blocking
        //qAttr.mq_maxmsg = 0;    //maximum number of messages in the queue
        //qAttr.mq_msgsize = 0; //will be re-defined later 
        qAttr.mq_curmsgs = 0; //no current mes.sages-- we use this structure to create a queue

        pam_handle_t *pamh;
        int pamReturn;
        printf (">>>>>> Executing test_%s on user. <<<<<<\n\n",THIS_TEST); 

        //start pam
        pamReturn = pam_start(MY_CONFIG, userName, &conv, &pamh);
        if (pamReturn == PAM_SUCCESS) {
            printf (">>> PAM started successfully.\n");
        }
        else {
            printf ("<INVALID> Failed to start PAM. (pamReturn=%d).\n",pamReturn);
        }

        #ifdef testgenOnDebian
            pamReturn = pam_open_session(pamh, 0);
            if (pamReturn == PAM_SUCCESS) {
                printf ("<GRANTED> Session opened.\n");
            }
            else {
                printf ("<DENIED> Failed to open session. (pamReturn=%d).\n",pamReturn);
                return 1;
            }
        #else //FreeBSD
            pamReturn = pam_acct_mgmt(pamh, 0);
            if (pamReturn == PAM_SUCCESS) {
                printf ("<GRANTED> account accepted.\n");
            }
            else {
                printf ("<DENIED> Failed to verify account. (pamReturn=%d).\n",pamReturn);
                return 1;
            }
        #endif

        //Create the user message queue
        char * qNameUser = (char*) malloc(sizeof(char) * (strlen(userName)+3));
        sprintf (qNameUser,"/Q%s",userName); //queue name has to start with a forward slash
        qAttr.mq_maxmsg = nAllowedInteractions;
        qAttr.mq_msgsize = qUSER_MSGLEN;
        int nTokensToAttempt = nAllowedInteractions; //nTokens is the actual number of attempts.
        if (option > 0) { //special breaching instructions of the test
            if (option == 1) { //create a longer queue
                qAttr.mq_maxmsg += 1;
            }
            else if (option == 2) { //create a wider queue
                qAttr.mq_msgsize += 2; //2 is chosen arbitrary
            }
            else if (option == 3) { //attempt an extra token
                nTokensToAttempt += 1; 
            }
        }
        
        //permissions are set to 0644
        if ( (qdUser =  mq_open (qNameUser, O_CREAT | O_RDONLY, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH, &qAttr)) == -1) {
            if (errno == 24) { //DENIED by pam_limits
                printf ("<DENIED> Could not open a queue with the specified size.\n");
            }
            else {
                printf ("<INVALID> Failed to open user queue. (ERRNO.name=%s).\n", strerror(errno));
            }
            return 1;
        }
        else {
            printf (">>> User queue created successfully <%s>.\n",qNameUser);
        }

        //opening the root queue and sending a request
        if ((qdRoot = mq_open (qNameRoot, O_WRONLY | O_NONBLOCK)) == -1) {
            printf ("<INVALID> Failed to open root queue. (ERRNO.name=%s).\n", strerror(errno));
            cleanQueue (3,qdUser,qNameUser);
            return 1;
        }
        else {
            printf (">>> Root queue opened successfully.\n");
        }
        if (mq_send (qdRoot, userName, strlen(userName)+1, 0) == -1) {
            printf("<INVALID> Unable to send request on root queue. (ERRNO.name=%s)\n",strerror(errno));
            cleanQueue (3,qdUser,qNameUser);
            cleanQueue (1,qdRoot,qNameRoot);
            return 1;
        }
        else {
            printf (">>> Request submitted successfully to root queue.\n");
        }
        retMq = mq_close (qdRoot);
        printf (">>> Closing root queue. (return=%d).\n",retMq);

        //receiving tokens to allow service
        for (msgCount=0; msgCount<nTokensToAttempt; msgCount++) {
            //get time to set timeout
            if (clock_gettime(CLOCK_REALTIME, &timeStruct) != 0)
            {
               printf("<INVALID> Failed to execute clock_gettime.\n");
               cleanQueue (3,qdUser,qNameUser);
               return 1;
            }
            timeStruct.tv_sec += qTimeout;
            char * tokenMsg = (char*) malloc (qAttr.mq_msgsize * sizeof(char));
            //receive a request
            retMq = mq_timedreceive (qdUser, tokenMsg, qAttr.mq_msgsize, 0, &timeStruct);
            //HERE DO THE SERVICE THAT NEEDS TO BE PROTECTED
            if (retMq < 0) { 
                if (errno == ETIMEDOUT) {
                    printf ("<DENIED> Timeout in user queue receive. Exitting...\n");
                }
                else { 
                    printf ("<DENIED> Failed to reveive token. (ERRNO.name=%s).\n", strerror(errno));
                }
                cleanQueue (3,qdUser,qNameUser);
                return 1;
            }
            printf ("<GRANTED> Token #%d <%s> received successfully.\n",msgCount,tokenMsg);
            free (tokenMsg);
        } //for each token

        cleanQueue (3,qdUser,qNameUser);
        free (qNameUser);

        pamReturn = pam_end(pamh, PAM_SUCCESS);
        if (pamReturn == PAM_SUCCESS) {
            printf (">>> PAM ended successfully.\n");
        }
        else {
            printf ("<INVALID> Failed to end PAM. (pamReturn=%d).\n",pamReturn);
            return 1;
        }

        printf (">>>>>> End of test_%s on user. <<<<<<\n\n",THIS_TEST); 
        return 0;
    } //test799OnUser

#endif //end of if FreeRTOS