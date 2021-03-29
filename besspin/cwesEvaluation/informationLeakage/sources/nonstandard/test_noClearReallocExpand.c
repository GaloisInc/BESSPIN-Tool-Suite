/* Test noClearReallocExpand */
#include "noClearRealloc.h"

#ifdef BESSPIN_FREERTOS
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
