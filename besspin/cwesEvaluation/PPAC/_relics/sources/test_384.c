/*
Test_384: Session Fixation
*/
#ifdef testgenOnFreeRTOS
#include "testgenFreeRTOS.h"

TaskHandle_t xMainTask = NULL;
UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.

#include <stdio.h>
void main(void) {
    printf("<NOT-IMPLEMENTED> This test is not implemented yet for FreeRTOS.\n");
}

#elif defined(testgenOnDebian) || defined(testgenOnFreeBSD)

#define THIS_TEST "384"
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
    int user = 1;
    int session_up = 0;

    CHECK(pam_start, MY_CONFIG, argv[user], &conv, &pamh);
    while (user++ < argc) {
        char *username;
        CHECK(pam_get_item, pamh, PAM_USER, &username);
        CHECK(pam_authenticate, pamh, 0);
        if (!session_up) {
#ifdef testgenOnFreeBSD
            char SESSION_ID[256] = {0};
            strcpy(SESSION_ID, username);
            strcat(SESSION_ID, ":1234");
            CHECK(pam_setenv, pamh, "SESSION_ID", SESSION_ID, 1);
#else
            CHECK(pam_open_session, pamh, 0);
#endif
            session_up = 1;
        }
        char *id = pam_getenv(pamh, "SESSION_ID");
        printf("%s.SESSION_ID=%s\n", username, id);
        // weakness: no pam_close_session
        pam_set_item(pamh, PAM_USER, argv[user]);
    } while (user < argc);
    CHECK(pam_end, pamh, 0);
    return 0;

 error:
    pam_error(pamh, "<INVALID> %s\n", pam_strerror(pamh, pamOK));
    return 1;
}
#endif
