# Buffer Errors #

This vulnerability allows inappropriate read and/or write access to locations within memory associated with variables, data structures or internal program data.
Inappropriate access to memory is exploited to subvert the normal hardware operations creating security vulnerability in the hardware.

## BOF (Buffer Overflow Bugs) ##
The software accesses through an array a memory location that is outside the boundaries of that array \[[more](https://samate.nist.gov/BF/Classes/BOF.html)\].

Memory access errors are some of the most common software flaws.
When exploitable, they can result in information exposure or loss,
arbitrary code execution, or various forms of capability denial.

## Scoring Approach ##

Each test attempts to show the existence of a buffer error *weakness*, i.e. a _potential_ vulnerability. 
Hence, if a test runs to completion, we count the test as witnessing the weakness.
Each CWE is assigned a score from NONE to V-HIGH as the fraction of detected errors (e.g., traps) decreases.
The rationale for this is that the MMU on commodity-off-the-shelf systems will typically detect _some_
buffer errors, and should be treated as a baseline.

### Buffer overflow generator

This prototype demonstrates a method of factored test generation
applied to the the **BOF** fault class.
It is designed to produce valid randomized C99 programs which contain
concrete instances of the abstract BOF model.
Future versions will implement automatic configuration of factors,
and may extend to other BF fault classes.

Although the generated programs should compile under recent versions
of GCC and Clang, they are expected (and intended) to cause runtime errors,
the nature of which may be specific to their execution environment.
The programs are self-contained and do not require standard library functions
or system calls. However, they may be configured to use `printf()`
for output, with `write()` and other syscalls either provided by `stdio`
or another source.


## Dependencies

The current implementation consists of a Python 3 program divided into
several modules. The Python program does not depend on any
packages outside the standard library,
but makes heavy use of [*f-strings*](https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep498)
and thus requires Python version 3.6 or later.
