# Numeric Errors #

These vulnerabilities stem from exploitation of improper numeric calculation or conversion.

---

## Overall Test Approach ##

This group of tests provoke or exploit C language `undefined behavior` such as uninitialized variables and pointers, calling functions with the wrong number of parameters, and so on. As such, the behavior of a program is difficult to predict, and may result in the program being aborted via a OS signal (e.g., on Debian) or a CPU exception (on a SSITH CPU running FreeRTOS, for example).

Several tests here are "multi-part" in that they run several test cases which are (logically) grouped according to a single CWE and a single program binary. To ensure that all parts get a chance to run, even in the face of an earlier part being aborted by the OS or CPU, these tests use the test harness's support for "multi-part" tests on both FreeRTOS and POSIX platforms.

* On FreeRTOS, each test that has more than one part includes `testsParameters.h` and defines a C macro `NUM_OF_TEST_PARTS` to define the number of times that each test is to be run. The implementation of the `main()` function for FreeRTOS then tests the preprocessor macro `BESSPIN_TEST_PART` to see which part of the test to run on each invocation.

* On Unix platforms, the test is run the right number of times from the Shell, passing the test part to be run as the first (and only) command-line argument of the test. This is picked up in the Unix version of `main()` using C's standard `argv[]` processing.

See [test_456.c](./sources/test_456.c) for an example.

---

## Scoring Approach ##

In the face of undefined behavior and possibly aborts, it is difficult to write test code that reliably produces predictable output. To this end, the scoring code recognizes both test-generated output and output from OS or CPU-level intervention. The following table shows the particular string that is matched in each test's log file and its score:

|Matching String or Signal   |Score|
|------------------|-------------|
|TEST FAILED       |HIGH       |
|TOP SECRET STUFF  |HIGH       |
|SEGFAULT          |HIGH         |
|TEST PASSED       |NONE         |
|TEST ERROR        |CALL-ERR     |

For more details about the scoring approach, please refer to [the Besspin philosophy document](../../../docs/cwesEvaluation/besspinPhilosophy.md).

---

## INI (Initialization) Group ##

