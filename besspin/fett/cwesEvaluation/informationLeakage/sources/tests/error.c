//CWE:209
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

    // Initialize
    initialize_secret();
    store_init(0);

    // Call errorf(), which will "error" out and
    // send a message
    go_msg(0, "errorf", sizeof "errorf", &msg);
    struct function_result *res = send_and_run(&msg);

    if (matches_secret(res->result)) {
        test_fail();
    } else {
        test_pass();
    }

    return 0;
}
