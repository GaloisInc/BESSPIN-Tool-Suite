#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#ifdef testgenOnUnix 
    #include <sys/mman.h>
#endif

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

/* The values have to be fixed and non-dynamic to fit the CWE description.
 We could have them generated pre-compilation and include them in testParameters.h if we 
 really want them to be random. Will have to figure out the appropriate ranges if we
 elect to go that way.
 The values were obtained by trying to allocate function/array dynamically, then using 
 a value slightly larger.
*/ 
#ifdef testgenOnFreeBSD
    #define FIXED_ADDR_DATA 0x40810008
#else
    #define FIXED_ADDR_DATA 0x15000
#endif

#ifdef testgenOnUnix 
    #define FIXED_ADDR_FUNC 0x2000020000
#elif testgenQEMU //FreeRTOS-Qemu
    #define FIXED_ADDR_FUNC 0x20400300
#else //other FreeRTOS
    #define FIXED_ADDR_FUNC 0xc000d000
#endif

static int jumpToFixedAddr (void);
static void copyToFixedAddr (void); 

// --------------- FreeRTOS Test ---------------
#ifdef testgenOnFreeRTOS
    #define NUM_OF_TEST_PARTS 2

    void main() {
        printf("\n<OSIMAGE=FreeRTOS>\n");
        #if TESTGEN_TEST_PART == 1
            printf("\n---Part01: Just copy---\n");
            copyToFixedAddr();
        #elif TESTGEN_TEST_PART == 2
            printf("\n---Part02: Jump to fixed address---\n");
            int retVal;
            retVal = jumpToFixedAddr();
            printf("<RETVAL=0x%X>\n",retVal);
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",TESTGEN_TEST_PART,NUM_OF_TEST_PARTS);
            return;
        #endif

        printf("\n<END-OF-MAIN>\n");
        return;
    }

// --------------- Debian && FreeBSD test ---------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))
    int main(int argc, char *argv[]);

    int main(int argc, char *argv[]) {
        int option, retVal;
        if (argc > 1) { //be safe
            option = atoi(argv[1]);
        } else {
            option = -1;
        }

        switch(option) {
            case 1 :
                copyToFixedAddr();
                break;
            case 2 :
                retVal = jumpToFixedAddr();
                printf("<RETVAL=0x%X>\n",retVal);
                break;
            default :
                printf("\n<INVALID> Part[%d] not in [1,2].\n",option);
                return 1;
        }

        printf("\n<END-OF-MAIN>\n");
        return 0;
    }

#endif //ifdef testgenOnFreeRTOS

int testegenTestFunc () { 
    return 0xbb;
}


static int jumpToFixedAddr () {
    printf("<JUMP-TO-FIXED-ADDR>\n");

    void (*pTest) (void) = copyToFixedAddr;
    printf("pTest=<%lx>\n",(unsigned long int) pTest);
    testegenTestFunc();

    int (*pFunction) (void) = (int (*)(void)) FIXED_ADDR_FUNC;

    printf("<VALUE-ASSIGNED>\n");

    // The assembly (little endian) for:
    //  int func () { return 0xbb }
    #ifdef testgenOnUnix
        // 0xe4221141, 0x7930800, 0x853e0bb0, 0x1416422, 0xXXXX8082
        unsigned char prog[] = {
            0x41, 0x11, 0x22, 0xe4,
            0x00, 0x08, 0x93, 0x07,
            0xb0, 0x0b, 0x3e, 0x85,
            0x22, 0x64, 0x41, 0x01,
            0x82, 0x80
        };
    #else
        // 0xff010113, 0x00812623, 0x01010413, 0x0bb00793, 0x00078513, 0x00c12403, 0x01010113, 0x00008067
        unsigned char prog[] = {
            0x13, 0x01, 0x01, 0xff,
            0x23, 0x26, 0x81, 0x00,
            0x13, 0x04, 0x01, 0x01,
            0x93, 0x07, 0xb0, 0x0b,
            0x13, 0x85, 0x07, 0x00,
            0x03, 0x24, 0xc1, 0x00,
            0x13, 0x01, 0x01, 0x01,
            0x67, 0x80, 0x00, 0x00          
        };
    #endif

    #ifdef testgenOnUnix 
        // Mark this block as executable
        mmap (pFunction, sizeof(prog), PROT_READ|PROT_WRITE|PROT_EXEC,
                 MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    #endif
    
    memcpy(pFunction,prog,sizeof(prog));
    printf("<MEMORY-READY>\n");

    return (*pFunction) ();
    
}

static void copyToFixedAddr () {
    printf("<COPY-TO-FIXED-ADDR>\n");

    int * pTest = (int *) MALLOC (4);
    printf("pTest=<%lx>\n",(unsigned long int) pTest);
    FREE(pTest);

    int * pAddr = (int *) FIXED_ADDR_DATA;
    int inst = 0x0bb00f93; //0x0bb00f93 is "li t6,0xbb", chosen arbitrarily

    printf("<VALUE-ASSIGNED>\n");
    
    memcpy(pAddr,&inst,4);

    printf("<MEMORY-READY>\n");
    printf("Value of pAddr=<%x>, addr =<%lx>\n",*pAddr,(long unsigned int) pAddr);

    return;
}