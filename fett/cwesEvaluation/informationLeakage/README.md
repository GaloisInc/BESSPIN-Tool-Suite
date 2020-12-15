# Information Leakage (also known as Information Exposure)

Information leakage is the exposure of parties to information which they are not
intended to see. Beyond leaking sensitive data, this can include revealing
information that enables subsequent attacks. Information can be leaked by
directly sending data to unauthorized parties, or through side or covert
channels that _indirectly_ allow parties to learn something about otherwise
secret data.

These weaknesses can be quite subtle. The
[description](https://samate.nist.gov/BF/Classes/IEXModel.html) on NIST's bugs
framework page is a useful starting point for learning more.

This directory has all the tests to evaluate information leakage vulnerabilities. The [testgen progress spreadsheet](https://docs.google.com/spreadsheets/d/1CNLjQN4VRd9_hAgm4UTgeuvEYDbKerKS5G_X0KlsMgA/edit?usp=sharing) logs the progress of which tests are implemented on which OS, and which system calls/modules should be supported.

## Test Methodology

The tests for this class are located [here](sources).

The sources in this directory define components of a generic application that
can be used to demonstrate IEX weaknesses. 

The application is a program that exposes two main capabilities:

1. The ability to store and retrieve data via a reliable naming scheme, i.e. addresses.
2. The ability to perform computations over stored data.

Already this suggests three components:

1. A module that interprets user requests into commands understood by the system;
2. A module that implements a data store;
3. A module that exposes and implements computations.

The IEX weaknesses described by the varous CWEs can be identified as weaknesses
in the above components. For example:

* CWE-203 describes leaky behavior discrepancies, as when a failed login attempt
  returns different messages to the user depending on if the username was
  incorrect or the password was incorrect (this simplifies brute-force attacks).
  This is a weakness in the third module above.
  
* CWE-707 describes weaknesses in interpreting user messages. For example, one
  exploitable weakness may be that the user can hijack program control by
  including specific control characters in a message, if the program does not
  sanitize the input before interpreting it. This can be realized both as a
  weakness in the interpreter (module 1), or the business logic (module 3).
  
* CWE-524 describes weaknesses due to incorrect cache implementations, which may
  be understood as weaknesses in the data store (module 2).
  
## Scoring Approach ##

Each test is scored by checking if the test driver is able to learn a secret value. If it is, then
the test is scored 'HIGH'; otherwise there is no weakness at the test is scored 'NONE'. 

Scores are grouped by CWE; the CWE score is the average of the related tests' scores.
  
## App (Test) Structure

The sources for the app live in the following directories:

- [sources/include](sources/include) all interfaces
- [sources/stores](sources/stores) implementations of data stores
- [sources/interpreters](sources/interpreters) implementations of user message interpreters
- [sources/functions](sources/functions) implementation of 1) a function lookup & dispatch table, 2) a source file for each exposed function. 
- [sources/tests](sources/tests) individual tests that witness a particular weakness
- [sources/control](sources/control) these are common routines

### Domains

To model different spheres or domains, an important concept that permeates the
design is a "domain": all data belongs to some domain. Domains are represented
by integers: a negative integer is a system domain (in general there is only one
such: -1), non-negative integers denote distinct non-system domains (the
motivation being a representation of different users).

It is thus a violation if data from -1 ever escapes to the calling process, or
(assuming the calling process is domain 0), if any data from domain != 0 escapes
to the calling process.

### Initial States
TBD

## Building a test instance

The `Makefile` sets a number of default choices for each components that can be
overriden on the command line. For example, to build an instance that witnesses
a weakness of an exploitable caching store, you can run: `make TEST=cache
STORE=cached weakness` which will produce an executable `cache`.

Hence:

```
$ make TEST=cache STORE=cached weakness
BUILDING TEST:
STORE=cached
INTERPRETER=simple_atoi
TEST=cache
clang -I include -DSTORE_SIZE=3 -DNDOMAINS=2 functions/search.c functions/sysconfig.c functions/login.c functions/basic.c functions/error.c stores/cached.c interpreters/simple_atoi.c control/control.c tests/cache.c -o cache

$ ./cache
TEST FAILED.
```

In this case, the witness only makes sense against a caching store. Thus:

```
$ make TEST=cache STORE=basic noweakness
BUILDING TEST:
STORE=basic
INTERPRETER=simple_atoi
TEST=cache
clang -DNO_WEAKNESS -I include -DSTORE_SIZE=3 -DNDOMAINS=2 functions/search.c functions/sysconfig.c functions/login.c functions/basic.c functions/error.c stores/basic.c interpreters/simple_atoi.c control/control.c tests/cache.c -o cache

$ ./cache
TEST PASSED.
```

However, the test is agnostic to the interpreter:

