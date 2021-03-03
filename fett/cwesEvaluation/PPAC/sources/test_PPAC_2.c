#include "testsParameters.h"
#include <stdio.h>

#ifdef testgenOnFreeRTOS
    void main() {
        printf("\n<INVALID> This test should never run on FreeROTS.\n");
        return;
    }

//---------------- Unix test ------------------------------------------------------
#elif defined(testgenOnDebian) || defined(testgenOnFreeBSD)

    int main () {
        printf (">>> This test is fully interactive.\n");
        return 0;
    }
    
#endif //end of if FreeRTOS