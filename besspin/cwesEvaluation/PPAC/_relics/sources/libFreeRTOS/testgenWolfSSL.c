/*
Functions used for WolfSSL implementation on FreeRTOS
*/
#include "testgenFreeRTOS.h"

#include "caCert.h"
#include "caCertSSITH.h"
#include "serverKey.h"
#include "serverCert.h"

// Declarations
void vEndWolfSSL (void *pvParameters);
int startWolfSSL( void );
void vInitServerWolfSSL (void *pvParameters);
void vInitClientWolfSSL (void *pvParameters);
/* The wolfSSL context for the server. */
WOLFSSL_CTX* xWolfSSL_ServerContext = NULL;
/* The wolfSSL context for the client. */
WOLFSSL_CTX* xWolfSSL_ClientContext = NULL;

//This task ends wolfSSL and free the memory
void vEndWolfSSL (void *pvParameters) {
    (void)pvParameters;
    BaseType_t funcReturn;

    if (xWolfSSL_ServerContext) {
        wolfSSL_CTX_free(xWolfSSL_ServerContext);
    }
    if (xWolfSSL_ClientContext) {
        wolfSSL_CTX_free(xWolfSSL_ClientContext);
    }

    wolfSSL_Cleanup();

    //notify main
    if (xMainTask == NULL) {
        onPrintf ("<INVALID> [endWolfSSL]: Unable to get the handle of <main:task>.\n");
        vEXIT(1);
    }
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
    if (funcReturn != pdPASS) {
        onPrintf ("<INVALID> [endWolfSSL]: Failed to notify <main:task>!\n");
        vEXIT(1);
    } 

    vTaskDelete (NULL);
}

//This function starts WolfSSL. Should be used before any other wolfssl function. And should be used only once.
int startWolfSSL( void )
{
    int funcReturn;

    #ifdef DEBUG_WOLFSSL
    {
        wolfSSL_Debugging_ON();
    }
    #endif

    /* Initialise wolfSSL.  This must be done before any other wolfSSL functions are called. */
    funcReturn = wolfSSL_Init();
    if (funcReturn != SSL_SUCCESS) {
        onPrintf ("<INVALID> [startWolfSSL]: Failed to start WolfSSL. [ret=%d]\n",funcReturn);
        exitTest (1); //cannot use prEXIT because this function is non-void
        return 1;
    }
    //On AWS, this function returns too fast and then the consequent parts do not work well
    vTaskDelay(pdMS_TO_TICKS(3000)); 
    return 0;
}

