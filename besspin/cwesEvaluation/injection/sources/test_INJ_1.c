#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#ifdef BESSPIN_FREERTOS
#include <FreeRTOS.h>
#include <message_buffer.h>
#include <task.h>
#else  // !BESSPIN_FREERTOS
#include <stdlib.h>
#include <time.h>
#include "inj_unix_helpers.h"
#include "unbufferStdout.h"
#endif  // !BESSPIN_FREERTOS

#include "testsParameters.h"

// EBREAK opcode
#define EBREAK 0b00000000000100000000000001110011

// Return `true` if `ptr` points to the stored return pointer
static bool is_return_pointer(uintptr_t* ptr, const void** expected_ret) {
    uintptr_t ptr_int = (uintptr_t) *ptr;
    uintptr_t expected_int = (uintptr_t) *expected_ret;
    // `ptr` should point to `expected_int` (within a few bytes).
    if (ptr_int > expected_int || expected_int - ptr_int > 8) {
        printf("<INVALID>\n");
        printf("Return pointer not at expected offset.\n");
        return false;
    }
    return true;
}

#ifdef BESSPIN_FREERTOS

// FreeRTOS test has 8 parts (will try offsets 1 through 8)
#define NUM_OF_TEST_PARTS 8

#define RET_PTR_OFFSET TESTGEN_TEST_PART

typedef struct {
    uintptr_t* buf;
    // The expected stored return value (for sanity checking)
    const void** expected_ret;
} shared_task_data_t;

// Handle for task to notify after performing injection
static TaskHandle_t xInjectedTaskHandle = NULL;

static void injector(void* params) {
    shared_task_data_t *data = (shared_task_data_t*) params;

    // Put an EBREAK opcode in the buffer
    *data->buf = EBREAK;

    // Compute the address of the stored return pointer in the parent task
    uintptr_t* ret = data->buf + RET_PTR_OFFSET;

    // Sanity check that `ret` points to the stored return pointer
    if (!is_return_pointer(ret, data->expected_ret)) {
        vTaskDelete(NULL);
        return;
    }

    // Overwrite parent's stored return pointer with address of buffer
    *ret = (uintptr_t) data->buf;

    // Unblock parent task
    xTaskNotifyGive(xInjectedTaskHandle);

    vTaskDelete(NULL);
}

static void message_buffer_test(const void** ret_ptr) {
    // Setup shared data
    uintptr_t ebreak;
    shared_task_data_t data = {
        .buf = &ebreak,
        .expected_ret = ret_ptr,
    };
    xInjectedTaskHandle = xTaskGetCurrentTaskHandle();

    // Run injector function as it's own task.
    BaseType_t task_created = xTaskCreate(injector,
                                          "injector",
                                          configMINIMAL_STACK_SIZE * 10,
                                          &data,
                                          configMAX_PRIORITIES - 1,
                                          NULL);
    if (task_created != pdPASS) {
        printf("<INVALID>\n");
        printf("Failed to create task.\n");
        return;
    }

    // Wait for task notification before returning
    if (!ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(5000))) {
        printf("<INVALID>\n");
        printf("Failed to receive task notification from injector task\n");
        return;
    }

    // If injection succeeded, then the return from this function will jump
    // into the ebreak variable.
    printf("<RETURNING>\n");
}

#else  // !BESSPIN_FREERTOS

// Read a uintptr_t from stdin
// Read two values from stdin, the first is an index, and the second is a
// value.  Set buf[index] = value.
static void write_buf(uintptr_t* buf, const void** expected_ret_ptr) {
    uintptr_t offset = read_uintptr_t();
    uintptr_t value = read_uintptr_t();

    uintptr_t* write_location = buf + offset;

    if (offset) {
        // If offset is nonzero, this function is overwriting the stored return
        // pointer with the address of the buffer.  `offset` should point to
        // `expected_ret_ptr` (within a few bytes) and `value` should be the
        // start of `buf`.
        if (!is_return_pointer(write_location, expected_ret_ptr)) {
            exit(0);
        }
        if ((uintptr_t*) value != buf) {
            printf("<INVALID>\n");
            printf("Return pointer overwrite value does not match address of buffer.\n");
            exit(0);
        }
    } else {
        // If the offset is zero, this function is writing the injected opcode.
        if (value != EBREAK) {
            printf("<INVALID>\n");
            printf("Unexpected injected opcode.\n");
            exit(0);
        }
    }

    *write_location = value;
}


static void stdin_test(const void** expected_ret_ptr) {
    uintptr_t buf[2];

    // Leak buffer address and offset
    fprintf(stderr, "<buffer address %p>\n", &buf[0]);
    fprintf(stderr, "<LEAKED>\n");

    // First read into buffer should place EBREAK in buf[0]
    write_buf(buf, expected_ret_ptr);

    // Second read into buffer should overwrite stored return pointer with the
    // address of buf
    write_buf(buf, expected_ret_ptr);

    // Print before returning so that scoring can differentiate between
    // segfaults occurring in the return, and segfaults occurring due to the
    // previous out of bounds writes.
    printf("<RETURNING>\n");

#ifdef BESSPIN_DEBIAN
    // Short sleep to ensure previous print completes and does not interleave
    // with kmesg segfault message.  Use nanosleep syscall instead of sleep for
    // bare metal support.
    struct timespec duration = { .tv_sec = 1, .tv_nsec = 0 };
    int do_sleep = 1;
    while (do_sleep) {
        // Run nanosleep in loop until duration has elapsed because nanosleep
        // can return early and store the remaining time in its second
        // argument.  See nanosleep(2) man page for more.
        do_sleep = nanosleep(&duration, &duration);
    }
#endif

    // Return should jump into buf.  Debian and FreeBSD should detect execution
    // of non-executable memory and raise a segmentation fault.
}
#endif  // !BESSPIN_FREERTOS

int main(void) {
    printf("<BEGIN_INJECTION_TEST>\n");
    const void* ret_ptr = &&ret_location;
#ifdef BESSPIN_FREERTOS
    printf("\n<OFFSET %d>\n", RET_PTR_OFFSET);
#ifdef BESSPIN_QEMU
    // Not implemented for QEMU due to issues with FreeRTOS tasks on QEMU.
    printf("<QEMU_NOT_IMPLEMENTED>\n");
    printf("FreeRTOS INJ-1 test is not implemented on QEMU.\n");
#else  // !BESSPIN_QEMU
    message_buffer_test(&ret_ptr);
#endif  // !BESSPIN_QEMU
#else  // !BESSPIN_FREERTOS
    unbufferStdout();
    stdin_test(&ret_ptr);
#endif  // !BESSPIN_FREERTOS
ret_location:
    if (ret_ptr != &&ret_location) {
        // Overwrote the local variable `ret_ptr`, not the actual return
        // pointer.  These two cases are indistinguishable to the return offset
        // check function, so the test needs to check here.
        printf("<INVALID>\n");
        printf("Overwrote main's ret_ptr local variable\n");
    }
    printf("<END_INJECTION_TEST>\n");
    return 0;
}
