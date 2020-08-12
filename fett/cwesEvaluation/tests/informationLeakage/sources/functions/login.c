#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

struct function_result*
login(struct smessage *msg)
{
    struct store_get_res *user      = store_get(msg->domain, SADDR(0,0));
    struct store_get_res *pass      = store_get(msg->domain, SADDR(1,0));
    struct store_get_res *adminuser = store_get(-1, SADDR(0,0));
    struct store_get_res *adminpass = store_get(-1, SADDR(1,0));
    struct function_result *ret = test_malloc(sizeof(*ret));
    #define CONST_RESPONSE(_k)                      \
        ret->result = _k;                           \
        ret->size   = sizeof _k

    if (!strcmp(user->result,adminuser->result)) {
        if(!strcmp(pass->result,adminpass->result)) {
            CONST_RESPONSE("OK");
        } else {
#ifdef NO_WEAKNESS
            CONST_RESPONSE("ERR:PASS_OR_USERNAME");
#else
            CONST_RESPONSE("ERR:PASS");
#endif
        }
    } else {
#ifdef NO_WEAKNESS
        CONST_RESPONSE("ERR:PASS_OR_USERNAME");
#else
        CONST_RESPONSE("ERR:USERNAME");
#endif
    }

    return ret;
}
