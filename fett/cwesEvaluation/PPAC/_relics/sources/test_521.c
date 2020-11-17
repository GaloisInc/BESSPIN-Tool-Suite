/*
Test_521: Weak Password Requirements
*/
#ifdef testgenOnFreeRTOS
#include "testgenFreeRTOS.h"

TaskHandle_t xMainTask = NULL;
UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.

#include <stdio.h>
void main_test_259(void);
void main(void) {
    printf("<NOT-IMPLEMENTED> This test is not implemented yet for FreeRTOS.\n");
}

#elif defined(testgenOnDebian) || defined(testgenOnFreeBSD)

#define THIS_TEST "521"
#define PAM_PREFIX "pam_"
#define MY_CONFIG PAM_PREFIX THIS_TEST

#include <sys/types.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <security/pam_appl.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

#ifdef testgenOnDebian
#include <security/pam_misc.h>
#include <security/pam_ext.h>
static struct pam_conv conv = { misc_conv, NULL };
#else //FreeBSD
#include <security/openpam.h>
static struct pam_conv conv = { openpam_ttyconv, NULL };
#endif

#define CHECK(f, ...)                           \
    do {                                        \
        pamOK = f(__VA_ARGS__);                 \
        if (pamOK != PAM_SUCCESS) goto error;   \
        printf(">>> " #f " successful\n");     \
    } while (0);

int main (int argc, char **argv)
{
    pam_handle_t *pamh;
    int pamOK;

    CHECK(pam_start, MY_CONFIG, argv[1], &conv, &pamh);
    CHECK(pam_authenticate, pamh, 0);
    pamOK = pam_chauthtok(pamh, 0);
    if (pamOK == PAM_SUCCESS) {
        printf("<GRANTED> Password change successful\n");
    } else if (pamOK == PAM_PERM_DENIED) {
        printf("<DENIED> Password change denied\n");
    } else {
        goto error;
    }
    CHECK(pam_end, pamh, 0);
    return 0;

 error:
    pam_error(pamh, "<INVALID> %s\n", pam_strerror(pamh, pamOK));
    return 1;
}
#endif
