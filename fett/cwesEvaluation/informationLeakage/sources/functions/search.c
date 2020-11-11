#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "types.h"
#include "stores.h"
#include "functions.h"

#ifndef RESULT_SIZE
#define RESULT_SIZE 257
#endif

struct function_result *
search(struct smessage *msg)
{
    const char *search_term = store_get(msg->domain, SADDR(0,0))->result;
    struct function_result *index_ret = test_malloc(sizeof(*index_ret));
    index_ret->result = test_malloc(RESULT_SIZE);
    index_ret->size   = 0;
    size_t result_ptr = 0;
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
            char *p;
            if ((p = strstr(get->result, search_term))) {
                // This can be modulated to accumulate results etc
                if (get->result + OBJ_SIZE < p)
                    p -= OBJ_SIZE;
                else
                    p = get->result;

                strncat(index_ret->result, p, RESULT_SIZE - result_ptr);
                int a = RESULT_SIZE - result_ptr;
                int b = strnlen(p, OBJ_SIZE - (p - get->result));
                result_ptr += (a < b) ? a : b;
            }
        }
#ifdef NO_WEAKNESS
#else
    }
    index_ret->size   = result_ptr;
#endif

    return index_ret;
}
