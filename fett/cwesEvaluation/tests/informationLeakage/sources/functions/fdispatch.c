#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

struct function_result*
run_command(struct smessage *msg)
{
    struct function_result *ret = test_malloc(sizeof(*ret));
    puts("malloc function res\r\n");
    struct store_get_res *res   = NULL;

    switch (msg->type) {
    case GET:
        res = store_get(msg->domain, msg->m.getmsg.address);
        if (res) {
            ret->result = res->result;
            ret->size   = res->size;
        }
        if (res) {
            test_free(res);
        }
        break;
    case SET:
        store_set(msg->domain, msg->m.setmsg.address, msg->m.setmsg.value, msg->m.setmsg.size);
        break;
    case GO: {
        for(size_t i = 0; i < n_functions; i++) {
            size_t name_len = strcspn(function_tab[i].name, ":");
            if (!strncmp(function_tab[i].name, msg->m.gomsg.value, name_len)) {
                return function_tab[i].fn(msg);
            }
        }
        break;
    }
    default:
        return NULL;
    }

    return ret;
}
