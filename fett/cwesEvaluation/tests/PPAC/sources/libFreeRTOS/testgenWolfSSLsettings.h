/*
testgen settings for WolfSSL -- This file is included in <WOLFSSL>/wolfssl/wolfcrypt/settings.h
*/

/* Needed for many parts of WolfSSL*/
#define FREERTOS
/* To use buffer arrays instead of certificate files */
#define NO_FILESYSTEM
/* For smaller implementations -- saves memory */
#define WOLFSSL_SMALL_STACK
/* Enable the following only during debugging development -- dumps lots of debug text */
//#define DEBUG_WOLFSSL
/* For smaller implementations -- saves memory */
#define BENCH_EMBEDDED
/* The value used instead of (void * heap) to mark a realloc call as edited by testgen */
#define USE_TESTGEN_REALLOC 1 //heap will never start at 0x1 (not aligned and in the wrong region)
/* To allow the retrieval of settings of the peer certs */
#define KEEP_PEER_CERT
/* To allow the use of Base64Encode */
#define WOLFSSL_BASE64_ENCODE
/* Allow the use of Diffie-Hellman Library */
#define HAVE_DH
