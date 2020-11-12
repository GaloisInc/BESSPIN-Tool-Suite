#include "types.h"
#include "control.h"
#include "interpreter.h"
#include "functions.h"
#include <stdlib.h>
#include <string.h>

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
matches_secret(const char *str)
{
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
scrub(const char *in, size_t in_size, char *out)
{
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
        memcpy(&out[idx], p, advance);
        idx += advance;
        p = next;
    }
}

void
initialize_secret()
{
#ifndef __IEX_GEN__STATIC_SECRET__
#ifndef __IEX_GEN__ARRAYS__
  secret = test_malloc(OBJ_SIZE);
#endif
  strncpy(&secret[0], PAD, sizeof(PAD));
  strncat(&secret[0], SECRET_TEXT, sizeof(SECRET_TEXT));
  strncat(&secret[0], PAD, sizeof(PAD));
#endif
}

#ifdef testgenOnFreeRTOS
void
test_not_implemented()
{
    puts("TEST NOT IMPLEMENTED.\r\n");
    test_end();
}

void
test_end()
{
    puts(">>>End of Fett<<<\n");
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

#endif //testgenOnFreeRTOS
