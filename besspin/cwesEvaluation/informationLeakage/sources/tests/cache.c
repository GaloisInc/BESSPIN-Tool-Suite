//CWE:524
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
    if (strcmp(STORE_IMPL, "CACHED")) {
        printf("<NO-WEAKNESS>\r\n");
        test_not_implemented();
    } else {
    }
    struct umessage msg;
    struct smessage *smsg;
    struct function_result *fres;

    // Initialization
    initialize_secret();
    store_init(0);

    // Issue a read for the privileged domain
    // in order to bring the value into the cache
    get_msg(-1, build_uaddr(0,0), &msg);
    smsg = interpret_cmd(&msg);
    fres = run_command(smsg);
    test_free(smsg);
    test_free(fres);

    // Now set the object with the same address in a
    // different domain. This should evict the cached
    // element. If the cache does not properly
    // clear any private data, then that's a problem. We issue
    // an "empty" write here in order to avoid accidentally
    // overwriting the cached data (which would mask the bug).
    set_msg(0, build_uaddr(0,0), "", 0, &msg);
    smsg        = interpret_cmd(&msg);
    fres = run_command(smsg);
    test_free(smsg);

    // Finally, issue a read for the object we just wrote.
    // In a correct implementation, we would get back "", but
    // we'll check that at the end...
    get_msg(0, build_uaddr(0,0), &msg);
    smsg        = interpret_cmd(&msg);
    fres = run_command(smsg);
    test_free(smsg);

    DEBUG_PRINTF("RESULT >> %.*s\r\n", (int)fres->size, fres->result);
    if (matches_secret(fres->result)) {
        test_fail();
    } else {
        test_pass();
    }

    return 0;
}
