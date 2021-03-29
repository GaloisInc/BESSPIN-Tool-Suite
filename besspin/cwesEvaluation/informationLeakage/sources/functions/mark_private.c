#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "control.h"
#include "stores.h"
#include "functions.h"

//mark_private(OBJ_ID, OFFSET, PRIVATE_VALUE):
struct function_result *
mark_private(struct smessage *msg)
{
    ARGP(msg->m.gomsg.value, msg->m.gomsg.size, pArgs);
    ARG(saddr_t, addr, pArgs);
    store_set(msg->domain, addr, pArgs, strlen(pArgs)+1);

    return NULL;
}
