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

typedef union {
    uintptr_t num;
    void (* const fn)(void);
} int_fn_union;

void benign(void) {
    printf("<EXECUTING_BENIGN_CODE>\n");
};

void malicious(void) {
    printf("<EXECUTING_MALICIOUS_CODE>\n");
};

#ifdef testgenOnFreeRTOS
void injector(void* params) {
    // Send malicious address as integer.
    MessageBufferHandle_t *msg_buf = (MessageBufferHandle_t*) params;
    uintptr_t address = (uintptr_t) &malicious;
    size_t sent_bytes = xMessageBufferSend(*msg_buf,
                                           &address,
                                           sizeof(address),
                                           // No wait because buffer should be
                                           // large enough to store entire
                                           // message without a reader on the
                                           // other end.
                                           0);
    if (sent_bytes != sizeof(address)) {
        printf("<INVALID>\n");
        printf("Failed to send address over message buffer\n");
    }
    vTaskDelete(NULL);
}

void message_buffer_test(void) {
    // Set function pointer to benign function.
    int_fn_union data = { .fn = benign };

    // Create a message buffer large enough to hold uintptr_t, including message
    // header.
    MessageBufferHandle_t msg_buf =
        xMessageBufferCreate(sizeof(size_t) + sizeof(uintptr_t));
    if (msg_buf == NULL) {
        printf("<INVALID>\n");
        printf("Failed to create message buffer.\n");
        return;
    }

    // Run injector function as it's own task.
    BaseType_t injector_task = xTaskCreate(injector,
                                           "injector",
                                           configMINIMAL_STACK_SIZE * 10,
                                           &msg_buf,
                                           configMAX_PRIORITIES - 1,
                                           NULL);
    if (injector_task != pdPASS) {
        printf("<INVALID>\n");
        printf("Failed to create task.\n");
        return;
    }

    size_t recv_bytes = xMessageBufferReceive(
            msg_buf,
            &data.num,
            sizeof(data.num),
            // Injector has the max priority so it likely ran before
            // this receive call, but allow this task to block for a few
            // seconds in case it's also running at max priority.
            pdMS_TO_TICKS(5000));
    if (recv_bytes != sizeof(data.num)) {
        printf("<INVALID>\n");
        printf("Failed to receive integer over message buffer\n");
        return;
    }

    data.fn();
}
#else  // !testgenOnFreeRTOS
void stdin_test(void) {
    // Set function pointer to benign function.
    int_fn_union data = { .fn = benign };

    // Leak malicious address.
    printf("<malicious address %p>\n", &malicious);
    printf("<LEAKED>\n");

    // Take a number over stdin and store in data.num (thus overwriting data.fn
    // without triggering a const error).
    char* line = NULL;
    size_t len = 0;
    if (getline(&line, &len, stdin) == -1) {
        printf("<INVALID>\n");
        printf("Failed to read from stdin\n");
        free(line);
        return;
    }
    data.num = (uintptr_t) strtoull(line, NULL, 0);
    free(line);
    if (data.num == 0 || data.num == ULLONG_MAX) {
        printf("<INVALID>\n");
        printf("Failed to convert string to integer\n");
        return;
    }

    // Execute injected function pointer.
    data.fn();
}
#endif  // !testgenOnFreeRTOS

int main(void) {
    printf("<BEGIN_INJECTION_TEST>\n");
#ifdef testgenOnFreeRTOS
#ifdef testgenQEMU
    // Not implemented for QEMU due to issues with FreeRTOS tasks on QEMU.
    printf("<QEMU_NOT_IMPLEMENTED>\n");
    printf("FreeRTOS INJ-3 test is not implemented on QEMU.\n");
#else
    message_buffer_test();
#endif
#else
    stdin_test();
#endif
    return 0;
}
