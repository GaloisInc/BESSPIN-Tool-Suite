/*
fett settings for WolfSSL -- This file is included in <WOLFSSL>/wolfssl/wolfcrypt/settings.h
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
/* The value used instead of (void * heap) to mark a realloc call as edited by fett */
#define USE_FETT_REALLOC 1 //heap will never start at 0x1 (not aligned and in the wrong region)
/* To allow the retrieval of settings of the peer certs */
#define KEEP_PEER_CERT
/* To allow the use of Base64Encode */
#define WOLFSSL_BASE64_ENCODE
/* Allow the use of Diffie-Hellman Library */
#define HAVE_DH
/* Allow the use of SHA512 - needed for Ed25519 */
#define HAVE_SHA512
#define WOLFSSL_SHA512
#define USE_SLOW_SHA2
/* Allow the use of Ed25519 signature algorithm */
#define HAVE_CURVE25519
#define HAVE_ED25519

/* enable FETT-specific modifications in WolfSSL sources */
#define fettOnFreeRTOS
