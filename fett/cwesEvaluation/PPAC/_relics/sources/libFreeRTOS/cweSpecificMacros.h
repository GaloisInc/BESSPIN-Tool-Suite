/*
testgen macros that change from a test to another
*/

#if TESTNUM == 307
    #define USE_TLS_OVER_TCP 
    #define nConnAttemptsTLS nAllowedAuthAttempts //this is specific to test_307
    #define doVERIFY_CLIENT_CERT
    #define doPRINT_GRANTED_IN_NTK
#elif TESTNUM == 799
    #define USE_TLS_OVER_TCP 
    #define doVERIFY_CLIENT_CERT //verifies the client certificate too (target is the server)
    #define doFETCH_SUBJECT_CN
    #define MSGBUF_SIZE 32
#elif TESTNUM == 284
    #define USE_TLS_OVER_TCP 
    #define doVERIFY_CLIENT_CERT //verifies the client certificate too (target is the server)
    #define doFETCH_SUBJECT_CN
    #define MSGBUF_SIZE 32
    #define SUBJECT_CN_BUF_SIZE 20
#elif TESTNUM == 287
    #define USE_TLS_OVER_TCP 
    #if (TESTGEN_TEST_PART == 1) || (TESTGEN_TEST_PART == 2)
        #define doVERIFY_CLIENT_CERT //verifies the client certificate too (target is the server)
        #define doFETCH_SUBJECT_CN
    #else //part 3
        #define doFETCH_RECV_MSG
    #endif
    #define MSGBUF_SIZE 32
    #define SUBJECT_CN_BUF_SIZE 20
#elif TESTNUM == 288
    #define USE_TLS_OVER_TCP 
    #define doVERIFY_CLIENT_CERT //verifies the client certificate too (target is the server)
    #define doFETCH_SUBJECT_CN
    #define doASK_FOR_NAME_IF_AUTH_FAILED
    #define MSGBUF_SIZE 32
    #define SUBJECT_CN_BUF_SIZE 20
    extern void vCommunicateTCPaskForAuth (void *pvParameters);
#elif TESTNUM == 289
    #define USE_TLS_OVER_TCP 
    #define doVERIFY_CLIENT_CERT //verifies the client certificate too (target is the server)
    #define doFETCH_SUBJECT_CN
    #define MSGBUF_SIZE 32
    #define SUBJECT_CN_BUF_SIZE 20
#elif TESTNUM == 290
    #define IP_NAME_SIZE 16
#elif TESTNUM == 294
    #define IP_NAME_SIZE 16
    #define doFETCH_CLIENT_IP
    #define TCP_DIFF_MESSAGES
    #define MSGBUF_SIZE 32
    extern void vCommunicateTCPdiffMessages (void *pvParameters);
#elif TESTNUM == 257
    #define USE_TLS_OVER_TCP
    #define doVERIFY_CLIENT_CERT
    #define doFETCH_RECV_MSG
    #define doFETCH_SUBJECT_CN
    #if (__riscv_xlen == 64)
        #define MSGBUF_SIZE 60 //20 for CN, 32 for PW, and 4 for handle
    #else
        #define MSGBUF_SIZE 56 //20 for CN, 32 for PW, and 8 for handle
    #endif
    #define SUBJECT_CN_BUF_SIZE 20
    #define SEND_CUSTOM_REPLY 
    #define PW_SIZE 32
#elif TESTNUM == 259
    #define USE_TLS_OVER_TCP
    #if (TESTGEN_TEST_PART == 1)
        #define doVERIFY_CLIENT_CERT
        #define doFETCH_RECV_MSG
        #define doFETCH_SUBJECT_CN
        #define SUBJECT_CN_BUF_SIZE 20
    #endif
    #if (__riscv_xlen == 64)
        #define MSGBUF_SIZE 60 //20 for CN, 32 for PW, and 4 for handle
    #else
        #define MSGBUF_SIZE 56 //20 for CN, 32 for PW, and 8 for handle
    #endif
    #define SEND_CUSTOM_REPLY 
    #define PW_SIZE 32
#elif TESTNUM == 301
    #define TCP_DIFF_MESSAGES
    #define KEY_SIZE 128
    extern void vCommunicateTCPdiffMessages (void *pvParameters);
#endif   