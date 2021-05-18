//CWE:201
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

    // Set (0,0) to SADDR(0,0)
    int value = SADDR(0,0);
    set_msg(0, build_uaddr(0,0), &value, sizeof(value), &msg);
    (void)send_and_run(&msg);

    // Now call direct(addr1) which
    // will fetch the PRIVILEGED DOMAIN's object at (0,0)
    // and return it. (This is bad ;).)
    saddr_t addr1 = SADDR(0,0);
    ARG_BUF(buf, "direct", sizeof(addr1));
    ARG_PUT(buf, addr1);
    go_msg(0, buf, sizeof buf, &msg);
    struct function_result *res = send_and_run(&msg);

    DEBUG_PRINTF("RESULT >> %.*s\r\n", res->size, res->result);
    if (matches_secret(res->result)) {
        test_fail();
    } else {
        test_pass();
    }
    return 0;
}
