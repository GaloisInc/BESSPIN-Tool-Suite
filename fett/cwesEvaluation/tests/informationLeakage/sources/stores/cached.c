#include "types.h"
#include "stores.h"
#include "control.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

char *__STORE_CWES = "524";
char *STORE_IMPL   = "CACHED";

struct store_obj {
    int domain;
    saddr_t addr;
    char data[OBJ_SIZE];
};

#ifdef __IEX_GEN__ARRAYS__
struct store_obj public_store[STORE_SIZE]   = {0};
struct store_obj system_store[STORE_SIZE]   = {0};
struct store_obj store[NDOMAINS*STORE_SIZE] = {0};
#else
struct store_obj *public_store;
struct store_obj *system_store;
struct store_obj *store;
#endif


static struct store_obj cached = { -1, 0, {0}};
static int cache_dirty = 0;
struct store_obj *cache_ptr = NULL;

#define DEBUG_MEM(_dom, _addr) \
    DEBUG_PRINTF("Reading MEM(%d, %d) (%p, %p, %p)\r\n", \
                 _dom, _addr,                            \
                 store, &MEM(_dom, 0), &MEM(_dom, _addr))

#define P0 1  // some prime non-divisor of NDOMAINS   (which is a power of 2)
#define P1 1 // some prime non-divisor of STORE_SIZE (which is a power of 2)

void
store_init(int domain)
{
#ifndef __IEX_GEN__ARRAYS__
    public_store = test_malloc(STORE_SIZE*sizeof(struct store_obj));
    system_store = test_malloc(STORE_SIZE*sizeof(struct store_obj));
    store        = test_malloc(NDOMAINS*STORE_SIZE*sizeof(struct store_obj));
#endif
    int p = 0;
    for(int i = 0; i < STORE_SIZE; i++) {
        MEMCPYSECRET(system_store[i].data);
        puts("SECRET: ");
        puts(system_store[i].data);
        puts("\r\n");
        system_store[i].domain  = -1;
        system_store[i].addr = i;
        public_store[i].domain  = -2;
        public_store[i].addr = i;
        for (int d = 0; d < NDOMAINS; d++) {
            int dom = (d*P0) % NDOMAINS;
            int addr = (i*P1) % STORE_SIZE;
            store[p].domain = dom;
            store[p].addr   = addr;
            if (dom != domain) {
                MEMCPYSECRET(store[p].data);
            } else {
                strncpy(store[p].data, NOT_SECRET, OBJ_SIZE);
            }
            p++;
        }
    }

    for (p = 0; p < NDOMAINS*STORE_SIZE; p++) {
        DEBUG_PRINTF("STORE[%d] = { %d, %d, %.*s }\n",
               p, store[p].domain, store[p].addr, (int)OBJ_SIZE, store[p].data);
    }
}

void write_back_cache() {
    if (cache_dirty) {
        DEBUG_PRINTF("CACHE DIRTY >>");
        DEBUG_PRINTF("WRITING { %d, %d, %.*s }\r\n", cached.domain, cached.addr, OBJ_SIZE, cached.data);
        memcpy(cache_ptr, &cached, sizeof(*cache_ptr));
        cache_dirty = 0;
    }
}

void set_cache(struct store_obj *val) {
    cache_ptr = val;
    memcpy(&cached, val, sizeof(cached));
}

struct store_obj*
find(int domain, saddr_t addr)
{
    char obj = OBJ_ADDR(addr);
    DEBUG_PRINTF("FINDING (%d, %x)\r\n", domain, obj);
    struct store_obj *ret = NULL;

    if (domain < 0) {
        for (int p = 0; ret == NULL && p < STORE_SIZE; p++) {
            if (system_store[p].addr == obj) {
                DEBUG_PRINTF(">>> FOUND AT %d\r\n", p);
                ret = &system_store[p];
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
    /* unsigned */ int obj = OBJ_ADDR(addr);
    int off = OBJ_OFF(addr);
    struct store_get_res *ret = test_malloc(sizeof(*ret));
    ret->size   = OBJ_SIZE;
    ret->result = test_malloc(OBJ_SIZE);

    struct store_obj *target = NULL;
    if (cache_ptr && cached.domain == domain && cached.addr == obj) {
        DEBUG_PRINTF("GET >> CACHE HIT!\r\n");
        target = &cached;
    } else {
        write_back_cache();
        target = find(domain, addr);
        set_cache(target);
    }

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

    if (!cache_ptr || cached.domain != domain || cached.addr != obj) {
        write_back_cache();
#ifdef NO_WEAKNESS
        memset(cached.data, 0, sizeof(cached.data));
#endif
        target        = find(domain, addr);
        cache_ptr     = target;
        cached.domain = domain;
        cached.addr   = obj;
    }
    puts("set\r\n");

    size_t min = size < OBJ_SIZE ? size : OBJ_SIZE;
    DEBUG_PRINTF("SET %d %d %d <- \"%.*s\" (%d)\n", domain, obj, off, min, value, min);
    if(min > 0)
        memcpy(cached.data, value, min);
    puts(cached.data);
    cache_dirty = 1;

    return;
}
