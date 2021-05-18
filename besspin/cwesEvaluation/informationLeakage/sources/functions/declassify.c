#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

struct function_result *
declassify(struct smessage *msg)
{
    ARGP(msg->m.gomsg.value, msg->m.gomsg.size, pArgs);
    ARG(saddr_t, addr1, pArgs);
    struct store_get_res *arg    = store_get(msg->domain, addr1);
    struct function_result *res  = test_malloc(sizeof(*res));
    char buf[OBJ_SIZE] = {0};
#ifdef NO_WEAKNESS
    scrub(arg->result, arg->size, buf);
#else
    memcpy(buf, arg->result, arg->size);
#endif
    res->size = arg->size;
    res->result = test_malloc(sizeof buf);
    memcpy(res->result, buf, sizeof buf);

    return res;
}
