#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

struct function_result *
errorf(struct smessage *msg)
{
    struct store_get_res *res = store_get(-1, SADDR(0,0));

    struct function_result *fres = test_malloc(sizeof(*fres));
    char error_str[OBJ_SIZE + sizeof("ERR_WITH_KEY: ") - 1];
    strncpy(error_str, "ERR_WITH_KEY: ", sizeof error_str);
#ifdef NO_WEAKNESS
    // Don't copy the 'key' to the error message
#else
    strncat(error_str, res->result, sizeof error_str - sizeof "ERR_WITH_KEY: " + 1);
#endif
    fres->result = test_malloc(sizeof(error_str));
    memcpy(fres->result, error_str, sizeof(error_str));
    fres->size   = sizeof(error_str);

    return fres;
}
