#ifndef __INTERPRETER_H__
#define __INTERPRETER_H__
#include "types.h"
#include "control.h"

// Return a representation, for a given interpreter,
// of the address of object 'addr' and offset 'offset'.
// This function exists to make the exploits modular.
uaddr_t
build_uaddr(char addr, char offset);

// Allocate & return a poitner
// to a 'system' message constructed from the user message.
struct smessage*
interpret_cmd(struct umessage *umsg);
#endif
