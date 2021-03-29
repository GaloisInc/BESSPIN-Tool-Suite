#include "types.h"
#include "stores.h"
#include "control.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
char *STORE_IMPL   = "SEPARATE";

#if NDOMAINS > 5
#error "STORE=separate only supports 5 or fewer stores"
#endif

const size_t store_size = OBJ_SIZE*STORE_SIZE*NDOMAINS;
// TODO: what to do here?
#ifdef __IEX_GEN__ARRAYS__
static char public_store[OBJ_SIZE*STORE_SIZE] = {0};
static char store_secret[OBJ_SIZE*STORE_SIZE] = {0};
static char store_0[OBJ_SIZE*STORE_SIZE] = {0};
#if NDOMAINS > 1
static char store_1[OBJ_SIZE*STORE_SIZE] = {0};
#endif
#if NDOMAINS > 2
static char store_2[OBJ_SIZE*STORE_SIZE] = {0};
#endif
#if NDOMAINS > 3
static char store_3[OBJ_SIZE*STORE_SIZE] = {0};
#endif
#if NDOMAINS > 4
static char store_4[OBJ_SIZE*STORE_SIZE] = {0};
#endif
#else
static char *public_store;
static char *store_0;
#if NDOMAINS > 1
static char *store_1;
#endif
#if NDOMAINS > 2
static char *store_2;
#endif
#if NDOMAINS > 3
static char *store_3;
#endif
#if NDOMAINS > 4
static char *store_4;
#endif
#if NDOMAINS > 5
static char *store_5;
#endif
static char *store_secret;
#endif

#ifdef __IEX_GEN__ARRAYS__
static char *store_table[] = { store_0,
#if NDOMAINS > 1
                               store_1,
#endif
#if NDOMAINS > 2
                               store_2,
#endif
#if NDOMAINS > 3
                               store_3,
#endif
#if NDOMAINS > 4
                               store_4,
#endif
};
static char *neg_table[2] = { public_store, store_secret };
#else
static char *store_table[5];
static char *neg_table[2];
#endif


#define DEBUG_MEM(_dom, _addr) \
    printf("Reading MEM(%d, %d) (%p, %p, %p)\r\n", \
           _dom, _addr,                             \
           store, &MEM(_dom, 0), &MEM(_dom, _addr))

#define ADDR_SADDR(_addr)                       \
    (OBJ_ADDR(_addr)*OBJ_SIZE + OBJ_OFF(_addr))

#define LMEM(_dom, _addr) \
    ((_dom < 0) ? &neg_table[_dom + 2][ADDR_SADDR(_addr)] : &store_table[_dom][ADDR_SADDR(_addr)])
#define MEM(_dom, _addr) \
    ((_dom < 0) ? neg_table[_dom + 2][ADDR_SADDR(_addr)] : store_table[_dom][ADDR_SADDR(_addr)])

void
store_init(int domain)
{
#ifndef __IEX_GEN__ARRAYS__
    public_store    = test_malloc(OBJ_SIZE*STORE_SIZE);
    store_secret    = test_malloc(OBJ_SIZE*STORE_SIZE);
    neg_table[0]    = public_store;
    neg_table[1]    = store_secret;
    store_0         = test_malloc(OBJ_SIZE*STORE_SIZE);
    store_table[0] = &store_0[0];
#if NDOMAINS > 1
    store_1         = test_malloc(OBJ_SIZE*STORE_SIZE);
    store_table[1] = &store_1[0];
#endif
#if NDOMAINS > 2
    store_2         = test_malloc(OBJ_SIZE*STORE_SIZE);
    public_store[2] = store_2;
#endif
#if NDOMAINS > 3
    store_3         = test_malloc(OBJ_SIZE*STORE_SIZE);
    public_store[3] = store_3;
#endif
#if NDOMAINS > 4
    store_4         = test_malloc(OBJ_SIZE*STORE_SIZE);
    public_store[4] = store_4;
#endif
#endif
    MEMCPYSECRET(store_secret);
}

struct store_get_res*
store_get(int domain, saddr_t addr)
{
#ifdef DEBUG
    printf("GET(%d, (%d, %d)) >> ", domain, OBJ_ADDR(addr), (char)OBJ_OFF(addr));
#endif
    struct store_get_res *ret = test_malloc(sizeof(*ret));
    ret->size   = OBJ_SIZE;
    ret->result = test_malloc(OBJ_SIZE);

#ifdef DEBUG
    printf("%p >> ", LMEM(domain, addr));
#endif
    memcpy(ret->result, LMEM(domain, addr), OBJ_SIZE);

#ifdef DEBUG
    printf("\"%.*s\"\r\n", ret->size, ret->result);
#endif

    return ret;
}

void
store_set(int domain, saddr_t addr, char *value, size_t size)
{
    memcpy(LMEM(domain, addr), value, size);
}
