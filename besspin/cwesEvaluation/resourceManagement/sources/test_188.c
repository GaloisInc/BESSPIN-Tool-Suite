#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA))
    #include "FreeRTOS.h"
    #define MALLOC pvPortMalloc
    #define FREE vPortFree
#else
    #define MALLOC malloc
    #define FREE free
#endif

#define FILL_AMOUNT_STACK 16 //arbitrary value
#define MESS_RADIUS_STACK FILL_AMOUNT_STACK //seems enough

#define FILL_AMOUNT_HEAP 128 //Let's go far
#define MESS_RADIUS_HEAP FILL_AMOUNT_HEAP //seems reasonable

enum direction {BEFORE, AFTER};
enum operation {READ, WRITE};

static void stackTest(enum direction dirOffset, enum operation opType);
static void heapTest(enum direction dirOffset, enum operation opType);

// --------------- FreeRTOS Test ---------------
#ifdef BESSPIN_FREERTOS
    #define NUM_OF_TEST_PARTS 8

    void main() {
        printf("\n<OSIMAGE=FreeRTOS>\n");
        #if BESSPIN_TEST_PART==1
            printf("\n---Part01: Stack Test [BEFORE, READ] ---\n");
            stackTest(BEFORE, READ);
        #elif BESSPIN_TEST_PART==2
            printf("\n---Part02: Stack Test [BEFORE, WRITE] ---\n");
            stackTest(BEFORE, WRITE);
        #elif BESSPIN_TEST_PART==3
            printf("\n---Part03: Stack Test [AFTER, READ] ---\n");
            stackTest(AFTER, READ);
        #elif BESSPIN_TEST_PART==4
            printf("\n---Part04: Stack Test [AFTER, WRITE] ---\n");
            stackTest(AFTER, WRITE);
        #elif BESSPIN_TEST_PART==5
            printf("\n---Part05: Heap Test [BEFORE, READ] ---\n");
            heapTest(BEFORE, READ);
        #elif BESSPIN_TEST_PART==6
            printf("\n---Part06: Heap Test [BEFORE, WRITE] ---\n");
            heapTest(BEFORE, WRITE);
        #elif BESSPIN_TEST_PART==7
            printf("\n---Part07: Heap Test [AFTER, READ] ---\n");
            heapTest(AFTER, READ);
        #elif BESSPIN_TEST_PART==8
            printf("\n---Part08: Heap Test [AFTER, WRITE] ---\n");
            heapTest(AFTER, WRITE);
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",BESSPIN_TEST_PART,NUM_OF_TEST_PARTS);
            return;
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
        if (argc > 1) { //be safe
            option = atoi(argv[1]);
        } else {
            option = -1;
        }

        switch(option) {
            case 1 :
                stackTest(BEFORE, READ);
                break;
            case 2 :
                stackTest(BEFORE, WRITE);
                break;
            case 3 :
                stackTest(AFTER, READ);
                break;
            case 4 :
                stackTest(AFTER, WRITE);
                break;
            case 5 :
                heapTest(BEFORE, READ);
                break;
            case 6 :
                heapTest(BEFORE, WRITE);
                break;
            case 7 :
                heapTest(AFTER, READ);
                break;
            case 8 :
                heapTest(AFTER, WRITE);
                break;
            default :
                printf("\n<INVALID> Part[%d] not in [1,8].\n",option);
                return 1;
        }
        printf("\n<END-OF-MAIN>\n");
        return 0;
    }
#endif //ifdef BESSPIN_FREERTOS

static void stackTest(enum direction dirOffset, enum operation opType) {
    char fillStart[FILL_AMOUNT_STACK];
    char goodCharBefore = 'A';
    char badChar = 'X';
    char goodCharAfter = 'A';
    char fillEnd[FILL_AMOUNT_STACK];

    int offset;
    char * pLoc;

    // This printing is essential to avoid any re-arrangements or optimizations.
    printf("\nfillStart\t= <%p>\n&goodCharBefore\t= <%p>\n&badChar\t= <%p>\n&goodCharAfter\t= <%p>\nfillEnd\t\t= <%p>\n\n",
                fillStart, &goodCharBefore, &badChar, &goodCharAfter, fillEnd);

    // fill the padding with 'X' -- why not
    memset(fillStart,'X',FILL_AMOUNT_STACK);
    memset(fillEnd,'X',FILL_AMOUNT_STACK);
    
    // Mess with badChar before and after
    printf("<BEGIN-MESS-%d-%d>\n",dirOffset,opType); 
    for (offset=1; offset<=MESS_RADIUS_STACK; offset++) {
        if (dirOffset==AFTER) {
            printf("OFFSET: <+%d>.\n",offset);
            pLoc = (&badChar + offset);
        } else {
            printf("OFFSET: <-%d>.\n",offset);
            pLoc = (&badChar - offset);
        }
        if (opType==WRITE) {
            *pLoc = 'X';
        } else {
            printf("pLoc=<%c>\n",*pLoc);
        }
        printf("<GOOD-CHARS> = <%c,%c>\n",goodCharBefore,goodCharAfter);
        
    }

    return;
}

static void heapTest(enum direction dirOffset, enum operation opType) {
    char *fillStart = (char *) MALLOC (FILL_AMOUNT_HEAP);
    char *goodCharBefore = (char *) MALLOC (1);
    char *badChar = (char *) MALLOC (1);
    char *goodCharAfter = (char *) MALLOC (1);
    char *fillEnd = (char *) MALLOC (FILL_AMOUNT_HEAP);

    int offset;
    char * pLoc;

    if (    (fillStart==NULL) || (fillEnd==NULL) || 
            (goodCharBefore==NULL) || (goodCharAfter==NULL) ||
            (badChar==NULL)
        ) {
        printf("<INVALID> Failed to Malloc.\n");
        return;
    }

    // This printing is essential to avoid any re-arrangements or optimizations.
    printf("\nfillStart\t= <%p>\ngoodCharBefore\t= <%p>\nbadChar\t= <%p>\ngoodCharAfter\t= <%p>\nfillEnd\t\t= <%p>\n\n",
                fillStart, goodCharBefore, badChar, goodCharAfter, fillEnd);

    // All initializations
    memset(fillStart,'X',FILL_AMOUNT_HEAP);
    *goodCharBefore = 'A';
    *badChar = 'X';
    *goodCharAfter = 'A';
    memset(fillEnd,'X',FILL_AMOUNT_HEAP);

    // Mess with badChar before and after
    printf("<BEGIN-MESS-%d-%d>\n",dirOffset,opType); 
    for (offset=1; offset<=MESS_RADIUS_HEAP; offset++) {
        if (dirOffset==AFTER) {
            printf("OFFSET: <+%d>.\n",offset);
            pLoc = (badChar + offset);
        } else {
            printf("OFFSET: <-%d>.\n",offset);
            pLoc = (badChar - offset);
        }
        if (opType==WRITE) {
            *pLoc = 'X';
        } else {
            printf("pLoc=<%c>\n",*pLoc);
        }
        printf("<GOOD-CHARS> = <%c,%c>\n",*goodCharBefore,*goodCharAfter);
    }

    return;
}