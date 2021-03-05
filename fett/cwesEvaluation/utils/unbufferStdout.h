#ifndef UNBUFFER_STDOUT_H_
#define UNBUFFER_STDOUT_H_

#include <stdio.h>
#include <stdlib.h>

// Unbuffer stdout so that redirection to a file will capture all output.
// Implemented in the header file so that most vulnerability classes can
// continue to use the default makefile.  This function is tiny so compilation
// time impacts of rebuilding it for each test aren't a concern.
void unbufferStdout(void) {
    if (setvbuf(stdout, 0, _IONBF, 0)) {
        printf("\n<INVALID>\n");
        printf("setvbuf failed.\n");
        fflush(stdout);
        exit(1);
    }
}

#endif  // UNBUFFER_STDOUT_H_
