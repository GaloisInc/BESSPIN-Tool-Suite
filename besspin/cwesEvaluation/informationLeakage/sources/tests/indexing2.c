//CWE:612
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
    initialize_secret();
    store_init(0);

    struct umessage msg;
    set_msg(0, build_uaddr(0,0), "#!", sizeof "#!", &msg);
    (void)send_and_run(&msg);
    set_msg(0, build_uaddr(1,0), "#!", sizeof "#!", &msg);
    (void)send_and_run(&msg);

    // Call search2().
    // Search2 is hardcoded to look in (0,0) for the search term.
    // This operation will scan _all_ of the store for data containing
    // the search term (even though it shouldn't).
    go_msg(0, "search2", sizeof "search2", &msg);
    struct function_result *res = send_and_run(&msg);

    DEBUG_PRINTF("RESULT >> %.*s\r\n", res->size, res->result);
    if (matches_secret(res->result)) {
        test_fail();
    } else {
        test_pass();
    }
    return 0;
}
