/* This is the common header for nonstandard tests */

#ifndef __NON_STD_COMMON_H__
#define __NON_STD_COMMON_H__

#include "testsParameters.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_QEMU))
    #define MALLOC_BLOCK_SIZE_MAX 0x004F //Maximum allocatable size in FreeRTOS qemu is 0x8F
    #define MALLOC_BLOCK_SIZE_MIN 0x0020 //A block of 32 bytes
#else
    #define MALLOC_BLOCK_SIZE_MAX 0x00FF 
    #define MALLOC_BLOCK_SIZE_MIN 0x0064 //A block of 100 bytes
#endif
#define MAX_SECRET_VALUE 0x54 //Easy solution to avoid 0xff, 0xaa, 0x5a, and 0x55
#define MIN_SECRET_VALUE 0x02 //Avoid zero and one
#define N_MATCHES_TO_COUNT 4 //Have to find the byte value 4 times to avoid unfortunate coincidences

#ifdef BESSPIN_FREERTOS
    #include "FreeRTOS.h"
    #include "task.h"
    #define EXIT puts(">>>End of Besspin<<<\n"); vTaskDelete(NULL)   
#else
    #define EXIT exit(1)
#endif

#if defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA)
    #define test_malloc pvPortMalloc
    #define test_free   vPortFree
#else
    #define test_malloc malloc
    #define test_free   free
#endif
    
#ifdef DEBUG
    #define DEBUG_PRINTF(...) printf(__VA_ARGS__)
#else
    #define DEBUG_PRINTF(...)
#endif

typedef struct secretLocInfo_ {
    unsigned char secret;
    unsigned char *pSecret;
    size_t szSecret;
} secretLocInfo_t;

/* main declaration */
#ifdef BESSPIN_FREERTOS
    void main_besspin(void);
#else
    int main(void);
#endif

/* Functions declarations (defined in nonstdCommon.c) */
secretLocInfo_t * mallocSecretInfo (void);
unsigned char createSecret(void);
void findSecret(secretLocInfo_t * secretInfo);

#endif // For the header guard
