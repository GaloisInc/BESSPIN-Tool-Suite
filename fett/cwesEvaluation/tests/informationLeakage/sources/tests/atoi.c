//CWE:707
#include <stdlib.h>
#ifndef testgenOnFreeRTOS
#include <setjmp.h>
#endif
#include <string.h>
#include <stdio.h>
#include "types.h"
#include "control.h"
#include "stores.h"
#include "functions.h"
#include "interpreter.h"
#include <signal.h>
/**
This tests CWE-707 by issuing requests for negative offsets.
*/

#ifndef testgenOnFreeRTOS
sigjmp_buf point;
static void handler(int sig, siginfo_t*dc, void *ddc)
{
    longjmp(point, 1);
}
#endif

TEST_MAIN
{
#ifndef testgenOnFreeRTOS
    struct sigaction sa;
    struct sigaction sa_old_segv;
    struct sigaction sa_old_bus;
    memset(&sa, 0, sizeof(struct sigaction));
    sa.sa_flags     = SA_NODEFER;
    sa.sa_sigaction = handler;
    sigaction(SIGSEGV, &sa, &sa_old_segv);
    sigaction(SIGBUS, &sa, &sa_old_bus);

    sigaction(SIGSEGV, &sa_old_segv, NULL);
    sigaction(SIGBUS, &sa_old_bus, NULL);
#endif
    struct umessage msg;

    // Test setup:
    // (1) Set secret value if it's not static
    initialize_secret();
    store_init(0);

    int bound = (int)STORE_SIZE*(int)OBJ_SIZE;
    bound = (bound + 7) & (~8);

    // Search for the secret value by requesting negative
    // addresses. The interpreter ought to check for this
    // (but it doesn't -- hence the weakness.). The store
    // implementations are not guaranteed to do the right thing
    // with negative addresses. (Actually, they are designed
    // explicitly to do the wrong thing ;).)
    for (int i = 0; i >= -1*(int)STORE_SIZE; i--) {
        for (int k = 0; k >= (-2)*bound; k--) {
#ifndef testgenOnFreeRTOS
            if (setjmp(point) != 0) { continue; }
#endif
            // Flush cache if there is one
            get_msg(0, build_uaddr(1,0), &msg);
            struct smessage *smsg        = interpret_cmd(&msg);
            struct function_result *fres = run_command(smsg);
            test_free(smsg);
            test_free(fres->result);
            test_free(fres);

            // Build a message to do a lookup at (i,k)
            get_msg(0, build_uaddr(i,k), &msg);
            smsg        = interpret_cmd(&msg);

#ifndef testgenOnFreeRTOS
            sigaction(SIGSEGV, &sa, NULL);
            sigaction(SIGBUS, &sa, NULL);
#endif
            // Do the lookup
            fres = run_command(smsg);
#ifndef testgenOnFreeRTOS
            sigaction(SIGSEGV, &sa_old_segv, NULL);
            sigaction(SIGBUS, &sa_old_bus, NULL);
#endif
            if (fres && fres->result && matches_secret(fres->result)) {
                DEBUG_PRINTF("RESULT >> (%d, %d), >> %.*s\r\n",
                             i, k, (int)fres->size, fres->result);
                test_fail();
            }
            test_free(fres->result);
            test_free(fres);
            test_free(smsg);
        }
    }
    DEBUG_PRINTF("RESULT >> NONE\r\n");
    test_pass();
    return 0;
}
