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
  - Virtual methods tables.
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

### TEST-822 ###

Untrusted Pointer Dereference
\[[CWE-822](https://cwe.mitre.org/data/definitions/822.html)\].


**Notes:**
- The program obtains a value from an untrusted source, converts this 
value to a pointer, and dereferences the resulting pointer.

**FreeRTOS:**
- Implemented.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of untrusted Pointer Dereference.

- The `compare` function compares two strings character by character. 
- The `do_malicious_modification` function: 
  If the pointer is de-referenced for a write operation, the attack 
  might allow modification of critical program state variables,
  cause a crash, or execute code.

------------------

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

**FreeRTOS:**
- Not yet implemented.

**Linux Debian and FreeBSD:**
- Not yet implemented.

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
