# Numeric Errors #

These vulnerabilities stem from exploitation of improper numeric calculation or conversion.

This directory has all the tests to evaluate numeric vulnerabilities. The [testgen progress spreadsheet](https://docs.google.com/spreadsheets/d/1CNLjQN4VRd9_hAgm4UTgeuvEYDbKerKS5G_X0KlsMgA/edit?usp=sharing) logs the progress of which tests are implemented on which OS, and which system calls/modules should be supported.

## Overall Test Approach ##

This group of tests provoke or exploit C language `undefined behavior` such as uninitialized variables and pointers, calling functions with the wrong number of parameters, and so on. As such, the behavior of a program is difficult to predict, and may result in the program being aborted via a OS signal (e.g., on Debian) or a CPU exception (on a SSITH CPU running FreeRTOS, for example).

Several tests here are "multi-part" in that they run several test cases which are (logically) grouped according to a single CWE and a single program binary. To ensure that all parts get a chance to run, even in the face of an earlier part being aborted by the OS or CPU, these tests use the test harness's support for "multi-part" tests on both FreeRTOS and POSIX platforms.

* On FreeRTOS, each test that has more than one part includes `testsParameters.h` and defines a C macro `NUM_OF_TEST_PARTS` to define the number of times that each test is to be run. The implementation of the `main()` function for FreeRTOS then tests the preprocessor macro `TESTGEN_TEST_PART` to see which part of the test to run on each invocation.

* On Debian (and other POSIX-like platforms), a custom script (in `scripts/vulClassTester.py`) maps the test name to its number of parts, then runs the test the right number of times from the Shell, passing the test part to be run as the first (and only) command-line argument of the test. This is picked up in the Debian version of `main()` using C's standard `argv[]` processing.

See `sources/test_456.c` for an example.

## Scoring Approach ##

In the face of undefined behavior and possibly aborts, it is difficult to write test code that reliably produces predictable output. To this end, the scoring code recognizes both test-generated output and output from OS or CPU-level intervention. The following table shows the particular string that is matched in each test's log file and its score:

|Matching String   |Score|
|------------------|-------------|
|TEST FAILED       |HIGH       |
|TOP SECRET STUFF  |HIGH       |
|SEGFAULT          |HIGH         |
|Segmentation Fault|HIGH         |
|TEST PASSED       |NONE         |
|\<ABORT\>         |NONE         |
|TEST ERROR        |CALL-ERR     |

Notes:

* We expect that SSITH CPUs to *react* upon detecting a security vulnerability, but there is clearly no standard way to detect or handle those in C at present. Consequently, we score based on the detection of said *reaction*. For the numeric errors tests, the default scoring mechanism is to score `NONE`, meaning that the CPU has successfully prevented a vulnerability, when it detects the string `<ABORT>` on the standard output channel; this can be configured to other different types of reactions as detailed in the main testgen [README](README.md).

* If a test produces no output at all that matches any of the strings above, then it is scored -2 meaning "TEST FAIL".


------------------

## INI (Initialization) Group ##

### TEST-456 ###
Missing Initialization of Variable \[[CWE-456](https://cwe.mitre.org/data/definitions/456.html)\].

**Related CWEs**
- [CWE-456](https://cwe.mitre.org/data/definitions/456.html).

**Notes:**
- None.

**Test Parts:**
- p01: function reads and returns the value of an uninitialized variable, which is subsequently used to index an array legally. Successfully printing a value from the array is treated as "TEST FAILED" since the reference to the uninitialized variable should not be permitted.

- p02: function reads and returns the value of an uninitialized variable, which is subsequently used to index an array out-of-bounds. Scored as per p01.

- p03: function reads and returns the value of an uninitialized variable, which leaks sensitive information from another unrelated computation to an output device. Leaking information is scored as "TEST FAILED".

**Possible Extensions:**
- Consider other possible undefined behaviors that might result in a security policy violation.



### TEST-457 ###
Use of Uninitialized Variable \[[CWE-457](https://cwe.mitre.org/data/definitions/457.html)\].

**Related CWEs**
- [CWE-457](https://cwe.mitre.org/data/definitions/457.html).

**Notes:**
- None.

**Test Parts:**
- p01: function reads and returns the value of an uninitialized variable, which is subsequently used in a division. Returned value is non-zero, so division succeeds in this case. Nevertheless, any successful reference to the uninitialized variable is scored as "TEST FAILED".

- p02: function reads and returns the value of an uninitialized variable, which is subsequently used in a division. Returned value is zero, so program crashes and/or exhibits a potential denial-of-service. Scored as p01. Technical note: RISC-V CPUs do NOT trap on division by zero.

**Possible Extensions:**
- Consider other possible undefined behaviors that might result in a security policy violation.

### TEST-665 ###
Improper Initialization \[[CWE-665](https://cwe.mitre.org/data/definitions/665.html)\].

**Related CWEs**
- [CWE-665](https://cwe.mitre.org/data/definitions/665.html).

**Notes:**
These cases are derived from the example code given in the MITRE CWE site.

**Test Parts:**
- p01: function allocates a local (automatic) string (array of char) but leaves it uninitialized. A subsequent call to strcat() produces an undefined behavior. Subsequent successful reference to the string is scored as "TEST FAILED".

- p02: As p01, but the first string is allocated by "malloc()" off the heap and accessed via a pointer. Scored as p01.

### TEST-824 ###
Access of Uninitialized Pointer \[[CWE-824](https://cwe.mitre.org/data/definitions/824.html)\].

**Related CWEs**
- [CWE-824](https://cwe.mitre.org/data/definitions/824.html).

**Notes:**
None

**Test Parts:**
- p01: A function prints a string to stdout, but the pointer to the string is a local, uninitialized variable. In this test, the undefined value of the pointer is contrived to point at secret data. Successul dereference of the uninitialized pointers is scored as "TEST FAILED".

- p02: A function calls another function via a pointer which is uninitialized. This test arranges the undefined value of the function pointer to point to a function that leaks secret information to stdout. Scored as p01.

### TEST-908 ###
Use of uninitialized Resource \[[CWE-908](https://cwe.mitre.org/data/definitions/908.html)\].

**Related CWEs**
- [CWE-908](https://cwe.mitre.org/data/definitions/908.html).

This CWE appears to be an almost-verbatim copy of CWE-665. In particular, the example code for this CWE shown on the MITRE site is identical to that shown for CWE-665.

As such, no explicit test for CWE-908 has been added.

### TEST-909 ###
Missing Initialization of Resource \[[CWE-909](https://cwe.mitre.org/data/definitions/909.html)\].

**Related CWEs**
- [CWE-909](https://cwe.mitre.org/data/definitions/909.html).

This CWE appears to be an almost-verbatim copy of CWEs 456 and 665. In particular, the example C code for this CWE shown on the MITRE site is identical to that shown for CWE-665.

As such, no explicit test for CWE-909 has been added.

------------------

## ARG (Arguments) Group ##

### CWE-227 ###
API Abuse \[[more](https://cwe.mitre.org/data/definitions/227.html)\].

This CWE is a category. As such, no specific test case has been constructed.

## TEST-234 ###
Failure to Handle Missing Parameter \[[CWE-234](https://cwe.mitre.org/data/definitions/234.html)\].

**Related CWEs**
- [CWE-234](https://cwe.mitre.org/data/definitions/234.html).

**Notes:**
The CWE website shows 2 examples of this problem in C. The first shows a simple case of calling a function with the wrong number of parameters. This is legal in K&R C, but has been illegal in C90 onwards, so this case has not been implemented here, since it is rejected by both GCC and clang.

**Test Parts:**
- p01: A "varargs" function is declared that expects exactly four arguments. It is then calls with just 3 arguments, returning an undefined result. This code is adapted from the second example on the CWE page linked above. If the result of the function is successfully printed, then this is scored as "TEST FAILED".

### TEST-559 ###
Often Misused: Arguments and Parameters \[[CWE-559](https://cwe.mitre.org/data/definitions/559.html)\].

**Related CWEs**
- [CWE-559](https://cwe.mitre.org/data/definitions/559.html).

This CWE is a category. As such, no specific test case has been constructed.

### TEST-560 ###
Use of umask() with chmod-style Argument \[[CWE-560](https://cwe.mitre.org/data/definitions/560.html)\].

**Related CWEs**
- [CWE-560](https://cwe.mitre.org/data/definitions/560.html).

This CWE relates to mis-understanding of the arguments to the umask() POSIX system call. As such, it is completely unrelated to the C language (or any other language for that matter), or the underlying CPU architecture, so we consider it out-of-scope for SSITH at this time.  We also note that FreeRTOS has no umask() API at all, so no test case for this CWE has been designed at this point.

### TEST-628 ###
Function Call with Incorrectly Specified Arguments \[[CWE-628](https://cwe.mitre.org/data/definitions/628.html)\].

**Related CWEs**
- [CWE-628](https://cwe.mitre.org/data/definitions/628.html).

This CWE is remarkably general - relating to calling a function "with arguments that are not correctly specified, leading to always-incorrect behavior and resultant weaknesses." The C language is rich in such possibilities, and this CWE could affect potentially any function call or predefined library or API in an entire application.

Therefore, attempting to produce a small number of test cases for this CWE seems rather fatuous. The same problem affects other languages, although some to a lesser extent through stronger type checking and rules. This CWE also has little to do with the CPU/architectural issues that SSITH is hoping to address.

See the more specific CWEs on this topic (e.g. CWE 683 - 688) for particular test cases.

### TEST-683 ###
Function Call with Incorrect Order of Arguments \[[CWE-683](https://cwe.mitre.org/data/definitions/683.html)\].

**Related CWEs**
- [CWE-683](https://cwe.mitre.org/data/definitions/683.html).

This CWE considers a function call with 2 or more arguments of the same type, but where the caller specifies the arguments in the wrong order. This particularly affects C, which has structural type equivalence and positional association of actual and formal parameters.

This could affect almost any function fitting the above description. The CWE notes the most common cause is a programmer's "cut and paste" error or similar mistake.

One CVE has been found \[[CVE-2014-3956](https://nvd.nist.gov/vuln/detail/CVE-2014-3956)\] where in incorrect order of arguments in a call in the "sendmail" application resulted in users having access to files unexpectedly.

The security impact of any such defect is highly dependent on the application itself and the meaning of the mis-used function.

Potential mitigation for this CWE include:
1. Use of extended static analysis for languages with weak type-checking.
2. Use of a language with stronger type checking and/or named association of parameters.
3. Use of contracts (e.g. pre-conditions) to enforce correctness properties of actual parameters.

but it is difficult to imagine how hardware could detect such issues within the current scope of the SSITH project. As such, no specific test case has been constructed at this time.

### TEST-685 ###
Function Call with Incorrect Number of Parameters \[[CWE-685](https://cwe.mitre.org/data/definitions/685.html)\].

**Related CWEs**
- [CWE-685](https://cwe.mitre.org/data/definitions/685.html).

This CWE most notably affects C when "varargs" functions are used, such as printf(). As such, this is a repetition of CWE-234 above, so no additional test case has been added.

### TEST-686 ###
Function Call with Incorrect Argument Type \[[CWE-686](https://cwe.mitre.org/data/definitions/686.html)\].

**Related CWEs**
- [CWE-686](https://cwe.mitre.org/data/definitions/686.html).

**Notes:**
This test subverts C's type model by assigning a pointer to the library function strchr() to another pointer-to-function that has the wrong number and types of its arguments.  This test has been adapted from the example shown in the SEI's CERT C Coding Standard \[[Rule EXP37-C](https://wiki.sei.cmu.edu/confluence/display/c/EXP37-C.+Call+functions+with+the+correct+number+and+type+of+arguments)\].

**Test Parts:**
- p01: As above - calling function via incorrectly typed pointer. If program control flow passes to the statement following the bad call, then this is scored "TEST FAILED".

### TEST-687 ###
Function Call with Incorrectly Specified Argument Value \[[CWE-687](https://cwe.mitre.org/data/definitions/687.html)\].

**Related CWEs**
- [CWE-687](https://cwe.mitre.org/data/definitions/687.html).

This CWE is very general - potentially covered any function call with "the wrong value" passed as an argument.  This could be true of any non-total function in any program or library.

The CWE description does refer to one particularly dangerous example in C - calling malloc() with a ZERO value as the argument, which is an Unspecified Behavior.  The returned pointer might be NULL, or might point to an area of memory that should not be accessed.

This test case illustrates that particular problem, since it is both relevant and potentially mitigated by SSITH CPUs.  See \[[Rule MEM04-C](https://wiki.sei.cmu.edu/confluence/display/c/MEM04-C.+Beware+of+zero-length+allocations)\] for more details.

**Test Parts:**
- p01: As described above - calling malloc() with a ZERO as argument. A successful attempt to subsequently dereference that pointer is scored as "TEST FAILED".

### TEST-688 ###
Function Call with Incorrect Variable or Reference as Argument \[[CWE-688](https://cwe.mitre.org/data/definitions/688.html)\].

**Related CWEs**
- [CWE-688](https://cwe.mitre.org/data/definitions/688.html).

This CWE is very general - potentially covered any function call with "the wrong variable" or "pointer to the wrong variable" passed as an argument.  This could be true of any function in any program or library.

It is imaginable that such an error could lead to a buffer overflow, NULL dereference, or similar, but those error cases are covered under other CWE identifiers.  As such, no test case for this CWE has been designed at this time.

------------------

## FRS (Faulty Result) Group ##

This group related to defects where software "produces a faulty result due to conversions between primitive types, range violations, or domain violations." \[[NIST BF FRS Group Page](https://samate.nist.gov/BF/Classes/FRS.html)\]

### TEST-128 ###
Wrap-around Error \[[CWE-128](https://cwe.mitre.org/data/definitions/128.html)\].

**Related CWEs**
- [CWE-128](https://cwe.mitre.org/data/definitions/128.html).

**Notes:**
This test has been inspired by the description of rule MEM07-C of the [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/MEM07-C.+Ensure+that+the+arguments+to+calloc%28%29%2C+when+multiplied%2C+do+not+wrap).

These defects relate to the fact that "unsigned" types (such as size_t) in C exhibit "modulo N" (or "wrap-around") arithmetic on overflow. This is well-defined behavior in C, but can lead to a class of defect if the possibility of wrap-around is not explicitly defended.

A particular problem occurs when a multiplication operator is applied to compute a number of bytes to pass to a subsequent call to a memory-allocation function such a `malloc()`. An unintentional wrap-around can lead to a small number of bytes being allocated (when a large number was expected), or a request to allocate zero bytes.

**Test Parts:**
- p01: This test illustrates this defect by incorrectly scaling a request for memory allocation so that the number of bytes requested is zero, owing to a wrap-around in the multiplication.  Subsequent writes to the (un)allocated memory are undefined behavior, and could lead to buffer overflow, code injection, or many other vulnerabilities. A SSITH platform could mitigate this problem in several ways, for instance:
  - Prevent the wrap-around in the unsigned multiplication operator.
  - Prevent the attempt to `malloc(0)` bytes.
  - Prevent use of the pointer returned from the call to `malloc(0)`

### TEST-190 ###
Integer Overflow \[[CWE-190](https://cwe.mitre.org/data/definitions/190.html)\].

**Related CWEs**
- [CWE-190](https://cwe.mitre.org/data/definitions/190.html).

**Notes:**
None

**Test Parts:**
- p01: This test illustrates the undefined behavior on overflow of signed integer addition in C. The code attempts to declare a function `arithmetic_mean()` that returns the average of its two arguments, assuming each argument is an `int` greater than zero. The function also promises to return a result which is greater than zero, since this is a reasonable expectation given positive arguments.  Unfortunately, the addition of the two arguments can overflow, which might lead to a negative result for "large" (i.e. near INT_MAX) arguments. This test is deemed to FAIL if a call to `arithmetic_mean()` returns a negative result and the overflow is not detected by the platform or CPU.

### TEST-191 ###
Integer Underflow \[[CWE-191](https://cwe.mitre.org/data/definitions/191.html)\].

**Related CWEs**
- [CWE-191](https://cwe.mitre.org/data/definitions/191.html).

**Related CVEs**
- [CVE-2004-1002](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2004-1002).

**Notes:**
None

**Test Parts:**
- p01: This test illustrates a vulnerability that results from underflow of an unsigned integer subtraction, inspired by the CVE entry cited above. The CVE cites an example of code that parses the structure of a data "packet" that includes a "length" field which is of an unsigned integer type. The code performs a subtraction operation on that length which (on underflow) can result in a very large number if the length field is incorrect. The code then loops over the data field of the packet, printing each byte of data from index 0 to the calculated length. An incorrect length field can therefore result in printing too much data (which might be some secret information) or a buffer overflow.

### TEST-192 ###
Integer Coercion \[[CWE-192](https://cwe.mitre.org/data/definitions/192.html)\].

**Related CWEs**
- [CWE-192](https://cwe.mitre.org/data/definitions/192.html).

**Notes:**
None

**Test Parts:**
- p01: This test illustrates a vulnerability that results from "coercion" of integer types in C. The test code has been adapted from "Example 2" given on the CWE-192 page cited above. In this case, we see a positive 32-bit signed integer with value 65535 (0x0000FFFF) implicitly converted onto a 16-bit signed integer with value -1. This value is later interpreted as the length of a string buffer, and passed to strncpy() where it converted (again) to a very large unsigned value, leading to multiple vulnerabilities, including buffer overdlow and information leakage

### TEST-194 ###
Unexpected Sign Extension \[[CWE-194](https://cwe.mitre.org/data/definitions/194.html)\].

**Related CWEs**
- [CWE-194](https://cwe.mitre.org/data/definitions/194.html).

**Notes:**
None

**Test Parts:**
- p01: This test illustrates a vulnerability that results from unexpected "sign extension" of integer types in C when a signed value is (implicitly) converted into a "wider" (e.g. more bits) integer type. This test case is adapted from the example given [here](https://docs.oracle.com/cd/E19205-01/819-5265/bjamz/index.html).

### TEST-195 ###
Signed to Unsigned Conversion Error \[[CWE-195](https://cwe.mitre.org/data/definitions/195.html)\].

**Related CWEs**
- [CWE-195](https://cwe.mitre.org/data/definitions/195.html).

**Notes:**
None

**Test Parts:**
- p01: This test illustrates a vulnerability that results from an implicit conversion from a small signed integer type to a wider unsigned type. This test case has been adapted from "Example 4" on the NIST CWE site at the link given above. Specifically, this test uses a data packet structure, the first two bytes of which are a signed 16-bit integer that gives the length of the remaining data in bytes. The test reads this length field, and passes it to "memcpy()" to copy the data to a buffer. Unfortunately, the signed integer length is implicitly converted to "size_t" in the call to memcpy() which can result in unexpected or undefined behavior if the original length field is negative.

### TEST-196 ###
Signed to Unsigned Conversion Error \[[CWE-196](https://cwe.mitre.org/data/definitions/196.html)\].

**Related CWEs**
- [CWE-196](https://cwe.mitre.org/data/definitions/196.html).

**Notes:**
None

**Test Parts:**
- p01: This test illustrates a vulnerability that results from an implicit conversion from unsigned to signed integer. In particular, this case illustrates how an unsigned value can be converted to a signed integer and then used as an offset into an array. If a large unsigned value is converted, this can result in a negative offset into the array object and subsequent undefined behavior. The test case exploits this behaviour to print the value of a sensitive string.

### TEST-197 ###
Numeric Truncation Error \[[CWE-197](https://cwe.mitre.org/data/definitions/197.html)\].

**Related CWEs**
- [CWE-197](https://cwe.mitre.org/data/definitions/197.html).
- [CWE-192](https://cwe.mitre.org/data/definitions/192.html).

**Notes:**
None

**Test Parts:**
- p01: This test illustrates a vulnerability that results from trunction from a wider (e.g. 32-bit) to a narrower (e.g. 16-bit) integer type. In such cases, C truncates the representation which may result in an unexpected value or change of sign.  This case illustrates how this can happen in converting the signed INT_MAX value into the standard int16_t type. On most implementations, this results in the value -1. The test goes on to use this value as an index into an array, which offers a second chance for a SSITH platform to detect and mitigate the problem.

### TEST-681 ###
Incorrect Conversion Between Numeric Types \[[CWE-681](https://cwe.mitre.org/data/definitions/681.html)\].

**Related CWEs**
- [CWE-192](https://cwe.mitre.org/data/definitions/192.html).
- [CWE-194](https://cwe.mitre.org/data/definitions/194.html).
- [CWE-195](https://cwe.mitre.org/data/definitions/195.html).
- [CWE-196](https://cwe.mitre.org/data/definitions/196.html).

**Notes:**
This CWE is rather general, covering any "incorrect conversion" between numeric types. It is actually the parent of CWEs 192, 194, 195 and 196 in the CWE hierarchy. These CWEs cover more specific cases of numeric conversion errors, and are dealt with above. As such, no specific test case has been designed for CWE 681.

### TEST-682 ###
Incorrect Calculation \[[CWE-682](https://cwe.mitre.org/data/definitions/682.html)\].

**Related CWEs**
- [CWE-128](https://cwe.mitre.org/data/definitions/128.html).
- [CWE-190](https://cwe.mitre.org/data/definitions/190.html).
- [CWE-191](https://cwe.mitre.org/data/definitions/191.html).
- [CWE-192](https://cwe.mitre.org/data/definitions/192.html).
- [CWE-369](https://cwe.mitre.org/data/definitions/369.html).

**Notes:**
This CWE is rather general, covering any "incorrect calculation" the result of which is "later used in security-critical decisions or resource management." It is actually a parent of CWEs 128, 190, 191, 192, and 369 in the CWE hierarchy. These CWEs cover more specific cases of numeric calculation errors, and are dealt with above. As such, no specific test case has been designed for CWE 682.

### TEST-704 ###
Incorrect Type Conversion or Cast \[[CWE-704](https://cwe.mitre.org/data/definitions/704.html)\].

**Related CWEs**
- [CWE-681](https://cwe.mitre.org/data/definitions/681.html).
- [CWE-588](https://cwe.mitre.org/data/definitions/588.html).

**Notes:**
This CWE is rather general, covering any "incorrect conversion or cast", many of which are covered by its child CWEs 681 and others covered above.

One specific case does yield an interesting test case, though, arising from its child CWE 588. This case covers an attempted conversion from a "pointer-to-function" to a "pointer-to-data" and then an attempt to write to the data at the resulting pointer location - a possible route for code injection and other related vulnerabilities. Some operating systems prevent this kind of attach by making program instructions "read only" or "execute only", but bare-metal or small systems like FreeRTOS may not do this, making this an interesting test case.

**Test Parts:**
- p01: This test converts a function pointer into a pointer to a "struct" data object, then attempts to write to the data referenced by the resulting pointer. The result is undefined behavior or a program crash on some systems. A SSITH platform might pass the test by preventing the initial cast operation, or by preventing the subsequent assignment via the pointer value.

### TEST-369 ###
Division by Zero \[[CWE-369](https://cwe.mitre.org/data/definitions/369.html)\].

**Related CWEs**
None.

**Notes:**
This CWE covers a very specific programming defect - division by zero. On _most_ CPUs, division by zero triggers some sort of CPU trap or exception which may either terminate the program, or be passed to some sort of software-defined exception handler.

RISC-V is unusual, though. It does _not_ trap on division by zero, but returns a well-defined (but normally non-sensical value) of "all one bits" (RISC-V ISA specification section 7.2).

In this case, then we do not expect an unmodified RISC-V to detect division by zero, but a SSITH CPU might do so and signal the problem to the test environment.

**Test Parts:**
- p01: This test loops over some data, computing a divisor each time, and doing so dynamically to avoid premature optimization of the code. At the fifth iteration of the main loop, a division by zero occurs. If this goes unnoticed by the CPU or operating system, then this is considered a FAIL.

------------------

## WOP (Wrong Operation) Group ##

This group relates to defects where software "executed the wrong operation."

The NIST Bugs Framework site offers no further advice at the time of writing.

Two CWEs in this group (480 and 595) are parents of other CWEs, so are not of interest.

CWE 486 ("Comparison of Classes by Name") is only applicable to dynamic object-oriented languages such as Java or Python, so is out of scope for SSITH at this time.

The remaining CWEs in this group all concern defects that can be expressed as legal, well-defined C code that are known to be likely sources of vulnerabilities, but are not violations of the C language definition.  For example, CWE 481 concerns the use of the assignment instead of comparison operator in C, such as:

```
if (a = 0) {
 ...
}
```

While it is likely that the programmer meant to write:

```
if (a == 0) {
 ...
}
```

The former example does not violate any C language rule and thus it is difficult to imagine how a SSITH CPU/ISA could differentiate these cases _at runtime_.  A highly competent C programmer might argue that they really did mean to write the first form, but it does not seem reasonable for a SSITH CPU to pass judgement in that domain.

On the other hand, this defect is readily prevented by simple static analysis. Many coding standards explicitly prohibit such use of assignment - for example MISRA C 2012 Rule 13.4 - and static analysis tools will faithfully reject such cases.

The same observation applies to the remaining CWEs in the group (482, 597, 783, and 1024) - they are all adequately addressed by comtemporary language subsets, coding standards and static analysis tools, but it seems implausible that CPU/ISA-level runtime detection would add any value.

Therefore, at this time, we have noted that this group is best addressed by static analysis, and therefore out of scope for SSITH at this time.
