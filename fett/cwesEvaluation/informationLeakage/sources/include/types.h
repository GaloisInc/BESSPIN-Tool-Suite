#ifndef __TYPES_H__
#define __TYPES_H__
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include "parameters.h"

#ifndef STORE_SIZE
#error "STORE_SIZE undefined"
#endif

#ifndef NDOMAINS
#error "NDOMAINS undefined"
#endif

#ifndef OBJ_SIZE
#define OBJ_SIZE (2*PATTERN_SIZE)
#endif

#define MEMCPYSECRET(_dst)                      \
    memcpy(_dst, secret, OBJ_SIZE)

// The "internal" type of
// store addresses
typedef int16_t saddr_t;
// Construct an saddr_t from an id/offset
#define SADDR(id, offset) ((((int16_t)id) << 8) | ((int16_t)offset & 0xFF))
// Destruct an saddr_t:
#define OBJ_OFF(_x)  ((int8_t)(0xFF & (((int16_t)_x << 8) >> 8)))
#define OBJ_ADDR(_x) (((int16_t)_x >> 8))
// Handy
#define VALID_ID(id) (0 <= id && id < STORE_SIZE)
#define VALID_OFF(off) (0 <= off && off < OBJ_SIZE)
#define VALID_SADDR(addr) \
    (VALID_ID(OBJ_ADDR(addr)) && VALID_OFF(OBJ_OFF(addr)))

// User definitions
typedef char* uaddr_t;

typedef enum { GET, SET, GO } m_type;

struct uget {
    uaddr_t address;
};
struct uset {
    uaddr_t address;
    char    *value;
    size_t  size;
};
struct ugo {
    char    *value;
    size_t  size;
};

struct umessage {
    // The type for the union below
    m_type type;
    // This is the TRUSTED "owner" of the message.
    // The integrity of the domain field is never the subject,
    // i.e. software systems can rely on it to determine
    // ownership.
    int    domain;
    union {
        struct uget getmsg;
        struct uset setmsg;
        struct ugo  gomsg;
    } m;
};

// System definitions,
// essentially identical to the user versions above
struct sget {
    saddr_t address;
};
struct sset {
    saddr_t address;
    char *value;
    size_t size;
};
struct sgo {
    char *value;
    size_t size;
};
struct smessage {
    m_type type;
    int domain;
    union {
        struct sget getmsg;
        struct sset setmsg;
        struct sgo  gomsg;
    } m;
};

#ifdef DEBUG
#define DEBUG_PRINTF(...) printf(__VA_ARGS__)
#else
#define DEBUG_PRINTF(...)
#endif

#endif
