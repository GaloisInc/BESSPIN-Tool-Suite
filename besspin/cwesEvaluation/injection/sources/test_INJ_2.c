#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>

#ifdef BESSPIN_FREERTOS
#include <FreeRTOS.h>
#include <message_buffer.h>
#include <task.h>
#else // !BESSPIN_FREERTOS
#include <stdlib.h>
#include "inj_unix_helpers.h"
#include "unbufferStdout.h"
#endif

// Number of elements in untrusted1.
#define UNTRUSTED1_SIZE 8

// Additional bytes beyond the size of untrusted1 to allocate for untrusted2
// buffer.  It must be large enough to run past the header for the trusted
// allocation (16 bytes on both FreeRTOS and Debian) and into the data.
// Allocations are padded out to the next 16 byte boundary and it's easier to
// think about the memory layout when the allocator isn't padding things behind
// our back, so 32 bytes larger than untrusted1 works well.
#define UNTRUSTED2_BYTES_INCREASE 32

// Size of the header for allocations returned by both malloc on Debian and
// pvPortMalloc on FreeRTOS.
#define BLOCK_HEADER_BYTES 16

#ifdef BESSPIN_FREERTOS

/*
 * Each pvPortMalloc allocation has this header placed in front of the returned
 * pointer:
 *
 * typedef struct A_BLOCK_LINK
 * {
 *     struct A_BLOCK_LINK *pxNextFreeBlock;
 *     size_t xBlockSize;
 * } BlockLink_t;
 *
 * We want to overwrite xBlockSize.  This struct is 8 bytes, but FreeRTOS
 * aligns on 16 byte boundaries, so it pads the struct out to 16 bytes.
 * Therefore, the xBlockSize field is 12 bytes (3 32-bit ints) before the
 * pointer returned by pvPortMallon 32 bit systems, and 8 bytes (1 64-bit int)
 * before the pointer on 64 bit systems.
 */
#if __riscv_xlen == 64
#define BLOCK_SIZE_OFFSET -1
#else
#define BLOCK_SIZE_OFFSET -3
#endif

// This is the index to write in `untrusted2` to overwrite the `trusted`
// integer.  It is 16 bytes from the end of the old `untrusted1` buffer, which
// puts it exactly on top of `trusted`.
#if __riscv_xlen == 64
#define TRUSTED_OVERWRITE_INDEX 10
#else
#define TRUSTED_OVERWRITE_INDEX 12
#endif

// Represents a write request between tasks to increment a value in a buffer.
typedef struct {
    // Index in the buffer to write.
    int index;
    // How much to increment the data in buffer[index] by.
    size_t increment;
} buffer_increment_t;

// Send a buffer_increment_t to a task
static bool send_buffer_increment(const MessageBufferHandle_t *msg_buf,
                                  const buffer_increment_t* buffer_increment) {
    size_t sent_bytes = xMessageBufferSend(*msg_buf,
                                           buffer_increment,
                                           sizeof(buffer_increment_t),
                                           // No wait because buffer should be
                                           // large enough to store entire
                                           // message without a reader on the
                                           // other end.
                                           0);
    bool did_send = sent_bytes == sizeof(buffer_increment_t);
    if (!did_send) {
        printf("<INVALID\n");
        printf("Failed to send buffer_increment_t over message buffer\n");
    }
    return did_send;
}

static void injector(void* params) {
    MessageBufferHandle_t *msg_buf = (MessageBufferHandle_t*) params;

    buffer_increment_t inc1, inc2;

    // First increment overwrites size header in `untrusted1`.
    inc1.index = BLOCK_SIZE_OFFSET;
    inc1.increment = UNTRUSTED2_BYTES_INCREASE;


    // Second incremeent overwrites `trusted` via `untrusted2`.
    inc2.index = TRUSTED_OVERWRITE_INDEX;
    inc2.increment = 1;

    if (!send_buffer_increment(msg_buf, &inc1)) {
        vTaskDelete(NULL);
        return;
    }

    send_buffer_increment(msg_buf, &inc2);
    vTaskDelete(NULL);
}

