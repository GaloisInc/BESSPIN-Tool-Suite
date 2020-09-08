#ifndef __FUNCTIONS_H_
#define __FUNCTIONS_H_
#include "stores.h"
#include "control.h"

// The function interface allows new functionality to be added to the app.
//
// Function calls are marshalled into strings, which will support
// (eventually) factoring the tests into multiple processes.
//
// The table of available functions is built by running 'tablegen.p'
// in the functions source directory.

struct function_result {
    char *result;
    size_t size;
};

typedef struct function_result * (*fn_t)(struct smessage *smsg);

struct function_rec {
    char *name;
    fn_t fn;
};

extern size_t n_functions;
extern struct function_rec function_tab[];

struct function_result*
run_command(struct smessage *msg);

#define ARG_BUF(name, cmd, argsz)           \
    char name[sizeof cmd + 1 + argsz] = cmd":"; \
    size_t name##_idx = sizeof(cmd);
#define ARG_PUT(buf, val) \
    memcpy(&buf[buf##_idx], &val, sizeof(val)); buf##_idx += sizeof(val)

#define ARGP(p, sz, args)                        \
    char * args = 1+memchr(p, ':', sz)
#define ARG(ty, x, args)                        \
    ty x;                                       \
    do {                                        \
        memcpy(&x, args, sizeof(ty));           \
        args += sizeof(ty);                     \
    } while (0)

#endif
