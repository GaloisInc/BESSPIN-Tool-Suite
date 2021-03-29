/* Test noClearReallocExpand */
#include "noClearRealloc.h"

#ifdef testgenOnFreeRTOS
    void main() {
        noClearReallocTest(EXPAND);
        return;
    }
#else
#include "unbufferStdout.h"
    int main() {
        unbufferStdout();
        noClearReallocTest(EXPAND);
        return 0;
    }
#endif
