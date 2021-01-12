/* This is the common header for nonstandard tests */

#include "testsParameters.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>

#if (defined(testgenOnFreeRTOS) && defined(testgenQEMU))
    #define MALLOC_BLOCK_SIZE_MAX 0x004F //Maximum allocatable size in FreeRTOS qemu is 0x8F
    #define MALLOC_BLOCK_SIZE_MIN 0x0020 //A block of 32 bytes
#else
    #define MALLOC_BLOCK_SIZE_MAX 0x00FF 
    #define MALLOC_BLOCK_SIZE_MIN 0x0064 //A block of 100 bytes
#endif
#define MAX_SECRET_VALUE 0x54 //Easy solution to avoid 0xff, 0xaa, 0x5a, and 0x55
#define MIN_SECRET_VALUE 0x02 //Avoid zero and one
#define N_MATCHES_TO_COUNT 4 //Have to find the byte value 4 times to avoid unfortunate coincidences

#ifdef testgenOnFreeRTOS
    #include "FreeRTOS.h"
    #include "task.h"
    #define EXIT puts(">>>End of Fett<<<\n"); vTaskDelete(NULL)   
#else
    #define EXIT exit(1)
#endif

#if defined(testgenOnFreeRTOS) && defined(testgenFPGA)
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
#ifdef testgenOnFreeRTOS
    void main_fett(void);
#else
    int main(void);
#endif

/* Functions declarations (defined in nonstdCommon.c) */
secretLocInfo_t * mallocSecretInfo (void);
unsigned char createSecret(void);
void findSecret(secretLocInfo_t * secretInfo);
