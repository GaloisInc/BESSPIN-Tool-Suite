//CWE:526
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "types.h"
#include "control.h"
#include "stores.h"
#include "functions.h"
#include "interpreter.h"

TEST_MAIN
{
    struct umessage msg;

    // Test setup:
    // (1) Set secret value if it's not static
    initialize_secret();
    // (2) Initialize store
    store_init(0);

    // Set store[0,0] := "FOO"
    set_msg(0, build_uaddr(0,0), "FOO", sizeof "FOO", &msg);
    (void)send_and_run(&msg);

    // Set store[1,0] := SADDR(0,0)
    saddr_t value = SADDR(0,0);
    set_msg(0, build_uaddr(1,0), &value, sizeof(value), &msg);
    (void)send_and_run(&msg);

    // Call set_env() which will load store[0,0] into env[FOO]
    go_msg(0, "set_env", sizeof "set_env", &msg);
    struct function_result *res = send_and_run(&msg);

    // Now check to see if the value made its way
    // into the observable environment
    char *env_result = getenv("FOO");
    if (env_result) {
        DEBUG_PRINTF("RESULT >> %s\r\n", env_result);
        if (matches_secret(env_result)) {
            test_fail();
        } else {
            test_pass();
        }
    } else {
        DEBUG_PRINTF("RESULT >> $FOO NOT SET\r\n");
        test_pass();
    }
    return 0;
}
