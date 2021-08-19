#include "testsParameters.h"
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA))
    #include "FreeRTOS.h"
#endif

#define NUM_OF_TEST_PARTS 4

#if __riscv_xlen == 64
    #define UINT_MAX UINT64_MAX
#elif __riscv_xlen == 32
    #define UINT_MAX UINT32_MAX
#endif

enum operation {MULT, ADD};

static void test_op_dtype_xlen(int part, enum operation op);
static void test_op_dtype_8(int part, enum operation op);
static void check_test_error(bool error, int part);
static __attribute__((noinline)) size_t add_xlen (size_t in1, size_t in2);
static __attribute__((noinline)) uint8_t add_8 (uint8_t in1, uint8_t in2);
static __attribute__((noinline)) size_t mult_xlen (size_t in1, size_t in2);
static __attribute__((noinline)) uint8_t mult_8 (uint8_t in1, uint8_t in2);

#ifdef BESSPIN_FREERTOS
    void main() {
        int testpart = BESSPIN_TEST_PART;
#elif (defined(BESSPIN_DEBIAN) || defined(BESSPIN_FREEBSD))
    #include "unbufferStdout.h"
    int main(int argc, char *argv[]);

    int main(int argc, char *argv[]) {
        unbufferStdout();
        int testpart;
        if (argc > 1) { //be safe
            testpart = atoi(argv[1]);
        } else {
            testpart = 0;
        } 
#endif
        printf ("TEST 128 PART P0%d\n",testpart);
        switch(testpart) {
            case 1 :
                test_op_dtype_xlen(testpart, MULT);
                break;
            case 2 :
                test_op_dtype_xlen(testpart, ADD);
                break;
            case 3 :
                test_op_dtype_8(testpart, MULT);
                break;
            case 4 :
                test_op_dtype_8(testpart, ADD);
                break;
            default :
                check_test_error(true, testpart);
        }

        #ifdef BESSPIN_FREERTOS
            return;
        #elif (defined(BESSPIN_DEBIAN) || defined(BESSPIN_FREEBSD))
            return 0;
        #endif
    }

static void check_test_error(bool error, int part) {
  if (error) {
    printf("SCORE:128:%d:TEST ERROR\n", part);
    exit(1);
  } else {
    printf("<GOOD>\n");
  }
}

static void test_op_dtype_xlen(int part, enum operation op) {
    size_t dut;

    // First, a benign case
    switch (op) {
        case MULT:
            dut = mult_xlen(200, 5);
            break;
        case ADD:
            dut = add_xlen(150, 850);
            break;
        default:
            check_test_error(true, part);
    }
    printf("DUT = <%lu>\n",dut);
    check_test_error (dut!=1000,part);

    // Second, a malicious case
    if (op==MULT)
        dut = mult_xlen((UINT_MAX / 4) + 1, 4); // wrap-around
    else
        dut = add_xlen(UINT_MAX - 32 + 1, 32); // wrap-around

    printf("DUT = <%lu>\n",dut);
    check_test_error (dut!=0,part); 

    printf ("SCORE:128:%d:TEST FAILED\n",part);
    return;
}

static void test_op_dtype_8(const int part, const enum operation op) {
    uint8_t dut;

    // First, a benign case
    switch (op) {
        case MULT:
            dut = mult_8(20, 5);
            break;
        case ADD:
            dut = add_8(15, 85);
            break;
        default:
            check_test_error(true, part);
    }
    printf("DUT = <%d>\n",dut);
    check_test_error (dut!=100,part);

    // Second, a malicious case
    if (op == MULT)
        dut = mult_8(64, 4); // wrap-around
    else
        dut = add_8(224, 32); // wrap-around

    printf("DUT = <%d>\n",dut);
    check_test_error (dut!=0,part); 

    printf ("SCORE:128:%d:TEST FAILED\n",part);
    return;
}

static __attribute__((noinline)) size_t add_xlen (size_t in1, size_t in2) {
    size_t ret = 0;
    ret += in1;
    ret += in2;
    return ret;
}

static __attribute__((noinline)) uint8_t add_8 (uint8_t in1, uint8_t in2) {
    uint8_t ret = 0;
    ret += in1;
    ret += in2;
    return ret;
}

static __attribute__((noinline)) size_t mult_xlen (size_t in1, size_t in2) {
    size_t ret = 1;
    ret *= in1;
    ret *= in2;
    return ret;
}

static __attribute__((noinline)) uint8_t mult_8 (uint8_t in1, uint8_t in2) {
    uint8_t ret = 1;
    ret *= in1;
    ret *= in2;
    return ret;
}

