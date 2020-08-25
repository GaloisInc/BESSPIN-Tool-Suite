#ifndef __STORES_H__
#define __STORES_H__
#include "types.h"
#include <stddef.h>

struct store_get_res {
    char *result;
    size_t size;
};

// Initialize the secret, user, and public stores.
// The initialization function *may* use the argument
// for some special setup.
// After initialization, it is guaranteed that domain -1
// has a 'secret' value stored in it somewhere
void
store_init(int principal_domain);

// @requires: domain \in N
// Behavior: reads addr in domain IF addr is in bounds (0 to NOBJS * OBJSIZE)
//           otherwise, addr overflows to other domains
// -1 : privileged system domain
// -2 : public domain
struct store_get_res *
store_get(int domain, saddr_t addr);

// As store_get, but sets object at addr.
void
store_set(int domain, saddr_t addr, char *value, size_t size);
#endif