### TEST-456 ###
Missing Initialization of Variable \[[CWE-456](https://cwe.mitre.org/data/definitions/456.html)\].

**Test Parts:**
- p01: function reads and returns the value of an uninitialized variable, which is subsequently used to index an array legally. Successfully printing a value from the array is treated as `TEST FAILED` since the reference to the uninitialized variable should not be permitted.

- p02: function reads and returns the value of an uninitialized variable, which is subsequently used to index an array out-of-bounds. Scored as per p01.

- p03: function reads and returns the value of an uninitialized variable, which leaks sensitive information from another unrelated computation to an output device. Leaking information is scored as `TEST FAILED`.


### TEST-457 ###
Use of Uninitialized Variable \[[CWE-457](https://cwe.mitre.org/data/definitions/457.html)\].

**Test Parts:**
- p01: function reads and returns the value of an uninitialized variable, which is subsequently used in a division. Returned value is non-zero, so division succeeds in this case. Nevertheless, any successful reference to the uninitialized variable is scored as `TEST FAILED`.

- p02: function reads and returns the value of an uninitialized variable, which is subsequently used in a division. Returned value is zero, so program crashes and/or exhibits a potential denial-of-service. Scored as p01. Technical note: RISC-V CPUs do NOT trap on division by zero.

### TEST-665 ###
Improper Initialization \[[CWE-665](https://cwe.mitre.org/data/definitions/665.html)\].

**Notes:**
These cases are derived from the example code given in the MITRE CWE site.

**Test Parts:**
- p01: function allocates a local (automatic) string (array of char) but leaves it uninitialized. A subsequent call to strcat() produces an undefined behavior. Subsequent successful reference to the string is scored as `TEST FAILED`.

- p02: As p01, but the first string is allocated by "malloc()" off the heap and accessed via a pointer. Scored as p01.

### TEST-824 ###
Access of Uninitialized Pointer \[[CWE-824](https://cwe.mitre.org/data/definitions/824.html)\].

**Test Parts:**
- p01: A function prints a string to stdout, but the pointer to the string is a local, uninitialized variable. In this test, the undefined value of the pointer is contrived to point at secret data. Successul dereference of the uninitialized pointers is scored as `TEST FAILED`.

- p02: A function calls another function via a pointer which is uninitialized. This test arranges the undefined value of the function pointer to point to a function that leaks secret information to stdout. Scored as p01.

---

## ARG (Arguments) Group ##

## TEST-234 ###
Failure to Handle Missing Parameter \[[CWE-234](https://cwe.mitre.org/data/definitions/234.html)\].

**Notes:**
The MITRE website shows 2 examples of this problem in C. The first shows a simple case of calling a function with the wrong number of parameters. This is legal in K&R C, but has been illegal in C90 onwards, so this case has not been implemented here, since it is rejected by both GCC and clang.

**Test Parts:**
- p01: A `varargs` function is declared that expects exactly four arguments. It is then called with just 3 arguments, returning an undefined result. This code is adapted from the second example on the CWE page linked above. If the result of the function is successfully printed, then this is scored as `TEST FAILED`.

---

## FRS (Faulty Result) Group ##

This group relates to defects where software *produces a faulty result due to conversions between primitive types, range violations, or domain violations.* Please see the \[[NIST BF FRS group page](https://samate.nist.gov/BF/Classes/FRS.html)\] for more details.

### TEST-128 ###
Wrap-around Error \[[CWE-128](https://cwe.mitre.org/data/definitions/128.html)\].

**Notes:**
This test has been inspired by the description of rule MEM07-C of the [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/MEM07-C.+Ensure+that+the+arguments+to+calloc%28%29%2C+when+multiplied%2C+do+not+wrap).

These defects relate to the fact that "unsigned" types (such as size_t) in C exhibit "modulo N" (or "wrap-around") arithmetic on overflow. This is well-defined behavior in C, but can lead to a class of defect if the possibility of wrap-around is not explicitly defended.

A particular problem occurs when a multiplication operator is applied to compute a number of bytes to pass to a subsequent call to a memory-allocation function such a `malloc()`. An unintentional wrap-around can lead to a small number of bytes being allocated (when a large number was expected), or a request to allocate zero bytes.

**Test Parts:**
- p01: This test illustrates this defect by incorrectly scaling a request for memory allocation so that the number of bytes requested is zero, owing to a wrap-around in the multiplication.  Subsequent writes to the (un)allocated memory are undefined behavior, and could lead to buffer overflow, code injection, or many other vulnerabilities. A SSITH platform could mitigate this problem in several ways, for instance:
  - Prevent the wrap-around in the unsigned multiplication operator.
  - Prevent the attempt to `malloc(0)` bytes.
  - Prevent use of the pointer returned from the call to `malloc(0)`
- p02: Identical to p01, but computes the allocation size using a `uint8_t` rather than a `size_t`, and allocates buffers of type `uint16_t` rather than `int`.

### TEST-190 ###
Integer Overflow \[[CWE-190](https://cwe.mitre.org/data/definitions/190.html)\].

**Test Parts:**
- p01: This test illustrates the undefined behavior on overflow of signed integer addition in C. The code attempts to declare a function `arithmetic_mean()` that returns the average of its two arguments, assuming each argument is an `int` greater than zero. The function also promises to return a result which is greater than zero, since this is a reasonable expectation given positive arguments.  Unfortunately, the addition of the two arguments can overflow, which might lead to a negative result for "large" (i.e. near INT_MAX) arguments. This test is deemed to FAIL if a call to `arithmetic_mean()` returns a negative result and the overflow is not detected by the platform or CPU.

### TEST-191 ###
Integer Underflow \[[CWE-191](https://cwe.mitre.org/data/definitions/191.html)\].

**Test Parts:**
- p01: This test illustrates a vulnerability that results from underflow of an unsigned integer subtraction, inspired by the CVE entry cited above. The CVE cites an example of code that parses the structure of a data "packet" that includes a "length" field which is of an unsigned integer type. The code performs a subtraction operation on that length which (on underflow) can result in a very large number if the length field is incorrect. The code then loops over the data field of the packet, printing each byte of data from index 0 to the calculated length. An incorrect length field can therefore result in printing too much data (which might be some secret information) or a buffer overflow.

### TEST-192 ###
Integer Coercion \[[CWE-192](https://cwe.mitre.org/data/definitions/192.html)\].

**Test Parts:**
- p01: This test illustrates a vulnerability that results from "coercion" of integer types in C. The test code has been adapted from "Example 2" given on the CWE-192 page cited above. In this case, we see a positive 32-bit signed integer with value `65535` (`0x0000FFFF`) implicitly converted onto a 16-bit signed integer with value -1. This value is later interpreted as the length of a string buffer, and passed to strncpy() where it converted (again) to a very large unsigned value, leading to multiple vulnerabilities, including buffer overdlow and information leakage

### TEST-194 ###
Unexpected Sign Extension \[[CWE-194](https://cwe.mitre.org/data/definitions/194.html)\].

**Test Parts:**
- p01: This test illustrates a vulnerability that results from unexpected "sign extension" of integer types in C when a signed value is (implicitly) converted into a "wider" (e.g. more bits) integer type. This test case is adapted from the example given [here](https://docs.oracle.com/cd/E19205-01/819-5265/bjamz/index.html).

### TEST-195 ###
Signed to Unsigned Conversion Error \[[CWE-195](https://cwe.mitre.org/data/definitions/195.html)\].

**Test Parts:**
- p01: This test illustrates a vulnerability that results from an implicit conversion from a small signed integer type to a wider unsigned type. This test case has been adapted from "Example 4" on the NIST CWE site at the link given above. Specifically, this test uses a data packet structure, the first two bytes of which are a signed 16-bit integer that gives the length of the remaining data in bytes. The test reads this length field, and passes it to "memcpy()" to copy the data to a buffer. Unfortunately, the signed integer length is implicitly converted to "size_t" in the call to memcpy() which can result in unexpected or undefined behavior if the original length field is negative.

### TEST-196 ###
Signed to Unsigned Conversion Error \[[CWE-196](https://cwe.mitre.org/data/definitions/196.html)\].

**Test Parts:**
- p01: This test illustrates a vulnerability that results from an implicit conversion from unsigned to signed integer. In particular, this case illustrates how an unsigned value can be converted to a signed integer and then used as an offset into an array. If a large unsigned value is converted, this can result in a negative offset into the array object and subsequent undefined behavior. The test case exploits this behaviour to print the value of a sensitive string.

### TEST-197 ###
Numeric Truncation Error \[[CWE-197](https://cwe.mitre.org/data/definitions/197.html)\].

**Test Parts:**
- p01: This test illustrates a vulnerability that results from trunction from a wider (e.g. 32-bit) to a narrower (e.g. 16-bit) integer type. In such cases, C truncates the representation which may result in an unexpected value or change of sign.  This case illustrates how this can happen in converting the signed INT_MAX value into the standard int16_t type. On most implementations, this results in the value -1. The test goes on to use this value as an index into an array, which offers a second chance for a SSITH platform to detect and mitigate the problem.

### TEST-681 ###
Incorrect Conversion Between Numeric Types \[[CWE-681](https://cwe.mitre.org/data/definitions/681.html)\].

**Related CWEs**
- [CWE-192](https://cwe.mitre.org/data/definitions/192.html).
- [CWE-194](https://cwe.mitre.org/data/definitions/194.html).
- [CWE-195](https://cwe.mitre.org/data/definitions/195.html).
- [CWE-196](https://cwe.mitre.org/data/definitions/196.html).
- [CWE-197](https://cwe.mitre.org/data/definitions/197.html).

**Notes:**
This CWE is rather general, covering any "incorrect conversion" between numeric types. It is actually the parent of CWEs 192, 194, 195, 196, and 197 in the CWE hierarchy. These CWEs cover more specific cases of numeric conversion errors, and are dealt with above. As such, no specific test case has been designed for CWE 681, but rather the worst score of these tests will be the score of CWE-681.


### TEST-369 ###
Division by Zero \[[CWE-369](https://cwe.mitre.org/data/definitions/369.html)\].


**Notes:**
This CWE covers a very specific programming defect - division by zero. On _most_ CPUs, division by zero triggers some sort of CPU trap or exception which may either terminate the program, or be passed to some sort of software-defined exception handler.

RISC-V is unusual, though. It does _not_ trap on division by zero, but returns a well-defined (but normally non-sensical value) of "all one bits" (RISC-V ISA specification section 7.2).

In this case, then we do not expect an unmodified RISC-V to detect division by zero, but a SSITH CPU might do so and signal the problem to the test environment.

**Test Parts:**
- p01: This test loops over some data, computing a divisor each time, and doing so dynamically to avoid premature optimization of the code. At the fifth iteration of the main loop, a division by zero occurs. If this goes unnoticed by the CPU or operating system, then this is considered a FAIL.

---
