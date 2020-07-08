#include "testsParameters.h"

#include <string.h>
#include <stdio.h>
#include <signal.h>
#define LENGTH 201 // the length of the character areas X, Y, Z

/** There are two areas X and Y that program compares.
   However, attacker might allow modification of the Y variable
   and therefore, cause unexpected program behaviour or crash
   during the program execution. */

char X[LENGTH]= {
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
};

char Y[LENGTH]= {
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

};

void
compare(char *str) {
    char T[LENGTH];
    strcpy(T, str);
    int i = 0;

    for (i = 0; i < LENGTH; i++){
        if (X[i] != T[i]) break;
    }
    if (i == LENGTH){
        printf("\n<EXECUTING_BENIGN_CODE>\n");
    }
    else {
        printf("\n<EXECUTING_MALICIOUS_CODE>\n");
    }
    return;
}
// attacker - change content of the Y area.
void
do_malicious_modification(char *ptr) {
    char Z[LENGTH];
    strcpy(Z, ptr);
    int i=0;
    for(i = 0; i <= strlen(Z); i++)
    {
        if(Z[i] == 'A')
        {
            Z[i] = 'B';
        }
    }

    compare(&Z[0]);
    return;
}

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
#endif

#ifdef testgenOnFreeRTOS
// ----------------- FreeRTOS Test ----------
#define NUM_OF_TEST_PARTS 2

void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
   #if TESTGEN_TEST_PART == 1
     printf("\n---Part01: regular_read.---\n");
     compare(&Y[0]);
   #elif TESTGEN_TEST_PART == 2
     printf("\n---Part02: do_malicious_modification.---\n");
     do_malicious_modification(&Y[0]);
    #else
     printf("SCORE:822:%d:TEST ERROR\n", TESTGEN_TEST_PART);
    #endif
  return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

int main()
{
  printf("\n<do_regular_compare>\n");
  compare(&Y[0]);
  // If the pointer is de-referenced for a write operation,
  // the attack might allow modification
  // of critical program state variables,
  // cause a crash, or execute code.
  printf("\n<do_malicious_modification>\n");
  do_malicious_modification(&Y[0]);
  return 0;
}
#endif // end of if FreeRTOS