// Receieve and apply a write request from a task.
static bool get_buffer_increment(const MessageBufferHandle_t* msg_buf,
                                 size_t* untrusted,
                                 int untrusted_size) {
    buffer_increment_t increment;
    size_t recv_bytes = xMessageBufferReceive(
            msg_buf,
            &increment,
            sizeof(increment),
            // Injector has the max priority so it likely ran before
            // this receive call, but allow this task to block for a few
            // seconds in case it's also running at max priority.
            pdMS_TO_TICKS(5000));
    bool did_recv = recv_bytes == sizeof(increment);
    if (!did_recv) {
        printf("<INVALID>\n");
        printf("Failed to receive buffer_increment_t over message buffer.\n");
        return false;
    }

    // Check for overflows, but not underflows to metadata.
    if (increment.index >= untrusted_size) {
        printf("<INVALID>\n");
        printf("Tried to overflow buffer.\n");
        return false;
    }

    // If index is negative, then this is the write that overwrites the
    // pvPortMalloc metadata.  Perform a sanity check that this is actually the
    // size field.
    if (increment.index < 0) {
        // The allocator sets the first bit of the size field to 1 to indicate
        // the block is allocated.  We need to mask this out to check the size.
        size_t block_allocated_bit = (size_t) 1 << (__riscv_xlen - 1);

        // Size should be the data size (untrusted_size * sizeof(size_t)) +
        // the header size (BLOCK_HEADER_BYTES)
        if ((((size_t) untrusted[increment.index]) & ~block_allocated_bit) !=
            (untrusted_size * sizeof(size_t)) + BLOCK_HEADER_BYTES) {
            printf("<INVALID>\n");
            printf("Failed to find size header.\n");
            return false;
        }
    }

    // Apply increment
    untrusted[increment.index] += increment.increment;
    return true;
}


static void rtos_test() {
    size_t* untrusted1 = (size_t*) pvPortMalloc(sizeof(size_t)*UNTRUSTED1_SIZE);
    if (untrusted1 == NULL) {
        printf("<INVALID>\n");
        printf("untrusted1 allocation failed.\n");
        return;
    }

    size_t* trusted = (size_t*) pvPortMalloc(sizeof(size_t));
    if (trusted == NULL) {
        printf("<INVALID>\n");
        printf("trusted allocation failed.\n");
        vPortFree(trusted);
        return;
    }

    // `trusted` should be exactly after `untrusted1` (accounting for the
    // header for `trusted`).
    if (trusted != untrusted1 + UNTRUSTED1_SIZE + (BLOCK_HEADER_BYTES / sizeof(size_t*))) {
        printf("<INVALID>\n");
        printf("Trusted allocation not immediately after untrusted1\n");
        vPortFree(untrusted1);
        vPortFree(trusted);
        return;
    }
    *trusted = 0;

    // Start task
    MessageBufferHandle_t msg_buf =
        xMessageBufferCreate(2*sizeof(size_t) + 2*sizeof(buffer_increment_t));
    if (msg_buf == NULL) {
        printf("<INVALID>\n");
        printf("Failed to create message buffer.\n");
        vPortFree(untrusted1);
        vPortFree(trusted);
        return;
    }
    BaseType_t did_create_task = xTaskCreate(injector,
                                             "injector",
                                             configMINIMAL_STACK_SIZE * 10,
                                             &msg_buf,
                                             configMAX_PRIORITIES - 1,
                                             NULL);
    if (did_create_task != pdPASS) {
        printf("<INVALID>\n");
        printf("Failed to create task.\n");
        vPortFree(untrusted1);
        vPortFree(trusted);
        return;
    }

    // Get first increment
    if (!get_buffer_increment(msg_buf, untrusted1, UNTRUSTED1_SIZE)) {
        // From this point on don't free on errors because untrusted1 and
        // trusted overlap.
        return;
    }

    // Free `untrusted1`
    vPortFree(untrusted1);

    // Allocate `untrusted2`.  The block for `untrusted1` will be at the front
    // of the free list, and will allso appear large enough to store
    // `untrusted2` due to the modified metadata.
    int untrusted2_size = UNTRUSTED1_SIZE +
                          (UNTRUSTED2_BYTES_INCREASE / sizeof(size_t));
    size_t* untrusted2 = (size_t*) pvPortMalloc(sizeof(size_t) * untrusted2_size);

    // Sanity check that the same memory location was returned.
    if (untrusted1 != untrusted2) {
        printf("<INVALID>\n");
        printf("untrusted2 allocation not placed at same memory address as untrusted1.\n");
        return;
    }

    // Get second increment, which will overwrite trusted
    if (!get_buffer_increment(msg_buf, untrusted2, untrusted2_size)) {
        return;
    }

    if (*trusted) {
        printf("<EXECUTING_MALICIOUS_CODE>\n");
    } else {
        printf("<EXECUTING_BENIGN_CODE>\n");
    }

    // Don't free untrusted2 or trusted as they are overlapping memory regions.
}

