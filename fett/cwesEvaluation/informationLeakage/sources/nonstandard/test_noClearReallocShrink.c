/* Test noClearReallocShrink */
#include "noClearRealloc.h"

#ifdef testgenOnFreeRTOS
    void main() {
        noClearReallocTest(SHRINK);
        return;
    }
#else
    int main() {
        noClearReallocTest(SHRINK);
        return 0;
    }
#endif