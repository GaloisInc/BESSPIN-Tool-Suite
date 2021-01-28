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

**FreeRTOS:**
- Not yet implemented.

**Linux Debian and FreeBSD:**
- Not yet implemented.

------------------

### TEST-INJ-2 ###

Untrusted Data Accessed as Heap Metadata.  Program input exploits a
vulnerability to read or modify heap metadata.  For example, a buffer overflow
of untrusted heap data that overwrites trusted `malloc` metadata in a
neighboring chunk such that a subsequent `free` of that chunk causes the memory
allocator to write untrusted data in trusted memory.

**FreeRTOS:**
- Not yet implemented.

**Linux Debian and FreeBSD:**
- Not yet implemented.

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
- When prompted, FETT writes the leaked `malicious` address to the running
  test's `stdin`.

------------------

### TEST-INJ-4 ###

Untrusted Data Accessed as Memory Address.  The program obtains a value from an
untrusted source and converts this value to a memory address.  Examples of
memory addresses that may be manipulated include:

- Pointers (as in [CWE-822](https://cwe.mitre.org/data/definitions/822.html)).
- Return values.

**FreeRTOS:**
- Not yet implemented.

**Linux Debian and FreeBSD:**
- Not yet implemented.
