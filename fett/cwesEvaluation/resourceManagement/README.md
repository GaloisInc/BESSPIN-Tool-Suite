# Resource Management #

This class of vulnerabilities allows improper use of the hardware
resources that, in turn, allow external takeover of hardware
resources.  This includes improper access to hardware resources such
as memory, CPU, and communication and/or preventing valid users from
gaining access to these resources.

This directory has all the tests to evaluate resource management
vulnerabilities. 
The [testgen progress spreadsheet](https://docs.google.com/spreadsheets/d/1CNLjQN4VRd9_hAgm4UTgeuvEYDbKerKS5G_X0KlsMgA/edit?usp=sharing) 
logs the progress of which tests are implemented on which OS, and
which system calls/modules should be supported.

Note that each CWE has one test associated with it, however, a certain
test could be testing other CWEs as well.  In other words, to claim
that a processor does not have a certain CWE means that it passes all
the tests that are relevant to the CWE in question.

## Scoring Approach ##

Each test attempts to show the existence of a weakness, and then reports what happens. If the processor reacts to the attempt by blocking it or detecting it, then they score `NONE` or `DETECTED` respectively. If they do not react, and the test runs to completion, then the score is `HIGH` conveying the existence of the weakness related to this test.   
In case of multi-part tests, the overall test score is the minimum score achieved among this test's parts.   

## MAL (Memory Allocation and Deallocation Bugs) ##

The software improperly deallocates allocated memory or uses an object
after its lifetime.
\[[more](https://samate.nist.gov/BF/Classes/MAL.html)\]

Related CWEs:

### TEST-188 ###

Reliance on Data or Memory Layout \[[CWE-188](https://cwe.mitre.org/data/definitions/188.html)\].

**Related CWEs**
- [CWE-435](https://cwe.mitre.org/data/definitions/435.html).  
- [CWE-1105](https://cwe.mitre.org/data/definitions/1105.html).  
- [CWE-198](https://cwe.mitre.org/data/definitions/198.html).
- [CWE-137](https://cwe.mitre.org/data/definitions/137.html).  


**Notes:**
- The software makes invalid assumptions about how protocol data 
  or memory is organized at a lower level, resulting in unintended program behavior.  

**FreeRTOS:**
- Implemented.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of a calculating an offset relative to another 
  field to pick out a specific piece of data on the stack memory segment. 
   
- The `example_byte_past` function: In this example the memory address of variable `e` 
  is derived by adding 1 to the address of variable `d`. This derived address is then used 
  to assign the value `e` to the variable `e`. Here, variable `e` may not be one byte past `d` and 
  it depends of the protocol implementation.
- The `example_byte_in_front` function: The similar explanation like in the previous example
  except that the variable `b` may be one byte in front of `a`. 
- The `example_three_bytes_past` function: In this example variable `h` 
  may be three bytes past the variable `g`.
- The `example_three_bytes_in_front` function: In this example variable `v` 
  may be three bytes in front of the variable `u`.
- The `example_input_args_past_on_stack` function: The similar as previous example related to the 
  byte past, except that arguments are considered on the stack.

### TEST-825 ###

Expired Pointer Dereference \[[CWE-825](https://cwe.mitre.org/data/definitions/825.html)\].

**Related CWEs**
- [CWE-627](https://cwe.mitre.org/data/definitions/627.html).  
- [CWE-415](https://cwe.mitre.org/data/definitions/415.html).  
- [CWE-119](https://cwe.mitre.org/data/definitions/119.html).  
- [CWE-416](https://cwe.mitre.org/data/definitions/416.html).  
- [CWE-562](https://cwe.mitre.org/data/definitions/562.html).  
- [CWE-125](https://cwe.mitre.org/data/definitions/125.html). 
- [CWE-787](https://cwe.mitre.org/data/definitions/787.html). 

**Notes:**
- The program dereferences a pointer that contains a location for
  memory that was previously valid, but is no longer valid.

**FreeRTOS:**
- Implemented through the use of `pvPortMalloc`/`pvPortFree`.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of a ``free`` operation as
  follows. 
- The  `test_double_free` function shows freeing a pointer variable
  more than once.
- The `test_free_no_longer_valid` function shows freeing a pointer
  after copying a string value into destination array using the
  `strcpy` function. This pointer is later incorrectly used in the
  `printf` function. When freeing pointers, be sure to set them to
  `NULL` once they are freed. 
- The utilization of multiple or complex data structures may lower the
  usefulness of this strategy. 

### TEST-761 ###

Free of Pointer not at Start of Buffer 
\[[CWE-761](https://cwe.mitre.org/data/definitions/761.html)\].

**Related CWEs**
- [CWE-623](https://cwe.mitre.org/data/definitions/623.html).
- [CWE-399](https://cwe.mitre.org/data/definitions/399.html).
- [CWE-465](https://cwe.mitre.org/data/definitions/465.html).
 
**Notes:**
- The application calls `free()` on a pointer to a memory resource
  that was allocated on the heap, but the pointer is not at the start
  of the buffer.

**FreeRTOS:**
- Implemented through the use of `pvPortMalloc`/`pvPortFree`.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of a `free` operation call
  in the middle of a character search algorithm.
- The `contains_char_malicious` function dynamically allocates a
  buffer to hold a string and then searches for a specific character.
  After completing the search, the programmer attempts to release the
  allocated memory and returns `SUCCESS` or `FAILURE` to the caller
- Note: if the character is not at the beginning of the string, or if
  it is not in the string at all, then the pointer will not be at the
  start of the buffer when the programmer frees it and it will result
  with the exception.
- The `contains_char_valid` function shows that instead of freeing the
  pointer in the middle of the buffer, the programmer can use an
  indexing pointer to step through the memory or abstract the memory
  calculations by using array indexing.  There are four scenarios
  considered in the test example:
  - Providing an existing character in the `contains_char_valid`
    operation will result with success.
  - Providing a non-existing character in the `contains_char_valid`
    will result with a failure but the program will not crash
    abruptly.
  - Providing an existing character in the `contains_char_malicious`
    operation will result with success.
  - Providing a non-existing character in the
    `contains_char_malicious` will result with a failure and program
    will crash abruptly.
 
### TEST-762 ###

Mismatched Memory Management Routines \[[CWE-762](https://cwe.mitre.org/data/definitions/762.html)\].

**Related CWEs**
- [CWE-763](https://cwe.mitre.org/data/definitions/763.html).  
- [CWE-590](https://cwe.mitre.org/data/definitions/590.html).  
- [CWE-399](https://cwe.mitre.org/data/definitions/399.html).  


**Notes:**
- The application attempts to return a memory resource to the system,
  but it calls a release function that is not compatible with the function 
  that was originally used to allocate that resource.  

**FreeRTOS:**
- Implemented through the use of `pvPortMalloc`/`pvPortFree`.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of a ``free`` operation as
  follows. 
- The  `array_allocated_globally` function: The array is allocated globally, 
  as part of the `data segment` of memory and the programmer attempts to call 
  `free()` on the array. The `free()` function can realize memory on the Heap 
  memory segment only.
- The `correct_memory_free` function shows proper way of freeing 
  memory located by the `malloc` function on the Heap memory segment.
- The `wrong_memory_free` function: The array `b` is allocated 
  automatically on the `stack` as a local variable and the programmer 
  attempts to call `free()` on the array.
     
### TEST-763 ###

Release of Invalid Pointer or Reference \[[CWE-763](https://cwe.mitre.org/data/definitions/763.html)\].

**Related CWEs**
- [CWE-404](https://cwe.mitre.org/data/definitions/404.html).  
- [CWE-761](https://cwe.mitre.org/data/definitions/761.html).  
- [CWE-762](https://cwe.mitre.org/data/definitions/762.html).  


**Notes:**
- The application attempts to return a memory resource to the system, 
  but calls the wrong release function or calls the appropriate release 
  function incorrectly. Usually the program does not release or 
  incorrectly releases a resource before it is made available for re-use. 

**FreeRTOS:**
- Implemented through the use of `pvPortMalloc/vPortFree`.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of a ``free`` operation as
  follows. 
- The  `wrong_shift_address_assignment`: The `free()` has been provided 
  a pointer to `x` in the middle of the allocated memory block.
  This means that, the function `free()` has no idea where the block
  starts or ends, therefore throwing an error.
- The `wrong_address_assignment` function shows wrong address assignment 
  to the pointer, which leads to error saying that p no longer points 
  to dynamically allocated memory. Hence it is incorrect to call `free()` 
  with it. 
  
### TEST-562 ###

Return of Stack Variable Address \[[CWE-562](https://cwe.mitre.org/data/definitions/825.html)\].

**Related CWEs**
- [CWE-758](https://cwe.mitre.org/data/definitions/758.html).
- [CWE-672](https://cwe.mitre.org/data/definitions/672.html).
- [CWE-825](https://cwe.mitre.org/data/definitions/825.html).
- [CWE-1006](https://cwe.mitre.org/data/definitions/1006.html).

**Notes:**
- A function returns the address of a stack variable, which will cause
  unintended program behavior, typically in the form of a program crash.

**FreeRTOS:**
- Implemented through the use of `pvPortMalloc`/`pvPortFree`.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of address stack allocation. 
- The `fill_array` function shows an address of stack memory
  associated with local variable `a` returned. This will lead to the
  program crash caused when attempting to print elements.
- The `fill_array_with_malloc` is recommended way of allocating memory
  on the stack.
  
### TEST-415 ###

Double Free \[[CWE-415](https://cwe.mitre.org/data/definitions/415.html)\].

**Related CWEs**
- [CWE-666](https://cwe.mitre.org/data/definitions/666.html).
- [CWE-675](https://cwe.mitre.org/data/definitions/675.html).
- [CWE-825](https://cwe.mitre.org/data/definitions/825.html).
- [CWE-123](https://cwe.mitre.org/data/definitions/123.html).
- [CWE-416](https://cwe.mitre.org/data/definitions/416.html).
- [CWE-364](https://cwe.mitre.org/data/definitions/364.html).

**Notes:**
- The product calls `free()` twice on the same memory address, 
  potentially leading to modification of unexpected memory locations.

**FreeRTOS:**
- Implemented through the use of `pvPortMalloc`/`pvPortFree`.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of double `free`. 
  
### TEST-416 ###

Use After Free \[[CWE-416](https://cwe.mitre.org/data/definitions/416.html)\].

**Related CWEs**
- [CWE-825](https://cwe.mitre.org/data/definitions/825.html).
- [CWE-123](https://cwe.mitre.org/data/definitions/123.html).
- [CWE-415](https://cwe.mitre.org/data/definitions/415.html).
- [CWE-364](https://cwe.mitre.org/data/definitions/364.html).
- [CWE-120](https://cwe.mitre.org/data/definitions/120.html).

**Notes:**
- Referencing memory after it has been freed can cause a program to crash, 
use unexpected values, or execute code.

**FreeRTOS:**
- Implemented through the use of `pvPortMalloc`/`pvPortFree`.

**Linux Debian and FreeBSD:** 
- The test demonstrates the improper use of pointer that points to de-allocated 
memory as well as consequences of double `free()`. 

### TEST-911 ###

Improper Update of Reference Count \[[CWE-911](https://cwe.mitre.org/data/definitions/911.html)\].

**Related CWEs**
- [CWE-664](https://cwe.mitre.org/data/definitions/664.html).  
- [CWE-672](https://cwe.mitre.org/data/definitions/672.html).  
- [CWE-772](https://cwe.mitre.org/data/definitions/772.html).  

**Notes:**
- The software uses a reference count to manage a resource, 
  but it does not update or incorrectly updates the reference count.

**FreeRTOS:**
- Implemented through the use of `pvPortMalloc`/`pvPortFree`.

**Linux Debian and FreeBSD:** 
- There are two tests showing the implicit reference count 
  in context of UAF `use-after-free` legacy c code.
- The `correct_implicit_reference_count` function shows 
  how `UAF` errors are tackled by the implicit pointer coupled 
  with the reference counters.
- The `unknown_implicit_reference_count` function shows the practical 
  hurdles in precise reference counting. There are two problems.
  The first one is that the `chunk` is declared as an ordinary array, 
  the compiler cannot provide any information with regard to the existence 
  of a pointer inside at runtime. 
  The second practical problem can be described as follows: 
  When `ptrC->data` is set to 1, the previously stored pointer, 
  `ptrC->next`, is simultaneously overwritten by the same value.
  From programmer's prospective we need to decrease reference count, 
  but from the compiler's view point it is just the store of the integer type, 
  so additional analysis is needed. 
  
  

## PTR (NULL or Incorrect Pointer Dereference Class) ##

The software improperly dereferences incorrect or null
pointer. \[[more](https://samate.nist.gov/BF/Classes/PTR.html)\].

### TEST-476 ###

`NULL` Pointer Dereference
\[[CWE-476](https://cwe.mitre.org/data/definitions/476.html)\].

**Related CWEs**
- [CWE-362](https://cwe.mitre.org/data/definitions/362.html).  
- [CWE-665](https://cwe.mitre.org/data/definitions/665.html).  

**Notes:**
- A `NULL` pointer dereference occurs when the application
  dereferences a pointer that it expects to be valid, but is `NULL`,
  typically causing a crash or exit.

**FreeRTOS:**
- Implemented.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of a read and write operation
  when the application dereferences a `NULL` pointer trying to read
  from, or assign to it.
- The `regular_test` function shows valid pointer dereference. 
- The `malicious_test_read` function shows an example of `NULL` pointer
  trying to read it.
- The `malicious_test_write` function shows an example of `NULL` pointer
  trying to write it.
- This weakness results in a fact that the processor was able to
  detect the violation and it also prevented the test from continuing
  with the breach.

### TEST-468 ###

Free of Pointer not at Start of Buffer
\[[CWE-468](https://cwe.mitre.org/data/definitions/468.html)\].

**Related CWEs**
- [CWE-682](https://cwe.mitre.org/data/definitions/682.html).
- [CWE-465](https://cwe.mitre.org/data/definitions/465.html).
 
**Notes:**
- In C, one may often accidentally refer to the wrong memory due to
  the semantics of when math operations are implicitly scaled.

**FreeRTOS:**
- Implemented.

**Linux Debian and FreeBSD:** 
Pointer arithmetic in C is automatically scaled according to the size
of the data type.  For example, if the type of `p` is `T*` and `sizeof(T)
== 4`, then the expression `p+1` adds 4 bytes to `p`.

- The test demonstrates the consequences of a correctly scaled and
  incorrectly scaled pointers in two functions.
- The `example_bad_scaled` shows pointer arithmetic where it appears
  likely that the programmer has forgotten that the offset is
  automatically scaled.  Recommendation: Cast to the correct type
  before using pointer arithmetic. For example, if the type of `p` is
  `int*` but it really points to an array of type `double[]` then use
  the syntax `(double*)p + k` to get a pointer to the `k`'th element
  of the array.
- The `example_good_scaled` function shows  how to use the array
  subscript operator rather than pointer arithmetic. For example,
  replace `*(p+k)` with `p[k]`. 

### TEST-562 ###

Return of Stack Variable Address
\[[CWE-562](https://cwe.mitre.org/data/definitions/562.html)\].

**Notes:**

*Per NIST*: A function returns the address of a stack variable, which
will cause unintended program behavior, typically in the form of a
crash.

The implicit allocation is trivially implemented in a function 
`char* f(void)` that returns a stack-allocated buffer.  Note that 
a decent C compiler will warn about such code, but will happily
generate a binary for this undefined behavior.

**FreeRTOS:**
- Unimplemented as of yet.

**Linux Debian and FreeBSD:** 
- Implemented and tested in Qemu.

### TEST-690 ###

Unchecked Return Value to `NULL` Pointer Dereference
\[[CWE-690](https://cwe.mitre.org/data/definitions/690.html)\].

**Related CWEs**
- [CWE-252](https://cwe.mitre.org/data/definitions/252.html).
- [CWE-476](https://cwe.mitre.org/data/definitions/476.html).
- [CWE-119](https://cwe.mitre.org/data/definitions/119.html).

**Notes:**
- The product does not check for an error after calling a function
  that can return with a `NULL` pointer if the function fails, which
  leads to a resultant `NULL` pointer dereference.

**FreeRTOS:**
- Implemented through the use of `pvPortMalloc`/`pvPortFree`.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of a `strcpy` operation
  when the application copying from a `NULL` pointer and non `NULL`
  pointer source.
- The `test_regular` function shows a valid pointed by source
  (including the `NULL` character) to the character array destination.
- The `test_malicious` function will fail due to `NULL` pointer
  de-referencing.
- While unchecked return value are not limited to returns of `NULL`
  pointer, function return `NULL` to indicate an error status.  When
  this error condition is not checked, a `NULL` pointer dereference
  can occur.

### TEST-588 ###

Attempt to Access Child of a Non-structure Pointer
\[[CWE-588](https://cwe.mitre.org/data/definitions/588.html)\].

**Related CWEs**
- [CWE-758](https://cwe.mitre.org/data/definitions/758.html).
- [CWE-704](https://cwe.mitre.org/data/definitions/704.html).
- [CWE-465](https://cwe.mitre.org/data/definitions/465.html).
- [CWE-569](https://cwe.mitre.org/data/definitions/569.html).

**Notes:**
- Casting a non-structure type to a structure type and accessing a field 
  can lead to memory access errors or data corruption.

**FreeRTOS:**
- Implemented.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of a casting  operation
  when the  void pointer and scalar pointer are cast as structure pointer.
 
- The `struct_pointer_cast_of_void_pointer` function: 
  The void pointer `vp`, is cast as a struct pointer. 
  The result is an exception `EXP-BAD_ACCESS` signal 
  handled by the emulated try catch block.
- The `struct_pointer_cast_of_scalar_pointer` function: 
  In this test, the pointer `p` of type integer is cast as a pointer of type struct. 
  The result is an exception `EXP-BAD_ACCESS` signal 
  handled by the emulated try catch block.

## RLR (Resources Limits and Releasing) ##

This is a custom sub-class that we use to group some of the interleaved CWEs. The sources of this sub-class have the prefix `test_rlr_`. 

**CWEs**

- [CWE-400](https://cwe.mitre.org/data/definitions/400.html): Uncontrolled Resource Consumption.
- [CWE-404](https://cwe.mitre.org/data/definitions/404.html): Improper Resource Shutdown or Release.
- [CWE-770](https://cwe.mitre.org/data/definitions/770.html): Allocation of Resources Without Limits or Throttling.
- [CWE-771](https://cwe.mitre.org/data/definitions/771.html): Missing Reference to Active Allocated Resource.
- [CWE-772](https://cwe.mitre.org/data/definitions/772.html): Missing Release of Resource after Effective Lifetime.
- [CWE-789](https://cwe.mitre.org/data/definitions/789.html): Uncontrolled Memory Allocation.

**Tests**
A. No limit to allocated resources. The related CWEs are [CWE-400](https://cwe.mitre.org/data/definitions/400.html), [CWE-770](https://cwe.mitre.org/data/definitions/770.html), and [CWE-789](https://cwe.mitre.org/data/definitions/789.html). This is tested by the following:
    A1. Heap exhaustion.
    A2. Stack exhaustion.
B. Losing references to actively allocated resources. The related CWEs are [CWE-400](https://cwe.mitre.org/data/definitions/400.html), and [CWE-771](https://cwe.mitre.org/data/definitions/771.html). This is tested by two concepts:
    B1. Lack of.
    B2. Error.
C. Not closing/returning/releasing a resource. The related CWEs are [CWE-400](https://cwe.mitre.org/data/definitions/400.html), [CWE-404](https://cwe.mitre.org/data/definitions/404.html), and [CWE-772](https://cwe.mitre.org/data/definitions/772.html).
D. Incorrectly releasing a resource before actually stopping to use it. The related CWE is [CWE-404](https://cwe.mitre.org/data/definitions/404.html).

### TEST - HEAP EXHAUSTION ###

The source file is `test_rlr_heapExhaust.c`. The test calls a function that allocates a lot of memory without freeing all of it. The RM seed is used in this test to randomize the amount of memory allocated at each malloc call, and to randomize the scarce calls to free. Whether there is a security protection or not, this test is destined to collapse because the system has to run out of memory at some point. 

### TEST - STACK EXHAUSTION ###

The source file is `test_rlr_stackExhaust.c`. The test implements three similar functions that just allocates 100 bytes on the stack, and then call a dispatch function that chooses one of three functions to call, and so on recursively. Randomization is in the value that is filled in the stack and the order of allocation. Similar to the heap exhaustion test, whether there is a security protection or not, this test is destined to collapse. On Debian and FreeRTOS/FreeBSD on qemu, this segfaults. For both FreeRTOS and FreeBSD on non-qemu, this just times-out.