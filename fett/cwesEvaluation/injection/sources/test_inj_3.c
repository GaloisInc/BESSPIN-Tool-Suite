#include <stdbool.h>
#include <stdio.h>
#include "testsParameters.h"

// Size of buffer in tagged_buffer_t
#define BUFFER_SIZE 8

// Use a struct to store the buffer and flags variable so that the compiler is
// forced to place the flags directly after the buffer in memory.
typedef struct {
    char buffer[BUFFER_SIZE];
    // Mark flags volatile to prevent the compiler from optimizing out checks
    volatile int flags;
} tagged_buffer_t;

// Simulate a copy of untrusted data to `buffer`
void get_untrusted_data(int bytes, char *buffer) {
    for (int i = 0; i < bytes; ++i) {
        buffer[i] = 'A';
    }
}

// Create and write untrusted data into a tagged_buffer_t.  If `malicious` is
// true, this write will overflow the buffer and write into trusted data.
void write_buffer(bool malicious) {
    tagged_buffer_t tagged_buffer;
    tagged_buffer.flags = 0;

    get_untrusted_data(BUFFER_SIZE + malicious, tagged_buffer.buffer);

    if (tagged_buffer.flags) {
        // Trusted field `tagged_buffer.flags` was altered, changing the
        // control flow of the execution
        printf("\n<EXECUTING_MALICIOUS_CODE>\n");
    } else {
        // Trusted field `tagged_buffer.flags` was not altered
        printf("\n<EXECUTING_BENIGN_CODE>\n");
    }
}

#ifdef testgenOnFreeRTOS
// ----------------- FreeRTOS Test --------------------------------------------
#define NUM_OF_TEST_PARTS 2

#ifdef testgenFPGA
#include "FreeRTOS.h"
#endif

void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
   #if TESTGEN_TEST_PART == 1
     printf("\n---Part01: regular_write.---\n");
     write_buffer(false);
   #elif TESTGEN_TEST_PART == 2
     printf("\n---Part02: malicious_write.---\n");
     write_buffer(true);
    #else
     printf("SCORE:INJ-3:%d:TEST ERROR\n", TESTGEN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test -------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

#include <stdlib.h>

int main(int argc, char *argv[]) {
    int option;
    if (argc > 1) { //be safe
        option = atoi(argv[1]);
    } else {
        option = -1;
    }
    switch(option) {
        case 1 :
            printf("\n<do_regular_write>\n");
            write_buffer(false);
            break;
        case 2 :
            printf("\n<do_malicious_write>\n");
            write_buffer(true);
            break;
        default :
            printf("SCORE:INJ-3:%d:TEST ERROR\n",option);
            return 1;
    }
    return 0;
}

#endif // end of if FreeRTOS
