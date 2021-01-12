#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include "testsParameters.h"

static void noClearReallocTest(void);

#ifdef testgenOnFreeRTOS
    void main() {
        noClearReallocTest();
        return;
    }
#else
    int main(void);
    int main() {
        noClearReallocTest();
        return 0;
    }
#endif

static void noClearReallocTest() {
    puts("TEST NOT IMPLEMENTED.\n");
    return;
}