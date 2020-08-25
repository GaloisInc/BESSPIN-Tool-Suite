//CWE:707
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "types.h"
#include "stores.h"
#include "control.h"
#include "functions.h"
#include "interpreter.h"

TEST_MAIN
{
    struct umessage msg;

    // Initialization
    initialize_secret();
    store_init(0);

    // sysconfig() will look at the store at (0,0) for a command.
    // sysconfig will 'tag' the untrusted command (1) with :U (and will
    // check for this tag later). However, we are "injecting" a tag
    // here with ":S". Since this is not properly scrubbed, we can
    // hijack the control of the function, tricking it into executing
    // in privileged mode.
    set_msg(0, build_uaddr(0,0), "1:S", sizeof "1:S", &msg);
    struct smessage *smsg        = interpret_cmd(&msg);
    struct function_result *fres = run_command(smsg);
    go_msg(0, "sysconfig", strlen("sysconfig"), &msg);
    smsg = interpret_cmd(&msg);
    fres = run_command(smsg);
    char *res1 = fres->result;
    test_free(smsg);
    test_free(fres);

    // Now send a message _without_ trying to hijack control.
    set_msg(0, build_uaddr(0,0), "1", sizeof "1", &msg);
    smsg        = interpret_cmd(&msg);
    fres = run_command(smsg);
    test_free(smsg);
    test_free(fres);

    go_msg(0, "sysconfig", strlen("sysconfig"), &msg);
    smsg = interpret_cmd(&msg);
    fres = run_command(smsg);
    char *res2 = fres->result;
    test_free(smsg);
    test_free(fres);

    DEBUG_PRINTF("%s %s\r\n", res1, res2);
    // If the messages are different, then we were able to influence
    // control-flow using the message, which was improperly checked.
    if (res1 && res2 && (0 == strcmp(res1, res2))) {
        test_pass();
    } else {
        test_fail();
    }

    return 0;
}
