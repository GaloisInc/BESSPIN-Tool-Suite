#ifndef INJ_UNIX_HELPERS_H_
#define INJ_UNIX_HELPERS_H_

#include <stdint.h>

// Read and return an int from stdin.  Must be on its own line, terminated with
// a newline.
int read_int();

// Read and return a uintptr_t from stdin.  Must be on its own line, terminated
// with a newline.
uintptr_t read_uintptr_t();

#endif  // INJ_UNIX_HELPERS_H_
