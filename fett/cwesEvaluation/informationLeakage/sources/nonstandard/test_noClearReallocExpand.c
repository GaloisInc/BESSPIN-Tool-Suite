/* Test noClearReallocExpand */
#include "noClearRealloc.h"

#ifdef testgenOnFreeRTOS
    void main() {
        noClearReallocTest(EXPAND);
        return;
    }
#else
    int main() {
        noClearReallocTest(EXPAND);
        return 0;
    }
#endif