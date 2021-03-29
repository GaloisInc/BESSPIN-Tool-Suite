#include <stdio.h>

#ifdef testgenOnFreeRTOS
    #error "This test does not support FreeRTOS"
#endif

int main(void);

int main() {
    int * pInt = NULL;
    printf("iDereference = <%d>!\n",*pInt); //This should cause a segfault
    return 0;
}