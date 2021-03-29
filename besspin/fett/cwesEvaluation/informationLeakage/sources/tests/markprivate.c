//CWE:212
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

    // Call mark_private(SADDR(1,0), SECRET_PATTERN),
    // which adds private data (SECRET_PATTERN) to the object at (1,0).
    int8_t id = 1;
    int8_t off = 0;
    saddr_t addr = SADDR(id,off);
    ARG_BUF(cmd1, "mark_private", sizeof(addr) + sizeof(SECRET_PATTERN));
    ARG_PUT(cmd1, addr);
    memcpy(&cmd1[cmd1_idx], SECRET_PATTERN, sizeof(SECRET_PATTERN));
    go_msg(0, cmd1, sizeof(cmd1), &msg);
    send_and_run(&msg);

    // Call broadcast(addr), which copies the value stored at
    // address `addr` to the PUBLIC domain (and really ought
    // to scrub the data first).
    ARG_BUF(cmd2, "broadcast", sizeof(addr));
    ARG_PUT(cmd2, addr);
    go_msg(0, cmd2, sizeof cmd2, &msg);
    send_and_run(&msg);

    // Check the public domain at `addr`.
    get_msg(-2, build_uaddr(id, off), &msg);
    struct function_result *res = send_and_run(&msg);
    DEBUG_PRINTF("RESULT >> %.*s\r\n", res->size, res->result);
    if (matches_secret(res->result)) {
        test_fail();
    } else {
        test_pass();
    }
    return 0;
}
