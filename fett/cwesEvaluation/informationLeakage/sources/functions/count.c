#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

struct function_result *
count(struct smessage *msg)
{
    const char *search_term = store_get(msg->domain, SADDR(0,0))->result;
    struct function_result *index_ret = test_malloc(sizeof(*index_ret));
    index_ret->result = NULL;
    index_ret->size = 0;
#ifdef NO_WEAKNESS
    int d = msg->domain;
#else
    for (int d = -1; d < NDOMAINS; d++) {
#endif
        for (int i = 0; i < STORE_SIZE; i++) {
            // This is where the search term is stored.
            if (d == msg->domain && i == 0)
                continue;

            struct store_get_res *get = store_get(d, SADDR(i,0));
            if (strstr(get->result, search_term)) {
                // This can be modulated to accumulate results etc
                index_ret->result = "HIT";
                index_ret->size   = sizeof "HIT";
            }
        }
#ifdef NO_WEAKNESS
#else
    }
#endif

    return index_ret;
}
