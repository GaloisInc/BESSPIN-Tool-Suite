#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

struct function_result*
fetch_resource(char *id)
{
    struct function_result *ret = test_malloc(sizeof (*ret));
    char *sep = strchr(id, ':');
    if (sep[1] == 'S') {
        ret->result = "SYSTEM_CONFIG";
        ret->size   = sizeof "SYSTEM_CONFIG";
    } else {
        ret->result = "USER_CONFIG";
        ret->size   = sizeof "USER_CONFIG";
    }
    return ret;
}

struct function_result*
sysconfig(struct smessage *msg)
{
    struct store_get_res *arg0 = store_get(msg->domain, SADDR(0,0));

    char id[10];

    // Attach domain to requested resource
    if (msg->domain >= 0) {
       sprintf(id, "%s:%c", arg0->result, 'U');
    } else if (msg->domain >= 0) {
       sprintf(id, "%s:%c", arg0->result, 'S');
    }

    return fetch_resource(id);
}
