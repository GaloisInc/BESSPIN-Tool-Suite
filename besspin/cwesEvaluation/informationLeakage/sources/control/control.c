#include "types.h"
#include "control.h"
#include "interpreter.h"
#include "functions.h"
#include <stdlib.h>
#include <string.h>

#ifdef __IEX_GEN__CAPABILITIES__
#include <cheri/cheric.h>
#endif

#ifndef __IEX_GEN__CAPABILITIES__
#ifdef __IEX_GEN__ARRAYS__
#ifdef __IEX_GEN__STATIC_SECRET__
char secret[OBJ_SIZE] = SECRET_PATTERN;
#else
char secret[OBJ_SIZE] = {0};
#endif // ARRAYS/STATIC
#else
#ifdef __IEX_GEN__STATIC_SECRET__
char *secret = SECRET_PATTERN;
#else
char *secret;
#endif // !ARRAYS/STATIC
#endif
#else // __IEX_GEN__CAPABILITIES__
uintptr_t *secret;
static uintptr_t secret_cap;
static uintptr_t pad_cap = 0x09ad09ad09ad09ad;
#endif // __IEX_GEN__CAPABILITIES__

void get_msg(int domain,
             uaddr_t addr,
             struct umessage *msg)
{
    msg->type             = GET;
    msg->domain           = domain;
    msg->m.getmsg.address = addr;
}

void set_msg(int domain,
             uaddr_t addr,
             char *value,
             size_t size,
             struct umessage *msg)
{
    msg->type = SET;
    msg->domain = domain;

    msg->m.setmsg.address = addr;
    if ( size > 0) {
      msg->m.setmsg.value   = test_malloc(size);
      memcpy(msg->m.setmsg.value, value, size);
    }
    msg->m.setmsg.size    = size;
}

void go_msg(int domain,
            char *value,
            size_t size,
            struct umessage *msg)
{
    msg->type   = GO;
    msg->domain = domain;

    msg->m.gomsg.value   = test_malloc(size);
    memcpy(msg->m.gomsg.value, value, size);
    msg->m.gomsg.size    = size;
}

int
matches_secret(const void *str)
{
#ifndef __IEX_GEN__CAPABILITIES__
    const char *p;
    puts("TESTING\r\n");
    if ((p = strstr(str, PAD))) {
        puts("ONE\r\n");
        if ((p = strstr(p, SECRET_TEXT))) {
            puts("TWO\r\n");
            if ((p = strstr(p, PAD))) {
                puts("THREE\r\n");
                return 1;
            }
        }
    }
#else // __IEX_GEN__CAPABILITIES__
    const uintptr_t *caps = str;
    puts("TESTING\r\n");
    if (!__builtin_is_aligned(str, sizeof(uintptr_t))) {
        // Can't (easily) contain caps
	return 0;
    }
    if (__builtin_cheri_equal_exact(secret[0], caps[0])) {
        puts("ONE\r\n");
        if (__builtin_cheri_equal_exact(secret[1], caps[1])) {
            puts("TWO\r\n");
            if (__builtin_cheri_equal_exact(secret[2], caps[2])) {
                puts("THREE\r\n");
                return 1;
            }
        }
    }
#endif // __IEX_GEN__CAPABILITIES__

    return 0;
}

struct function_result *
send_and_run(struct umessage *msg)
{
    struct smessage *smsg        = interpret_cmd(msg);
    struct function_result *fres = run_command(smsg);

    return fres;
}

void
scrub(const void *in, size_t in_size, void *out)
{
#ifndef __IEX_GEN__CAPABILITIES__
    size_t idx = 0;
    const char *p = in;
    char *bad = NULL;
    while (p != NULL && p[0] != 0) {
        size_t advance = strlen(p);
        bad = strstr(p, SECRET_PATTERN);
        char *next = NULL;
        if (bad) {
            advance = bad - p;
            next    = bad + strlen(SECRET_PATTERN);
        }
        memcpy((char *)out + idx, p, advance);
        idx += advance;
        p = next;
    }
#else // __IEX_GEN__CAPABILITIES__
    const uintptr_t *inp = in;
    uintptr_t *outp = out;
    while ((char *)inp < (char *)in + in_size) {
        size_t size = (char *)inp - (char *)in;
        if (size < sizeof(uintptr_t)) {
            memcpy(outp, inp, size);
            return;
        }
        /*
         * XXX: should this be less restrictive (e.g. address equiality +
         * a tag?)
         */
        if (!__builtin_cheri_equal_exact(*inp, secret_cap))
            *outp++ = *inp;
        inp++;
    }
#endif // __IEX_GEN__CAPABILITIES__
}

void
initialize_secret()
{
#ifndef __IEX_GEN__CAPABILITIES__
#ifndef __IEX_GEN__STATIC_SECRET__
#ifndef __IEX_GEN__ARRAYS__
  secret = test_malloc(OBJ_SIZE);
#endif
  strncpy(&secret[0], PAD, sizeof(PAD));
  strncat(&secret[0], SECRET_TEXT, sizeof(SECRET_TEXT));
  strncat(&secret[0], PAD, sizeof(PAD));
#endif
#else // __IEX_GEN__CAPABILITIES__
    secret = test_malloc(OBJ_SIZE);
    secret_cap = cheri_andperm(secret, ~CHERI_PERM_GLOBAL);
    secret[0] = pad_cap;
    secret[1] = secret_cap;
    secret[2] = pad_cap;
#endif // __IEX_GEN__CAPABILITIES__
}

#ifdef BESSPIN_FREERTOS
void
test_not_implemented()
{
    puts("TEST NOT IMPLEMENTED.\r\n");
    test_end();
}

void
test_end()
{
    puts(">>>End of Besspin<<<\n");
    do {} while(1);
}

void
test_pass()
{
    puts("TEST PASSED.\r\n");
    test_end();
}

void
test_fail()
{
    puts("TEST FAILED.\r\n");
    test_end();
}
#else
void
test_not_implemented()
{
    puts("TEST NOT IMPLEMENTED.\r\n");
    test_end();
}

void
test_end()
{
    exit(0);
}

void
test_pass()
{
    puts("TEST PASSED.\r\n");
    test_end();
}

void
test_fail()
{
    puts("TEST FAILED.\r\n");
    test_end();
}

#endif //BESSPIN_FREERTOS
