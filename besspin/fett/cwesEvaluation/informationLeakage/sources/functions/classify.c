#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

// classify((0,0)) -> copy a value + secret to (0,1)
struct function_result *
classify(struct smessage *msg)
{
    char *pArgs = 1 + memchr(msg->m.gomsg.value, ':', msg->m.gomsg.size);

    saddr_t addr1;
    {
        memcpy(&addr1, pArgs, sizeof(saddr_t));
        pArgs += sizeof(saddr_t);
    }
    saddr_t addr2;
    {
        memcpy(&addr2, pArgs, sizeof(saddr_t));
        pArgs += sizeof(saddr_t);
    }
    struct store_get_res *arg    = store_get(msg->domain, addr1);
    struct store_get_res *secret = store_get(-1, SADDR(0,0));

    char buf[OBJ_SIZE] = {0};

    memcpy(buf, arg->result, strlen(arg->result));
    strncat(buf, secret->result, OBJ_SIZE-strlen(buf));
    store_set(msg->domain, addr2, buf, OBJ_SIZE);

    return NULL;
}
