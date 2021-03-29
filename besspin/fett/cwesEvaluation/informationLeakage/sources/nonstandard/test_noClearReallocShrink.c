/* Test noClearReallocShrink */
#include "noClearRealloc.h"

#ifdef testgenOnFreeRTOS
    void main() {
        noClearReallocTest(SHRINK);
        return;
    }
#else
#include "unbufferStdout.h"
    int main() {
        unbufferStdout();
        noClearReallocTest(SHRINK);
        return 0;
    }
#endif
