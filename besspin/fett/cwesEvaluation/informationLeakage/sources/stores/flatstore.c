#include "types.h"
#include "stores.h"
#include "control.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
char *STORE_IMPL   = "FLATSTORE";

const size_t store_size = OBJ_SIZE*STORE_SIZE*NDOMAINS;

#ifdef __IEX_GEN__ARRAYS__
static char public_store[OBJ_SIZE*STORE_SIZE] =  {0};
static char system_store[OBJ_SIZE*STORE_SIZE] =  {0};
static char store[OBJ_SIZE*STORE_SIZE*NDOMAINS] = {0};
#else
static char *public_store;
static char *system_store;
static char *store;
#endif

#ifdef DEBUG
#define DEBUG_MEM(_dom, _addr) \
    printf("Reading MEM(%d, %d[%d]) (%p, %p, %p)\r\n", \
           _dom, OBJ_ADDR(_addr), OBJ_OFF(_addr),      \
           store, LMEM(_dom, 0), LMEM(_dom, _addr))
#else
#define DEBUG_MEM(_dom, _addr_)
#endif

//#define ADDR_SADDR(_addr)                                             \
    //    (((int8_t)OBJ_ADDR(_addr)*OBJ_SIZE) + (int8_t)OBJ_OFF(_addr))
signed int
ADDR_SADDR(int16_t addr)
{
    int p = OBJ_ADDR(addr)*OBJ_SIZE;
    int o = OBJ_OFF(addr);
    return p + o;
}


#define LMEM(_dom, _addr)                          \
    (((_dom) >= 0) ?                              \
     &store[((_dom)*STORE_SIZE*OBJ_SIZE) + ADDR_SADDR(_addr)] \
     : (((_dom) == -1) ? &system_store[ADDR_SADDR(_addr)] : &public_store[ADDR_SADDR(_addr)]))
#define MEM(_dom, _addr) \
    (((_dom) >= 0) ?                                                    \
     store[((_dom)*STORE_SIZE*OBJ_SIZE) + ADDR_SADDR(_addr)]           \
     : (((_dom) == -1) ? system_store[ADDR_SADDR(_addr)] :public_store[ADDR_SADDR(_addr)]))

#define SYS_MEM(_addr)                        \
    system_store[_addr]


void
store_init(int domain)
{
#ifndef __IEX_GEN__ARRAYS__
    public_store = test_malloc(OBJ_SIZE*STORE_SIZE);
    memset(public_store, 0, OBJ_SIZE*STORE_SIZE);
    system_store = test_malloc(OBJ_SIZE*STORE_SIZE);
    memset(system_store, 0, OBJ_SIZE*STORE_SIZE);
    store        = test_malloc(store_size);
    memset(store, 0, store_size);
#endif
    MEMCPYSECRET(&SYS_MEM(0));
    /* for(int i = 0; i < STORE_SIZE; i++) { */
    /* } */
    /* for(int d = 0; d < NDOMAINS; d++) { */
    /*     if (d == domain) */
    /*         continue; */
    /*     for(int i = 0; i < STORE_SIZE; i++) { */
    /*         MEMCPYSECRET(LMEM(d, i*OBJ_SIZE)); */
    /*     } */
    /* } */
    DEBUG_PRINTF("SECRET ADDR: %p\r\n", secret);
    DEBUG_PRINTF("SYSTEM STORE ADDR: %p\r\n", system_store);
    DEBUG_PRINTF("USER STORE ADDR: %p\r\n", store);
    DEBUG_PRINTF("PUBLIC STORE ADDR: %p\r\n", public_store);
}

struct store_get_res*
store_get(int domain, saddr_t addr)
{
    struct store_get_res *ret = test_malloc(sizeof(*ret));
    puts("get malloc\r\n");
    ret->size   = OBJ_SIZE;
    ret->result = test_malloc(OBJ_SIZE);
    puts("res malloc\r\n");
    DEBUG_PRINTF("DOM: %d\n", domain);
    DEBUG_PRINTF("addr: %d\n", ADDR_SADDR(addr));
    memcpy(ret->result, LMEM(domain, addr), OBJ_SIZE);

    return ret;
}

void
store_set(int domain, saddr_t addr, char *value, size_t size)
{
    memcpy(LMEM(domain, addr), value, size);
}
