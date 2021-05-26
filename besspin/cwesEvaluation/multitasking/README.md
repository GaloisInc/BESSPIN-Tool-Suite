# Multitasking #

The multitasking tests evaluate the target's ability to run multiple programs
simultaneously, and to detect weaknesses that occur simultaneously.  The
multitasking tests re-run the CWE test parts that are both enabled from the
sequential run, and supported by the multitasking test runner.  It then reports
a score as a percentage of CWE scores that matched between the sequential and
multitasking runs.  This README details how to configure the test, how the test
works, the philosophy and algorithm behind scoring, and the supported platforms
and vulnerability classes that the test operates over.

## Configuration ##

Two configuration options in the `evaluateSecurityTests` section of the
configuration file control the operation of the multitasking tests:

- `runUnixMultitaskingTests`:  Enable or disable the multitasking tests.  If
  enabled, the multitasking tests will run after the sequential tests.  This
  option only affects Unix OSes and is ignored for FreeRTOS.
- `instancesPerTestPart`: The number of instances of each test part to be
  spawned as separate processes when running multitasking tests.

## Algorithm ##

The multitasking tests spawn multiple test processes as follows:

-  Create a lock file on the target.
-  Loop `instancesPerTestPart` times:
   -  For each enabled test that supports multitasking:
      -  Spawn a test wrapper on the target that spin locks until
         the lock file is removed.  Once the lock file is removed,
         execute the test.
-  Remove the lock file.
-  Wait for tests to complete or time out.
-  Score the test runs using the same scoring functions as the sequential run.
-  Compare test scores to sequential run (see Scoring Section for more).

By wrapping each test part in a program that blocks until the lock file is
removed, the tool stresses the ability of the processor to detect many
weaknesses occurring simultaneously.  Without this wrapper program, many of
the tests would run to completion before the target could spawn all off the
multitasking processes.

## Scoring ##

The objective of the multitasking tests is to evaluate the processor's ability
to concurrently run processes in a way that is consistent with its behavior
when running a single process.  Therefore, the multitasking score reflects how
similar the test scores are between the multitasking test runs and the
sequential test runs.  When a test running in multitasking mode earns the same
score as it did in the sequential run, it receives the multitasking score
`PASS`.  Otherwise, it receives the score `FAIL`.  The tool aggregates these
scores and presents them in the "Multitasking Pass" column in the score report
table.  This column presents the percentage of multitasking test runs that
scored `PASS` for a given CWE test.  For example, if:
* `instancesPerTestPart` is 5,
* TEST-192 scored `DETECTED` in the sequential test run, and
* TEST-192 scored `DETECTED` in 3 multitasking test runs and `HIGH` in 2
  multitasking runs,

then the "Multitasking Pass" cell for TEST-192 would read `60%`.

The tool also aggregates all multitasking scores across all tests and reports
it as a percentage.  For example, if 100 multitasking tests ran and 80 scored
`PASS`, you would see:
```
(Info)~  80/100 multitasking tests scored as expected (80.0%).
```

## Supported Platforms and Vulnerability Classes ##

The multitasking tests run only on Unix OSes, and support the following
vulnerability classes:

* Buffer Errors
* Resource Management
* Information Leakage
* Numeric Errors
