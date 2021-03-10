#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <unistd.h>

#include "unbufferStdout.h"

#define LOCK_FILE "multitask.lock"

// How much to sleep in microseconds per process being spawned
#define SLEEP_US_PER_PROC 5000

void fail_if(bool condition, const char* message) {
    if (condition) {
        printf("<INVALID>\n");
        printf("%s\n", message);
        exit(1);
    }
}

int main(int argc, char **argv) {
    unbufferStdout();

    // Print PID
    printf("<PID %ld>\n", (long) getpid());

    // The total number of processes being spawned.
    int num_procs = atoi(argv[1]);

    // Compute sleep duration between lock file checks
    unsigned long total_sleep_us = num_procs * SLEEP_US_PER_PROC;
    unsigned int sleep_s = (unsigned int) (total_sleep_us / 1000000);
    useconds_t sleep_us = (useconds_t) (total_sleep_us % 1000000);

    // Spin until lock file is removed
    while (access(LOCK_FILE, F_OK) == 0) {
        if (sleep_s) {
            sleep(sleep_s);
        }
        if (sleep_us) {
            usleep(sleep_us);
        }
    }

    // Exec
    execv(argv[2], argv + 2);
    printf("Exec failed with errno <%d>\n", errno);
    fail_if(true, "Failed to exec");

    return 1;
}
