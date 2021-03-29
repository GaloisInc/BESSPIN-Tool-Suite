//CWE:203
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

    // Set the privileged domain username
    set_msg(-1, build_uaddr(0,0), "ADMIN_USER", sizeof "ADMIN_USER", &msg);
    struct smessage *smsg        = interpret_cmd(&msg);
    struct function_result *fres = run_command(smsg);

    // Set the privileged domain password
    set_msg(-1, build_uaddr(1,0), "ADMIN_PASS", sizeof "ADMIN_PASS", &msg);
    smsg = interpret_cmd(&msg);
    fres = run_command(smsg);

    // Now set the login attempt username
    set_msg(0, build_uaddr(0,0), "ADA", sizeof "ADA", &msg);
    smsg = interpret_cmd(&msg);
    fres = run_command(smsg);

    // Now set the login attempt password
    set_msg(0, build_uaddr(1,0), "LOVELACE", sizeof "LOVELACE", &msg);
    smsg = interpret_cmd(&msg);
    fres = run_command(smsg);

    // Try to login() using the login attempt credentials,
    // and remember the message
    go_msg(0, "login", strlen("login"), &msg);
    smsg = interpret_cmd(&msg);
    fres = run_command(smsg);
    char *s1 = fres->result;

    // Now change the login attempt username to the admin username
    set_msg(0, build_uaddr(0,0), "ADMIN_USER", sizeof "ADMIN_USER", &msg);
    smsg = interpret_cmd(&msg);
    fres = run_command(smsg);

    // ... and attempt to login again, recording the message.
    msg.type = GO;
    go_msg(0, "login", strlen("login"), &msg);
    smsg = interpret_cmd(&msg);
    fres = run_command(smsg);
    char *s2 = fres->result;

    DEBUG_PRINTF("RESULT >> %s %c= %s\n",
                 s1,
                 strcmp(s1,s2) ? '!' : '=',
                 s2);
    // In the first login attempt, the username/password are both wrong.
    // In the second login attempt, the username is correct.
    // If the error message allows the attacker to distinguish these cases,
    // then that is a weakness.
    if (!strcmp(s1,s2)) {
        test_pass();
    } else {
        test_fail();
    }

    return 0;
}