#endif  // BESSPIN_FREERTOS
#ifdef BESSPIN_DEBIAN

static bool get_buffer_increment(int64_t* untrusted, int64_t untrusted_size) {
    // Read index
    int index = read_int();

    // Check for overflows, but not underflows to metadata.
    if (index >= untrusted_size) {
        printf("<INVALID>\n");
        printf("Tried to overflow buffer.\n");
        return false;
    }

    // If index is negative, then this is the write that overwrites the malloc
    // metadata.  Perform a sanity check that this is actually the size field.
    // It should be the data size (untrusted_size * sizeof(int64_t) + the
    // header size (BLOCK_HEADER_BYTES) + the in use bit (1).
    if (index < 0 &&
        untrusted[index] != (untrusted_size * sizeof(int64_t)) +
                            BLOCK_HEADER_BYTES +
                            1) {
        printf("<INVALID>\n");
        printf("Failed to find size header\n");
        return false;
    }

    // Read and apply increment
    int64_t increment = (int64_t) read_int();
    untrusted[index] += increment;

    return true;
}

static void debian_test() {
    int64_t* untrusted1 = (int64_t*) malloc(sizeof(int64_t)*UNTRUSTED1_SIZE);
    if (untrusted1 == NULL) {
        printf("<INVALID>\n");
        printf("untrusted1 allocation failed.\n");
        return;
    }

    int64_t* trusted = (int64_t*) malloc(sizeof(int64_t));
    if (trusted == NULL) {
        printf("<INVALID>\n");
        printf("trusted allocation failed.\n");
        free(untrusted1);
        return;
    }

    // `trusted` should be exactly after `untrusted1` (accounting for the
    // header for `trusted`).
    if (trusted != untrusted1 + UNTRUSTED1_SIZE + (BLOCK_HEADER_BYTES / sizeof(int64_t*))) {
        printf("<INVALID>\n");
        printf("Trusted allocation not immediately after untrusted1\n");
        free(untrusted1);
        free(trusted);
        return;
    }
    *trusted = 0;

    // Get first increment
    fprintf(stderr, "<READY FOR INPUT>\n");
    if (!get_buffer_increment(untrusted1, UNTRUSTED1_SIZE)) {
        // From this point on don't free on errors because untrusted1 and
        // trusted overlap.
        return;
    }

    // Free `untrusted1`
    free(untrusted1);

    // Allocate `untrusted2`.  The block for `untrusted1` will be at the front
    // of the free list, and will allso appear large enough to store
    // `untrusted2` due to the modified metadata.
    int untrusted2_size = UNTRUSTED1_SIZE +
                          (UNTRUSTED2_BYTES_INCREASE / sizeof(int64_t));
    int64_t* untrusted2 = (int64_t*) malloc(sizeof(int64_t) * untrusted2_size);

    // Sanity check that the same memory location was returned.
    if (untrusted1 != untrusted2) {
        printf("<INVALID>\n");
        printf("untrusted2 allocation not placed at same memory address as untrusted1.\n");
        return;
    }

    // Get second increment, which will overwrite trusted
    if (!get_buffer_increment(untrusted2, untrusted2_size)) {
        return;
    }

    if (*trusted) {
        printf("<EXECUTING_MALICIOUS_CODE>\n");
    } else {
        printf("<EXECUTING_BENIGN_CODE>\n");
    }

    // Don't free untrusted2 or trusted as they are overlapping memory regions.
}
#endif  // BESSPIN_DEBIAN

int main(void) {
    printf("<BEGIN_INJECTION_TEST>\n");
#ifdef BESSPIN_FREERTOS
#ifdef BESSPIN_QEMU
    // Not implemented for QEMU due to issues with FreeRTOS tasks on QEMU.
    printf("<QEMU_NOT_IMPLEMENTED>\n");
    printf("FreeRTOS INJ-2 test is not implemented on QEMU.\n");
#else  // !testgenOnQEMU
    rtos_test();
#endif  // !testgenOnQEMU
#else  // !BESSPIN_FREERTOS
    unbufferStdout();
#ifdef BESSPIN_FREEBSD
    // Not implemented for FreeBSD due to jemalloc not placing metadata
    // directly before returned pointers
    printf("<FREEBSD_NOT_IMPLEMENTED>\n");
    printf("INJ-2 test is not implemented on FreeBSD\n");
#else   // !BESSPIN_FREEBSD
    debian_test();
#endif  // !testgeonOnFreeBSD
#endif  // !BESSPIN_FREERTOS

    return 0;
}
