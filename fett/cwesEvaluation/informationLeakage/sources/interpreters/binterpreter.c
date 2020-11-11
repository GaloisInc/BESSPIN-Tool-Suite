#include <stddef.h>
#include <stdlib.h>
#include "types.h"
#include "interpreter.h"

char *__INTERPRETER_CWES = "";

uaddr_t
build_uaddr(char addr, char offset)
{
    uaddr_t x = (uaddr_t)(0xFFFF & SADDR((uint16_t)addr,(uint16_t)offset));
    return x;
}

/*
 * Basic Interpreter Module for T/O tests
 */
struct smessage*
interpret_cmd(struct umessage *umsg)
{
    struct smessage *ret = test_malloc(sizeof(*ret));
    ret->type = umsg->type;
    ret->domain = umsg->domain;
    switch (umsg->type) {
    case GET:
#ifdef NO_WEAKNESS
        if (!VALID_SADDR((saddr_t)umsg->m.getmsg.address))
            return NULL;
#endif
        ret->m.getmsg.address = (saddr_t)umsg->m.getmsg.address;
        break;
    case SET:
#ifdef NO_WEAKNESS
        if (!VALID_SADDR((saddr_t)umsg->m.getmsg.address))
            return NULL;
#endif
        ret->m.setmsg.address = (saddr_t)umsg->m.setmsg.address;
        ret->m.setmsg.value   = umsg->m.setmsg.value;
        ret->m.setmsg.size    = umsg->m.setmsg.size;
        break;
    case GO:
        ret->m.gomsg.value = umsg->m.gomsg.value;
        ret->m.gomsg.size  = umsg->m.gomsg.size;
        break;
    }

    return ret;
}
