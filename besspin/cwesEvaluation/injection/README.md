# Injection #

The injection class represents architectural weaknesses that allow information
from a less trusted domain to replace information in a more trusted domain in
violation of an explicit or implied policy. Use of the injected information in
the context of the more trusted domain could be detrimental to system operation
or security. Examples of protected information that should not be influenceable
by a less trusted domain include:

- Machine-language instructions of an application, operating system kernel,
  hypervisor, or enclave.
- Internal pointers, including:
  - Return addresses.
  - Virtual method tables.
  - Handlers for interrupts, exceptions, or IRQs.
  - GOT entries.
- Heap metadata.
- Protected information, including credentials or cryptographic keys.
- Internal state of an application, operating system kernel, hypervisor, or
  enclave.

The concept of trust domains is broad. Examples of common trust domain
boundaries include:

- Userspace processes: input received from external sources (sockets, file
  descriptors) is considered less trusted.
- Userspace processes: information transferred from another userspace process
  through interprocess communication (IPC) is considered less trusted.
- Operating system kernel: information received from userspace through system
  calls is considered less trusted.
- Operating system kernel: information received through I/O interfaces with a
  peripheral, including DMA, is considered less trusted.
- Hypervisor: information received from guest operating systems is considered
  less trusted.
- Secure enclaves: externally provided inputs, including all memory outside of
  control of the enclave, are considered less trusted.

Injection could be performed through a variety of mechanisms, including, but
not limited to:

- Buffer overflows.
- Use-after-free.
- Write-what-where primitives, provided by insufficient bounds checking,
  uncontrolled format strings, or protocol-parsing weaknesses.
- DMA.
- Type confusion.
- Memory aliasing.

The thread tying all of these mechanisms together is that the source of the
information is inappropriate for the context in which it is ultimately used.

## Tests ##

This directory contains, or will contain, the following tests.

### TEST-INJ-1 ###

Untrusted Data Accessed as Machine Language Instructions.  Program input
exploits a vulnerability to cause execution of untrusted code which may, for
example:

- Jump to execute additional untrusted code.
- Jump to execute trusted code in an unintended manner, such as in return
  oriented programming.

**Notes:**

- Although the mechanism for obtaining untrusted data differs between FreeRTOS
  and Unix, the basic structure of the test is the same.  This test:
  1. Leaks the address of a buffer.
  2. Places untrusted user data in the buffer.  Specifically, the test places
     the EBREAK opcode in the buffer.
  3. Due to missing bounds checks, places untrusted over the end of the buffer
     and into a stored return pointer.  The test places the address of the
     buffer here.
  4. When returning from a function, execution jumps to the buffer containing
     the EBREAK instruction.
- Because the test overwrites a stored return pointer, it is sensitive to stack
  layout.  It contains sanity checks to determine whether the second write will
  overwrite the return pointer.  The test accomplishes this by comparing the
  value to be overwritten with the address of the `ret_location` label, which
  is the expected value of the return pointer.  If these values do not match
  then the test will score CALL-ERR, indicating that the offset between the
  start of the buffer and the return pointer is incorrect.  BESSPIN re-runs the
  test with different offsets and only scores the test for which it correctly
  locates the stored return pointer.

**FreeRTOS:**
- The FreeRTOS test uses tasks as a source of untrusted information.
- The `shared_task_data_t` struct holds the data shared between the two tasks.
  It contains:
  * A pointer to a `uintptr_t`.
  * A pointer to the expected return value for sanity checking.
- The `injector` function is run in a task, where it:
  1. Takes a pointer to a `shared_task_data_t` as input.
  2. Places the EBREAK opcode in `buf`.
  3. Computes the address of a stored return pointer in the other task using
     `buf` and a known offset.
  4. Overwrites the stored return pointer with the address for `buf`.
  5. Notifies the other task to unblock it.
- The `message_buffer_test` function:
  1. Creates a `shared_task_data_t` where `buf` points to a local stack
     variable `ebreak`.
  2. Creates a task running the `injector` function and passes it a pointer to
     the `shared_task_data_t`.
  3. Waits for a notification from the task.
  4. Returns.  If the return pointer was successfully overwritten, this return
     will jump into the `ebreak` variable.

**Linux Debian and FreeBSD:**
- The Debian and FreeBSD test uses `stdin` as a source of untrusted
  information.
- The `stdin_test` function:
  1. Creates a `uintptr_t` buffer `buf` on the stack and leaks its address.
  2. Takes 4 lines over stdin:
     1. An offset (O1).
     2. A value (V1).
     3. An offset (O2).
     4. A value (V2).
  3. Writes V1 at `buf + O1`.
  4. Writes V2 at `buf + O2`.
  5. Returns.
- Besspin sends the following values to the test program:
  1. The first offset: `0`.
  2. The first value: The EBREAK opcode.
  3. The second offset:  `inj1UnixReturnPointerOffset`.
  4. The second value: The address of `buf`.
- The return of `stdin_test` will then jump to `buf`, but the OS will detect
  execution of non-executable memory and raise a segmentation fault.
  Therefore, the expected score on Unix is DETECTED.

------------------

### TEST-INJ-2 ###

