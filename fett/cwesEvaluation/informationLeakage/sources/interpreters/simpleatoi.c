#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include "types.h"
#include "interpreter.h"

char *__INTERPRETER_CWES = "707";

/*
 * In this example, we assume that the address is 3 ASCII digits.
 */
saddr_t
simple_atoi(uaddr_t address) {
    int base = 1;
    saddr_t addr = 0;
    char offset = 0;
    for (int e = 1; e < 3; e++) {
        offset += base*(address[e] - '0');
        base = base*10;
    }
    int objid = address[0] - '0';
#ifdef NO_WEAKNESS
    if (objid < 0) objid = 0;
    if (objid >= STORE_SIZE) objid = STORE_SIZE-1;
    if (offset <0) offset = 0;
    if (offset >= OBJ_SIZE) offset = OBJ_SIZE-1;
#endif

    saddr_t x = SADDR(address[0] - '0', offset);
    printf("{ %hd, %hd }\n", OBJ_ADDR(x), OBJ_OFF(x));
    return x;
}

uaddr_t
build_uaddr(char addr, char offset)
{
    uaddr_t uaddr = test_malloc(3);
    uaddr[0] = '0' + addr;
    uaddr[1] = '0' + (offset % 10);
    uaddr[2] = '0' + (offset / 10);

    return uaddr;
}

struct smessage*
interpret_cmd(struct umessage *umsg)
{
    struct smessage *ret = test_malloc(sizeof(*ret));
    ret->type = umsg->type;
    ret->domain = umsg->domain;
    switch (umsg->type) {
    case GET:
        ret->m.getmsg.address = simple_atoi(umsg->m.getmsg.address);
        break;
    case SET:
        ret->m.setmsg.address = simple_atoi(umsg->m.setmsg.address);
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
