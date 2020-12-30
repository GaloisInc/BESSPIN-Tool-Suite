#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#ifdef testgenOnUnix 
    #define FIXED_ADDR_DATA 0x15000
    #define FIXED_ADDR_FUNC 0x2000020000
#else
    #define FIXED_ADDR_DATA 0xc000d000
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
    
    int (*pFunction) (void) = (int (*)(void)) FIXED_ADDR_FUNC;

    return (*pFunction) ();
    /* The function call will cause a segfault/trap unless we use a value in the right region for pFunction,
        and we store a valid stub/program in that location. Here's some simple steps in case someone wants to
        craft a specific attack:
        (*) To get a value, the easiest thing to do is to:
                void (*pTest) (void) = copyToFixedAddr; //any existing function
                printf("pTest=<%lx>\n",(unsigned long int) pTest);
            Then use a larger value to guarantee you're in the right region, for instance:
            - For GFE-Debian/FreeBSD-qemu and GFE-Debian-awsf1, the value 0x2000020000 works
            - For GFE-FreeRTOS-qemu, the value 0x20400300 works.
            - For GFE/LMCO-FreeRTOS-awsf1, the value 0xc000d000 works.

        (*) You need a program. For example, the assembly (little endian) for returning the int value 187:
            >>> int func () { return 0xbb; }, is:
            - P2: 0xe4221141, 0x7930800, 0x853e0bb0, 0x1416422, 0xXXXX8082
                unsigned char prog[] = {
                    0x41, 0x11, 0x22, 0xe4,
                    0x00, 0x08, 0x93, 0x07,
                    0xb0, 0x0b, 0x3e, 0x85,
                    0x22, 0x64, 0x41, 0x01,
                    0x82, 0x80
                };
            - P1: 0xff010113, 0x00812623, 0x01010413, 0x0bb00793, 0x00078513, 0x00c12403, 0x01010113, 0x00008067
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

        (*) Then, before calling the function, you need to change the permissions in that block (in case of unix), 
            and copy the bytes over:
            - #include <sys/mman.h>
            - mmap (pFunction, sizeof(prog), PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
            - memcpy(pFunction,prog,sizeof(prog));
    */
    
}

static void copyToFixedAddr () {
    printf("<COPY-TO-FIXED-ADDR>\n");

    int * pAddr = (int *) FIXED_ADDR_DATA;
    int inst = 0x0bb00f93; //0x0bb00f93 is "li t6,0xbb", chosen arbitrarily
    
    memcpy(pAddr,&inst,4);
    /* The memcpy line will cause a segfault/trap unless we use a value in the right region
        For example, you can get a working value by running the following:
            int * pTest = (int *) MALLOC (sizeof(int));
            printf("pTest=<%lx>\n",(unsigned long int) pTest);
            FREE(pTest);
        Then, you can choose a larger value, for instance:
        - For GFE-FreeBSD-vcu118/qemu/awsf1, the value 0x40810008 is good.
        - For GFE/LMCO-FreeRTOS-vcu118/awsf1, the value 0xc01d0000 is good.
        - For GFE-FreeRTOS-qemu or GFE-Debian-qemu/vcu118/awsf1, the value 0x15000 works. 
    */
    return;
}