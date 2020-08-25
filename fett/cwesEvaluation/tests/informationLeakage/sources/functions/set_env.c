#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

struct function_result *
set_env(struct smessage *msg)
{
#ifdef testgenOnFreeRTOS
    test_not_implemented();
#endif
    struct function_result *res = NULL;
    struct store_get_res *arg0  = store_get(msg->domain, SADDR(0,0));
    struct store_get_res *arg1  = store_get(msg->domain, SADDR(1,0));
    saddr_t *addr = (saddr_t *)arg1->result;
    struct store_get_res *val   = store_get(-1, *addr);
#ifndef NO_WEAKNESS
    setenv(arg0->result, val->result, 1);
#endif

    return res;
}
