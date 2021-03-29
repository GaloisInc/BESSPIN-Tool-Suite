#include "testsParameters.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N_FUNC 3 //How many functions we define to add to the confusion?
#define SIZE_FUNC_0 100
#define FILL_VAL_0 0xb
#define SIZE_FUNC_1 200
#define FILL_VAL_1 0xc
#define SIZE_FUNC_2 300
#define FILL_VAL_2 0xd

static int callRandFunc (void);
static int func0 (void);
static int func1 (void);
static int func2 (void);

// --------------- FreeRTOS Test ---------------
#ifdef BESSPIN_FREERTOS
    #define NUM_OF_TEST_PARTS 1

    void main() {
        unsigned int retVal;
        printf("\n<OSIMAGE=FreeRTOS>\n");
        srand(RM_SEED);
        #if BESSPIN_TEST_PART == 1
            retVal = callRandFunc();
            printf("\n<END-OF-MAIN>\n");
        #else
            printf("\n<INVALID> Part[%d] not in [1,%d].\n",BESSPIN_TEST_PART,NUM_OF_TEST_PARTS);
        #endif
    }

// --------------- Debian && FreeBSD test ---------------
#elif (defined(BESSPIN_DEBIAN) || defined(BESSPIN_FREEBSD))
#include "unbufferStdout.h"
    int main(void);

    int main() {
        unbufferStdout();
        srand(RM_SEED); //RM_SEED is written in besspin/cwesEvaluation/build.py
        return callRandFunc();
    }

#endif //ifdef BESSPIN_FREERTOS

static int callRandFunc() {
    unsigned int whichFuncToCall;

    whichFuncToCall = (unsigned int) (rand() % N_FUNC);
    switch(whichFuncToCall) {
        case 0 :
            return func0();
        case 1 :
            return func1();
        case 2 :
            return func2();
        default:
            printf("\n<INVALID> default case statement! Wrong function number.\n");
            return 1;
    }
}

static int func0 () {
    char dump0[SIZE_FUNC_0];
    memset (dump0,FILL_VAL_0,SIZE_FUNC_0);
    return callRandFunc();
}

static int func1 () {
    char dump1[SIZE_FUNC_1];
    memset (dump1,FILL_VAL_1,SIZE_FUNC_1);
    return callRandFunc();
}

static int func2 () {
    char dump2[SIZE_FUNC_2];
    memset (dump2,FILL_VAL_2,SIZE_FUNC_2);
    return callRandFunc();
}
