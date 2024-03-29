#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

static int *useUninit (bool x);
static void uninitString (void);

// --------------- FreeRTOS Test ---------------
#ifdef BESSPIN_FREERTOS
    #define NUM_OF_TEST_PARTS 2

    void main() {
        printf("\n<OSIMAGE=FreeRTOS>\n");
        
        #if BESSPIN_TEST_PART == 1
            printf("\n---Part01: Use uninit---\n");
            int *pRet = useUninit(false);
            printf("<RETVAL=0x%X>\n",*pRet);
            FREE(pRet);
        #elif BESSPIN_TEST_PART == 2
            printf("\n---Part02: Uninit String---\n");
            uninitString();
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",BESSPIN_TEST_PART,NUM_OF_TEST_PARTS);
        #endif

        printf("\n<END-OF-MAIN>\n");
        return;
    }

// --------------- Debian && FreeBSD test ---------------
#elif (defined(BESSPIN_DEBIAN) || defined(BESSPIN_FREEBSD))
#include "unbufferStdout.h"
    int main(int argc, char *argv[]);

    int main(int argc, char *argv[]) {
        unbufferStdout();
        int option;
        int *pRet;
        if (argc > 1) { //be safe
            option = atoi(argv[1]);
        } else {
            option = -1;
        }
        
        switch(option) {
            case 1 :
                pRet = useUninit(false);
                printf("<RETVAL=0x%X>\n",*pRet);
                FREE(pRet);
                break;
            case 2 :
                uninitString();
                break;
            default :
                printf("\n<INVALID> Part[%d] not in [1,2].\n",option);
                return 1;
        }

        printf("\n<END-OF-MAIN>\n");
        return 0;
    }

#endif //ifdef BESSPIN_FREERTOS

// This function returns a non-unitialized int
static int *useUninit (bool x) {
    int *pVal = (int *) MALLOC (sizeof(int));

    if (pVal == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return NULL;
    }

    if (x) {
        printf("<INVALID> useUninit should never be called with true.\n");
        *pVal = 0xBB; //arbitrary value
    } else {
        printf("<USE-UNINIT>\n");
    }
    return pVal;
}

// This function allocates a number of chars on the heap, but leave a bunch of them unitialized
#define XSTRLEN 10
static void uninitString () {
    int i;
    char shortStr[] = "BBBBB"; 
    char *xStr = (char *) MALLOC (XSTRLEN*sizeof(char));

    if (xStr == NULL) {
        printf("<INVALID> Failed to Malloc.\n");
        return;
    }

    strcpy (xStr, shortStr);

    printf("using %%s: xStr=<%s>.\n",xStr);

    for (i=0;i<XSTRLEN;i++) {
        printf("xStr[%d]=<%d>\n",i,(int) xStr[i]);
    }
    FREE(xStr);
    return;
}
