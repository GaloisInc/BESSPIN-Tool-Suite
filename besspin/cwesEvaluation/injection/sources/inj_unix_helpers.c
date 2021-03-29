#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// Size of buffer to use when reading from stdin
#define BUF_SIZE 32

#include "inj_unix_helpers.h"

// Read a line from stdin, storing the line in `line`.  Strips the '\n' from
// the string.
static void read_line(char line[BUF_SIZE]) {
    // Use read syscall rather than getline so the tests build on a bare metal
    // compiler
    for (size_t i = 0; i < BUF_SIZE; ++i) {
        // Read one character at a time
        ssize_t bytes = read(0, line + i, sizeof(char));
        if (bytes != sizeof(char)) {
            printf("<INVALID>\n");
            printf("Failed to read from stdin.\n");
            exit(0);
        }
        switch (line[i]) {
            case '\n':
                // Replace newline with null terminator and return
                line[i] = '\0';
                return;
            case '\0':
                printf("<INVALID>\n");
                printf("Unexpected null terminator.\n");
                exit(0);
            default:
                // Keep reading
                break;
        }
    }
    printf("<INVALID>\n");
    printf("Buffer full before reading newline.\n");
    exit(0);
}

int read_int() {
    char line[BUF_SIZE];
    read_line(line);
    int value = atoi(line);
    return value;
}

uintptr_t read_uintptr_t() {
    char line[BUF_SIZE];
    read_line(line);
    uintptr_t value = (uintptr_t) strtoull(line, NULL, 0);
    if (value == ULLONG_MAX) {
        printf("<INVALID>\n");
        printf("Failed to convert string to integer\n");
        exit(0);
    }
    return value;
}
