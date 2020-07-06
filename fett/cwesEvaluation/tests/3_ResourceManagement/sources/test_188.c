#include "testsParameters.h"

#include <stdio.h>
void
example_byte_in_front(void) { // works for MacOS Catalina
    char a='a';
    char b;
    *(&a - 1) = 'b';
    if (b == 'b') {
        printf("\n<PROTOCOL_ONE_BYTE_IN_FRONT> b=%c\n", b);
    }else {
        printf("\n<WRONG_PROTOCOL> No one byte in front.\n");
    }
}

void
example_byte_past(void) { // works for Debian
    char d='d';
    char e;
    *(&d + 1) = 'e';
    if (e == 'e') {
        printf("\n<PROTOCOL_ONE_BYTE_PAST> e=%c\n", e);
    }else {
        printf("\n<WRONG_PROTOCOL> No byte past.\n");
    }
}

void
example_input_args_past_on_stack(char x, char y) {
    if(*(&x - 1) == y) {
        printf("\n<EXPECTED_INPUT_PAST> y=%c\n", y);
    }
    else {
        printf("\n<WRONG_PROTOCOL> No byte past.\n");
    }
}

void
example_input_args_in_front_on_stack(char x, char y) {
    if(*(&x + 1) == y) {
        printf("\n<EXPECTED_INPUT_PAST> y=%c\n", y);
    }
    else {
        printf("\n<WRONG_PROTOCOL> No byte past.\n");
    }
}

#ifdef testgenOnFreeRTOS

#if (defined(testgenFPGA))
#include "FreeRTOS.h"
#endif
// ----------------- FreeRTOS Test ----------
#define NUM_OF_TEST_PARTS 4

void main() {
    printf("\n<OSIMAGE=FreeRTOS>\n");
#if TESTGEN_TEST_PART == 1
    printf("\n---Part01: example_byte_in_front.---\n");
    example_byte_in_front();
#elif TESTGEN_TEST_PART == 2
    printf("---Part02: example_byte_past.---\n");
    example_byte_past();
#elif TESTGEN_TEST_PART == 3
    printf("---Part03: example_input_args_past_on_stack.---\n");
    example_input_args_past_on_stack('A', 'B');
#elif TESTGEN_TEST_PART == 4
    printf("---Part04: example_input_args_past_on_stack.---\n");
    example_input_args_in_front_on_stack('A', 'B');
#else
    printf("SCORE:188:%d:TEST ERROR\n",TESTGEN_TEST_PART);
#endif
    return;
}

//---------------- Debian && FreeBSD test ------------------------------------------------------
#elif (defined(testgenOnDebian) || defined(testgenOnFreeBSD))

/** aligned on 32-bit boundaries.*/
void
example_three_bytes_past() {
    char g='g';
    char h;
    *(&g + 3) = 'h';
    if (h == 'h') {
        printf("\n<PROTOCOL_THREE_BYTE_PAST> h=%c\n", h);
    } else {
        printf("\n<WRONG_PROTOCOL> No three bytes past.\n");
    }

}

/** aligned on 32-bit boundaries.*/
void
example_three_bytes_in_front() {
    char u='q';
    char v;
    *(&u - 3) = 'v';
    if (v == 'v') {
        printf("\n<PROTOCOL_THREE_BYTES_IN_FRONT> v=%c\n", v);
    } else {
        printf("\n<WRONG_PROTOCOL> No three bytes in front.\n");
    }

}

int main() {
    printf("\n<example_byte_in_front>\n");
    example_byte_in_front();
    printf("\n<example_one_byte_past>\n");
    example_byte_past();
    printf("\n<example_three_bytes_in_front>\n");
    example_three_bytes_in_front();
    printf("\n<example_three_bytes_past>\n");
    example_three_bytes_past();
    printf("\n<example_input_args_past_on_stack>\n");
    example_input_args_past_on_stack('A', 'B');
    printf("\n<example_input_args_in_front_on_stack>\n");
    example_input_args_in_front_on_stack('A', 'B');
    return 0;
}

#endif // end of if FreeRTOS

