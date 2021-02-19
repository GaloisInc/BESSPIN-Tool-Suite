#include <stdbool.h>
#include <stdio.h>
#include <unistd.h>

#include "unbufferStdout.h"

#define LOCK_FILE "multitask.lock"

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

    // Spin until lock file is removed
    while (access(LOCK_FILE, F_OK) == 0) {
        // Sleep for 0.1 seconds before checking again
        usleep(100000);
    }

    // Exec
    execv(argv[1], argv + 1);
    fail_if(true, "Failed to exec");

    return 1;
}
