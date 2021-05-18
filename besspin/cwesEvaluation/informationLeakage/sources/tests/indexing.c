//CWE:202,612
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

    initialize_secret();
    store_init(0);

    // Set store(0,0) to a component of the secret message.
    set_msg(0, build_uaddr(0,0), "#!", sizeof "#!", &msg);
    (void)send_and_run(&msg);

    // Call search().
    // Search is hardcoded to look in (0,0) for the search term.
    // This operation will scan _all_ of the store for data containing
    // the search term (even though it shouldn't), and return
    // the number of matches
    go_msg(0, "search", sizeof "search", &msg);
    struct function_result *res = send_and_run(&msg);

    DEBUG_PRINTF("RESULT >> %.*s\r\n", res->size, res->result);
    if (res->size > 0) {
        test_fail();
    } else {
        test_pass();
    }
    return 0;
}
