#include "types.h"
#include "stores.h"
#include "control.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
char *STORE_IMPL   = "FRAGMENTED";

char *__STORE_CWES = "";

struct store_obj {
    int domain;
    saddr_t addr;
    char data[OBJ_SIZE + 1];
};

#ifdef __IEX_GEN__ARRAYS__
struct store_obj public_store[STORE_SIZE]   = {0};
struct store_obj system_store_a[STORE_SIZE] = {0};
struct store_obj store[NDOMAINS*STORE_SIZE] = {0};
struct store_obj system_store_b[STORE_SIZE] = {0};
#else
struct store_obj *public_store;
struct store_obj *system_store_a;
struct store_obj *store;
struct store_obj *system_store_b;
#endif

#define DEBUG_MEM(_dom, _addr) \
    DEBUG_PRINTF("Reading MEM(%d, %d) (%p, %p, %p)\r\n", \
           _dom, _addr,                             \
           store, &MEM(_dom, 0), &MEM(_dom, _addr))

#define P0 1  // some prime non-divisor of NDOMAINS   (which is a power of 2)
#define P1 1 // some prime non-divisor of STORE_SIZE (which is a power of 2)

void
store_init(int domain)
{
#ifndef __IEX_GEN__ARRAYS__
    public_store = test_malloc(STORE_SIZE*sizeof(struct store_obj));
    system_store_a = test_malloc(STORE_SIZE*sizeof(struct store_obj));
    store = test_malloc(NDOMAINS*STORE_SIZE*sizeof(struct store_obj));
    system_store_b = test_malloc(STORE_SIZE*sizeof(struct store_obj));
#endif
    int p = 0;
    for(int i = 0; i < STORE_SIZE; i++) {
        system_store_a[i].domain = -1;
        system_store_a[i].addr = i;
        system_store_b[i].domain = -1;
        system_store_b[i].addr = i;
        public_store[i].domain  = -2;
        public_store[i].addr = i;
        MEMCPYSECRET(system_store_a[i].data);
        MEMCPYSECRET(system_store_b[i].data);
        for (int d = 0; d < NDOMAINS; d++) {
            int dom = (d*P0) % NDOMAINS;
            int addr = (i*P1) % STORE_SIZE;
            store[p].domain = dom;
            store[p].addr   = addr;
            p++;
        }
    }

    for (int p = 0; p < NDOMAINS*STORE_SIZE; p++) {
        DEBUG_PRINTF("STORE[%d] = { %d, %d, %.*s }\n",
               p, store[p].domain, store[p].addr, (int)OBJ_SIZE, store[p].data);
    }
}

struct store_obj*
find(int domain, saddr_t addr)
{
    unsigned char obj = OBJ_ADDR(addr);
    DEBUG_PRINTF("FINDING (%d, %x)\r\n", domain, obj);
    struct store_obj *ret = NULL;

    if (domain < 0) {
        struct store_obj *pstore = (domain == -1) ? system_store_a : public_store;
        for (int p = 0; ret == NULL && p < STORE_SIZE; p++) {
            if (pstore[p].addr == obj) {
                DEBUG_PRINTF(">>> FOUND AT %d\r\n", p);
                ret = &pstore[p];
            }
        }
    } else {
        for (int p = 0; ret == NULL && p < NDOMAINS*STORE_SIZE; p++) {
            if (store[p].domain == domain && store[p].addr == obj) {
                DEBUG_PRINTF(">>> FOUND AT %d\r\n", p);
                ret = &store[p];
            }
        }
    }

    return ret;
}

struct store_get_res*
store_get(int domain, saddr_t addr)
{
    unsigned int obj = OBJ_ADDR(addr);
    int off = OBJ_OFF(addr);
    struct store_get_res *ret = test_malloc(sizeof(*ret));
    ret->size   = OBJ_SIZE;
    ret->result = test_malloc(OBJ_SIZE);

    struct store_obj *target = NULL;
    target = find(domain, addr);

    if (target) {
        DEBUG_PRINTF("OFFSET: %d\r\n", off);
        memcpy(ret->result, target->data + off, OBJ_SIZE);
    }

    return ret;
}

void
store_set(int domain, saddr_t addr, char *value, size_t size)
{
    struct store_obj *target = NULL;
    int obj = OBJ_ADDR(addr);
    int off = OBJ_OFF(addr);

    target = find(domain, addr);
    size_t min = size < OBJ_SIZE ? size : OBJ_SIZE;
    DEBUG_PRINTF("SET %d %d %d <- \"%.*s\" (%d)\n", domain, obj, off, (int)min, value, (int)min);
    memcpy(target->data, value + off, min);

    return;
}
