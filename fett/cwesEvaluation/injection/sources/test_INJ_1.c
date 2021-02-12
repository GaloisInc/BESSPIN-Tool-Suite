#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#ifdef testgenOnFreeRTOS
#include <FreeRTOS.h>
#include <message_buffer.h>
#include <task.h>
#else  // !testgenOnFreeRTOS
#include <limits.h>
#include <stdlib.h>
#endif  // !testgenOnFreeRTOS

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

#ifdef testgenOnFreeRTOS

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

#else  // !testgenOnFreeRTOS

// Read a uintptr_t from stdin
static uintptr_t read_value() {
    char* line = NULL;
    size_t len = 0;
    if (getline(&line, &len, stdin) == -1) {
        printf("<INVALID>\n");
        printf("Failed to read from stdin\n");
        free(line);
        exit(0);
    }
    uintptr_t value = (uintptr_t) strtoull(line, NULL, 0);
    free(line);
    if (value == ULLONG_MAX) {
        printf("<INVALID>\n");
        printf("Failed to convert string to integer\n");
        exit(0);
    }
    return value;
}

// Read two values from stdin, the first is an index, and the second is a
// value.  Set buf[index] = value.
static void write_buf(uintptr_t* buf, const void** expected_ret_ptr) {
    uintptr_t offset = read_value();
    uintptr_t value = read_value();

    uintptr_t* write_location = buf + offset;

    if (offset) {
        // If offset is nonzero, this function is overwriting the stored return
        // pointer with the address of the buffer.  `offset` should point to
        // `expected_ret_ptr` (within a few bytes) and `value` should be the
        // start of `buf`.
        uintptr_t write_int = (uintptr_t) *write_location;
        uintptr_t expected_int = (uintptr_t) *expected_ret_ptr;
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
    printf("<buffer address %p>\n", &buf[0]);
    printf("<LEAKED>\n");

    // First read into buffer should place EBREAK in buf[0]
    write_buf(buf, expected_ret_ptr);

    // Second read into buffer should overwrite stored return pointer with the
    // address of buf
    write_buf(buf, expected_ret_ptr);

    // Print before returning so that scoring can differentiate between
    // segfaults occuring in the return, and segfaults occuring due to the
    // previous out of bounds writes.
    printf("<RETURNING>\n");

#ifdef testgenOnDebian
    // Short sleep to ensure previous print completes and does not interleave
    // with kmesg segfault message.
    sleep(1);
#endif

    // Return should jump into buf.  Debian and FreeBSD should detect execution
    // of non-executable memory and raise a segmentation fault.
}
#endif  // !testgenOnFreeRTOS

int main(void) {
    printf("<BEGIN_INJECTION_TEST>\n");
    const void* ret_ptr = &&ret_location;
#ifdef testgenOnFreeRTOS
    printf("\n<OFFSET %d>\n", RET_PTR_OFFSET);
#ifdef testgenQEMU
    // Not implemented for QEMU due to issues with FreeRTOS tasks on QEMU.
    printf("<QEMU_NOT_IMPLEMENTED>\n");
    printf("FreeRTOS INJ-1 test is not implemented on QEMU.\n");
#else  // !testgenOnQEMU
    message_buffer_test(&ret_ptr);
#endif  // !testgenOnQEMU
#else  // !testgenOnFreeRTOS
    stdin_test(&ret_ptr);
#endif  // !testgenOnFreeRTOS
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