//This task initializes a wolfSSL server CTX
void vInitServerWolfSSL (void *pvParameters)
{
    (void) pvParameters;
    BaseType_t frReturn; //FreeRTOS return
    int wsReturn; //wolfss return

    /* Attempt to create a context that uses the TLS 1.2 server protocol. */
    WOLFSSL_METHOD * methodTLSv1_2 = wolfTLSv1_2_server_method();
    if (methodTLSv1_2 == NULL) {
        onPrintf ("<INVALID> [initServerWolfSSL]: Failed to create a TLS1.2 method. Probably a memory error.\n");
        vEXIT(1);
    }
    xWolfSSL_ServerContext = wolfSSL_CTX_new( methodTLSv1_2 );
    if (!xWolfSSL_ServerContext) {
        onPrintf ("<INVALID> [initServerWolfSSL]: Failed to create a WolfSSL context.\n");
        vEXIT(1);
    } else {
        onPrintf ("\t>>>>>> Server context <WOLFSSL_CTX> created.\n");
    }

    /* Load the CA certificate. */
    wsReturn = wolfSSL_CTX_load_verify_buffer(xWolfSSL_ServerContext, caCert_pem, caCert_pem_len, SSL_FILETYPE_PEM);
    if (wsReturn != SSL_SUCCESS) {
        onPrintf ("<INVALID> [initServerWolfSSL]: Failed to load CA certificate <load_verify>. [ret=%ld]\n",wsReturn);
        vEXIT(1);
    } else {
        onPrintf ("\t>>>>>> CA certificate loaded.\n");
    }
    /* Load the server certificate */
    wsReturn = wolfSSL_CTX_use_certificate_buffer(xWolfSSL_ServerContext, serverCert_pem, serverCert_pem_len, SSL_FILETYPE_PEM);
    if (wsReturn != SSL_SUCCESS) {
        onPrintf ("<INVALID> [initServerWolfSSL]: Failed to load certificate <use_certificate>. [ret=%d]\n",wsReturn);
        vEXIT(1);
    } else {
        onPrintf ("\t>>>>>> Server certificate loaded.\n");
    }
    /* Load the server private key */
    wsReturn = wolfSSL_CTX_use_PrivateKey_buffer(xWolfSSL_ServerContext, serverKey_pem, serverKey_pem_len, SSL_FILETYPE_PEM);
    if (wsReturn != SSL_SUCCESS) {
        onPrintf ("<INVALID> [initServerWolfSSL]: Failed to load private key <use_PrivateKey>. [ret=%d]\n",wsReturn);
        vEXIT(1);
    } else {
        onPrintf ("\t>>>>>> Server private key loaded.\n");
    }

    #ifdef doVERIFY_CLIENT_CERT
        wolfSSL_CTX_set_verify(xWolfSSL_ServerContext, SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT, NULL);
        onPrintf ("\t>>>>>> \"Verify client mode\" activated.\n");
    #endif

    //notify main
    if (xMainTask == NULL) {
        onPrintf ("<INVALID> [initServerWolfSSL]: Unable to get the handle of <main:task>.\n");
        vEXIT(1);
    }
    frReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
    if (frReturn != pdPASS) {
        onPrintf ("<INVALID> [initServerWolfSSL]: Failed to notify <main:task>!\n");
        vEXIT(1);
    } 

    vTaskDelete (NULL);
}

//This task initializes a wolfSSL client CTX
void vInitClientWolfSSL (void *pvParameters)
{
    BaseType_t frReturn; //FreeRTOS return
    uint8_t useJediCert = * (uint8_t *) pvParameters;
    int wsReturn; //wolfss return
    
    /* Attempt to create a context that uses the TLS 1.2 client protocol. */
    WOLFSSL_METHOD * methodTLSv1_2 = wolfTLSv1_2_client_method();
    if (methodTLSv1_2 == NULL) {
        onPrintf ("<INVALID> [initClientWolfSSL]: Failed to create a TLS1.2 method. Probably a memory error.\n");
        vEXIT(1);
    }
    xWolfSSL_ClientContext = wolfSSL_CTX_new( methodTLSv1_2 );
    if (!xWolfSSL_ClientContext) {
        onPrintf ("<INVALID> [initClientWolfSSL]: Failed to create a WolfSSL context.\n");
        vEXIT(1);
    } else {
        onPrintf ("\t>>>>>> Client context <WOLFSSL_CTX> created.\n");
    }

    /* Load the CA certificate. */
    if (useJediCert == uTRUE) { //use the Jedi certificate
        wsReturn = wolfSSL_CTX_load_verify_buffer(xWolfSSL_ClientContext, caCert_pem, caCert_pem_len, SSL_FILETYPE_PEM);
    } else { //use the ssith certificate
        wsReturn = wolfSSL_CTX_load_verify_buffer(xWolfSSL_ClientContext, caCertSSITH_pem, caCertSSITH_pem_len, SSL_FILETYPE_PEM);        
    }
    if (wsReturn != SSL_SUCCESS) {
        onPrintf ("<INVALID> [initClientWolfSSL]: Failed to load CA certificate <load_verify>. [ret=%ld,Jedi=%d]\n",wsReturn,useJediCert);
        vEXIT(1);
    } else {
        onPrintf ("\t>>>>>> CA certificate loaded.\n");
    }

    //notify main
    if (xMainTask == NULL) {
        onPrintf ("<INVALID> [initClientWolfSSL]: Unable to get the handle of <main:task>.\n");
        vEXIT(1);
    }
    frReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS ,eSetValueWithOverwrite);
    if (frReturn != pdPASS) {
        onPrintf ("<INVALID> [initClientWolfSSL]: Failed to notify <main:task>!\n");
        vEXIT(1);
    } 

    vTaskDelete (NULL);
}