```
$ make TEST=cache STORE=cached INTERPRETER=simple_atoi weakness
BUILDING TEST:
STORE=cached
INTERPRETER=simple_atoi
TEST=cache
clang-I include -DSTORE_SIZE=3 -DNDOMAINS=2 functions/search.c functions/sysconfig.c functions/login.c functions/basic.c functions/error.c stores/cached.c interpreters/simple_atoi.c control/control.c tests/cache.c -o cache

$ ./cache
TEST FAILED.
```

## Adding a test
 TBD
 
## Implemented Components

### Stores

#### `basic.c`

Domain memory is a single allocated array of bytes.

#### `separate.c`

Each domain is a separately allocated region of memory.

#### `fragmented.c`

Domain memory is a single array of objects. Each object belongs to a domain,
objects belonging to different domains may occur at non-regular indices in the
array.

#### `cached.c` (CWE-524)

As `fragmented.c`, but the last object retrieved is cached. The weakness exposed
by this store is that the cached object is not cleared before being overwritten.

### Interpreters

#### `basic.c` (CWE-707)

The interpreter in `basic.c` interprets user addresses directly as system
addresses, but does not do any range checking on the values. This can allow
information exposure via buffer overruns.

#### `simple_atoi.c` (CWE-707)

The interpreter in `simple_atoi.c` interprets user addresses that are given as
ascii-encoded integers. However, the interpreter does not verify that each byte
is an ascii-encoded digit in the range `0` to `9`, which can lead to positive
and negative buffer overruns (or simply reading memory out of the _logical_
bound of an object if it lives in a common pool), and hence information
exposure.


### Functions

#### `broadcast` (CWE-212,226)

Copies a value from a domain to the public domain. When compiled with a
weakness, this function does not scrub the secret from the value.

#### `classify`

Adds a secret value to existing data.

#### `declassify` (CWE-212,226)

Returns a value that may contain sensitive information to the user. When
compiled with a weakness, this function does not scrub the secret from the
value.

#### `direct` (CWE-201,209)

This function retrieves a user-specified address as a wrapper around
the store interface. When compiled with a weakness, this function always
returns data from the privileged domain (domain `-1`).

#### `error` (CWE-201,209)

This function synthesizes a message using private data, when compiled with a
weakness (e.g. as in an error  message).

#### `login` (CWE-203)

This function simulates a login service. The user provides a username and
password, which are compared against the system's user and password values. When
compiled with a weakness, the function returns different results depending on
whether the username or the password checks failed (if they fail).

#### `mark_private`

Adds user-specified private data to a value.

#### `count`, `search` (CWE-202,612)

Searches the store for a value, and returns whether or not it is found. When
compiled with a weakness, the request's domain is not checked and the value is
searched in all domains.

The `search` variant returns a buffer containing all of the matches and some
context around them.

#### `set_env` (CWE-526,214)

This function exposes functionality that sets an environment variable by reading
a privileged memory location.

#### `sysconfig` (CWE-707)

This function interprets a user's request to fetch a resource. If the request
comes from a non-privileged domain, then ':U' is appended to the request,
otherwise ':S' is appended. The procedure that fetches the resource checks to
see which tag is set, and fetches from the system store if the system tag is
set. 

When compiled with a weakness, the request is not sanitized, meaning that the
user can append its own tag to the request, which will shadow the
system-appended tag.

## Tests

The components described above have weaknesses. Each weakness is witnessed by
a test in the `tests` directory:

### CWE-707 `atoi`

This test sends malformed requests to the store, asking for out-of-bounds
elements. If any request returns with the secret, then the test fails. 

Both the `atoi` interpreter and the `basic` interpreter should fail vs. this test, along
with every store implementation.

### CWE-524 `cache`

This test sends several requests from different domains in order to make sure
that a secret value is cached. The test ensures that when the location
containing the secret value is evicted, it is overitten with a value that is too
small to mask the secret value (and due to the weakness, the cached data is not
first cleared).

### CWE-226 `classify`

This test sets some data in a user's domain, marks it private using "classify",
and then attempts to "declassify" the data. The test checks to see if the
private data still exists after the declassification.

### CWE-201 `direct_sys`

This is a direct test of the `direct` function, which exposes a direct
information leakage.

### CWE-201,209 `error`

This is a direct test of the `error` function, which exposes a direct
information leakage through an error message.

### CWE-202,612 `indexing`, `indexing2`

Direct test of `search` and `search2`, which searches the store for a value, and
returns whether or not it is found. The test checks to see if the search routine indicates
that data was found in another domain.

### CWE-203 `login`

This test tests the `login` function, by first attempting to log in with a bad
username, then a bad password. The error messages are compared to check for
discrepancy.

### CWE-212 `mark_private`

First this test marks a user region as private, setting the private region to
SECRET_PATTERN. Next, the test broadcasts this memory object containing the private region.
The test finally checks the public domain to see if the private data has been scrubbed.

### CWE-526,214 `set_env`

The test directly calls `set_env` to set an environment variable with sensitive information.

### CWE-707 `sysconfig`

This test sends a request to read sysconfig. The request pre-empts the
implementation's tagging scheme to trick the system into performing a system
read rather than an unprivileged read.
