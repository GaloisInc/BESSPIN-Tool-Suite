#ifndef __CONTROL_H__
#define __CONTROL_H__

#ifdef __IEX_GEN__ARRAYS__
extern char secret[OBJ_SIZE];
#else
extern char *secret;
#endif // !ARRAYS/STATIC

// For checking test dependencies
extern char *STORE_IMPL;

//////////////////////////////////////////////////////
// Initialize the secret value (if it isn't static  //
//////////////////////////////////////////////////////
void
initialize_secret();

//////////////////////////////////////////////////////
// Convenience functions for building user messages //
//////////////////////////////////////////////////////
void
get_msg(int domain, uaddr_t addr, struct umessage *msg);

void
set_msg(int domain, uaddr_t addr, char *val, size_t sz, struct umessage *msg);

void
go_msg(int domain, char *value, size_t size, struct umessage *msg);

struct function_result *
send_and_run(struct umessage *msg);

// return 1 <=> `str` contains the secret value
int
matches_secret(const char *str);

// Removes the secret value from `in`, copying result
// into `out` buffer. Both buffers should have size
// `in_size`
void
scrub(const char *in, size_t in_size, char *out);

//////////////////////////////////
// Wrappers around OS interface //
//////////////////////////////////
void
test_end();

void
test_not_implemented();

void
test_pass();

void
test_fail();

#ifdef testgenOnFreeRTOS
#define IEX_TESTGEN
#endif

#ifdef IEX_TESTGEN
#define TEST_MAIN  int test_main()
#else
#define TEST_MAIN int main(int argc, char **argv)
#endif

#if defined(testgenOnFreeRTOS) && defined(testgenFPGA)

#define test_malloc pvPortMalloc
#define test_free   vPortFree
#else

#define test_malloc malloc
#define test_free   free

#endif
#endif