Untrusted Data Accessed as Heap Metadata.  Program input exploits a
vulnerability to read or modify heap metadata.  For example, a buffer overflow
of untrusted heap data that overwrites trusted `malloc` metadata in a
neighboring chunk such that a subsequent `free` of that chunk causes the memory
allocator to write untrusted data in trusted memory.

**Notes:**
- Although the mechanism for obtaining untrusted data and offsets for heap
  metadata differ between FreeRTOS and Debian, the tests are otherwise
  identical.  This test:
  1. Allocates a buffer `untrusted1` to store untrusted data.
  2. Allocates an integer `trusted` to store trusted data, and sets it to `0`.
     This will be allocated directly after `untrusted1`, with the 16 byte
     heap metadata header for `trusted` inbetween.
  3. Takes an untrusted value `index1`.  `index1` is chosen such that it points
     to the size field of heap metadata for `untrusted1`.
  4. Takes an untrusted value `increment1`.  `increment1` is 32, as that
     matches the additional size of the allocation in step 7.
  5. Increments `untrusted1[index]` by `increment1`.
  6. Frees `unstrusted1`.  This places the block at the front of the free list,
     but with size metadata that indicates the block is 32 bytes larger than it
     actually is.
  7. Allocates a buffer `untrusted2` that is 32 bytes larger than `untrusted1`.
     Because of the incorrect size metadata, the allocator will return the
     block of memory that formerly held `untrusted1`.
  8. Takes an untrusted value `index2`.  `index2` points to memory 16 bytes
     after the end of the old `untrusted1` buffer.  This is in bounds for
     `untrusted2`, but overlaps with the allocation for `trusted`.
  9. Takes an untrusted value `increment2`.  `increment2` is 1, but any
     non-zero number would work.
  10. Increments `untrusted2[index2]` by `increment2`.
  11. Branches on `trusted` being nonzero, demonstrating that untrusted data
      has been stored in a trusted variable.

**FreeRTOS:**
- The FreeRTOS test uses tasks as a source of untrusted information.
- `untrusted1` is a buffer of 8 32-bit integers.
- `untrusted2` is a buffer of 16 32-bit integers (32 bytes larger than
  `untrusted1`).
- `index1` is `-3`, as the size header is 12 bytes (3 32-bit ints) before the
  `untrusted1` pointer returned by `pvPortMalloc`.
- `index2` is `12`, which is 16 bytes (4 32-bit ints) beyond the end of the
  `untrusted1` allocation, and therefore just past the 16 byte header for
  `trusted` and into the `trusted` data itself.

**Linux Debian:**
- The Debian test uses `stdin` as a source of untrusted information.
- `untrusted1` is a buffer of 8 64-bit integers.
- `untrusted2` is a buffer of 12 64-bit integers (32 bytes larger than
  `untrusted1`).
- `index1` is `-1`, as the size header is 8 bytes (1 64-bit int) before the
  `untrusted1` pointer returned by `malloc`.
- `index2` is `10`, which is 16 bytes (2 64-bit ints) beyond the end of the
  `untrusted1` allocation, and therefore just past the 16 byte header for
  `trusted` and into the `trusted` data itself.

**FreeBSD:**
- This test is not implemented and scores N/A on FreeBSD as the FreeBSD malloc
  implementation (jemalloc) does not place heap metadata directly adjacent to
  the pointers it returns.

------------------

### TEST-INJ-3 ###

Untrusted Data Accessed as Trusted Data.  Program input exploits a
vulnerability to bypass protection mechanisms that enforce separation of trust
domains.  For example, an exploit overrunning a buffer of untrusted data to
overwrite trusted internal program state.

**Notes:**
- This test overwrites a trusted function pointer with untrusted data, causing
  a change in control flow.
- The `int_fn_union` union contains an integer `num` field and a function
  pointer field `fn`.  The weakness arises from placing untrusted data in
  `num`, then executing `fn`.
- The `benign` function is the intended destination of the function pointer.
- The `malicious` function is the function that the test attempts to execute by
  exploiting the weakness.

**FreeRTOS:**

- The FreeRTOS test uses tasks as a source of untrusted information.
- The `injector` function is run in a task, where it:
  1. Takes a pointer to a message buffer handle as input.
  2. Casts the address of the `malicious` function to a `uintptr_t` and sends
     it over the message buffer.
- The `message_buffer_test` function:
  1. Creates an `int_fn_union`, and initializes the `fn` field to the address
     of the `benign` function.
  2. Creates a message buffer.
  3. Creates a task running the `injector` function, and passes it a pointer to
     the message buffer handler.
  4. Reads a `uintptr_t` from the message buffer handler, and stores it into
     the `num` field of the union.
  5. Executes the `fn` field of the union.

**Linux Debian and FreeBSD:**

- The Debian and FreeBSD test uses `stdin` as a source of untrusted
  information.
- The `stdin_test` function:
  1. Creates an `int_fn_union`, and initializes the `fn` field to the address
     of the `benign` function.
  2. Leaks the address of the `malicious` function over `stdout`.
  3. Reads an integer over `stdin` into the `num` field of the union.
  4. Executes the `fn` field of the union.
- When prompted, BESSPIN writes the leaked `malicious` address to the running
  test's `stdin`.
