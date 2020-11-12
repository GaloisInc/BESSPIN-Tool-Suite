//CWE:226
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

    // initialization
    initialize_secret();
    store_init(0);

    saddr_t addr1 = SADDR(0,0);
    saddr_t addr2 = SADDR(1,0);

    // Set 0's store[0,0] to some low-security value
    set_msg(0, build_uaddr(0,0), "PUBLIC", sizeof "PUBLIC"-1, &msg);
    send_and_run(&msg);

    // Build "classify(addr1, addr2)" which will
    // "stamp" the value in addr1 with a private value and
    // store this result in (1,0)
    ARG_BUF(buf, "classify", sizeof(addr1) + sizeof(addr2));
    ARG_PUT(buf, addr1);
    ARG_PUT(buf, addr2);
    go_msg(0, buf, sizeof(buf), &msg);
    send_and_run(&msg);

    // Build "declassify(addr2)" which will
    // "scrub" the value in addr2 and return it.
    // So we expect to receive a value that does not
    // have any private information in it.
    ARG_BUF(buf2, "declassify", sizeof(addr2));
    ARG_PUT(buf2, addr2);
    go_msg(0, buf2, sizeof(buf2), &msg);
    struct function_result *res = send_and_run(&msg);

    DEBUG_PRINTF("RESULT >> %.*s\r\n", (int)res->size, res->result);
    if (matches_secret(res->result)) {
        test_fail();
    } else {
        test_pass();
    }
    return 0;
}
