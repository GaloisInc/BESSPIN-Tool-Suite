#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

struct function_result *
direct(struct smessage *msg)
{
    ARGP(msg->m.gomsg.value, msg->m.gomsg.size, pArgs);
    ARG(saddr_t, addr1, pArgs);
    struct store_get_res *arg = store_get(msg->domain, addr1);
    // Bug: -1 instead of correct domain
    int addr = *(int *)(arg->result);
#ifdef NO_WEAKNESS
    struct store_get_res *res  = store_get(msg->domain, addr);
#else
    struct store_get_res *res  = store_get(-1, addr);
#endif
    struct function_result *fres = test_malloc(sizeof(*fres));
    fres->result = test_malloc(res->size);
    strncpy(fres->result, res->result, res->size);
    fres->size = res->size;

    return fres;
}
