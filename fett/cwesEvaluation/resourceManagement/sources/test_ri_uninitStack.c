#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

static int useUninit (bool x);
static void uninitString (void);

// --------------- FreeRTOS Test ---------------
#ifdef testgenOnFreeRTOS
    #define NUM_OF_TEST_PARTS 2

    void main() {
        printf("\n<OSIMAGE=FreeRTOS>\n");
        
        #if TESTGEN_TEST_PART == 1
            printf("\n---Part01: Use uninit---\n");
            int retVal;
            retVal = useUninit(false);
            printf("<RETVAL=0x%X>\n",retVal);
        #elif TESTGEN_TEST_PART == 2
            printf("\n---Part02: Uninit String---\n");
            uninitString();
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",TESTGEN_TEST_PART,NUM_OF_TEST_PARTS);
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
                retVal = useUninit(false);
                printf("<RETVAL=0x%X>\n",retVal);
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

#endif //ifdef testgenOnFreeRTOS


// This function returns a non-unitialized int
static int useUninit (bool x) {
    int val; //Uninitialized
    if (x) {
        printf("<INVALID> useUninit should never be called with true.\n");
        val = 0xBB; //arbitrary value
    } else {
        printf("<USE-UNINIT>\n");
    }
    return val;
}

// This function allocates a number of chars on the stack, but leave them unitialized
#define XSTRLEN 10
static void uninitString () {
    char xStr[XSTRLEN];
    int i;
    char shortStr[] = "BBBBB"; 

    strcpy (xStr, shortStr);

    printf("using %%s: xStr=<%s>.\n",xStr);

    for (i=0;i<XSTRLEN;i++) {
        printf("xStr[%d]=<%d>\n",i,(int) xStr[i]);
    }
    return;
}