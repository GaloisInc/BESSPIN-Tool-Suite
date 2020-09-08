#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

//broadcast(addr):
struct function_result *
broadcast(struct smessage *msg)
{
    ARGP(msg->m.gomsg.value, msg->m.gomsg.size, pArgs);
    ARG(saddr_t, addr, pArgs);

    struct store_get_res *val = store_get(msg->domain, addr);
    char buf[OBJ_SIZE] = {0};
#ifdef NO_WEAKNESS
    scrub(val->result, val->size, buf);
#else
    memcpy(buf, val->result, val->size);
#endif
    store_set(-2, addr, buf, val->size);
    return NULL;
}
