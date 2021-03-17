# BESSPIN Security Evaluation Philosophy #

*This document is still under construction -- See ticket #1016, task#4*

*The following part is copied as is from the old documentation*

## Tests and Scoring

The testing philosophy is that for each CWE or a set of CWEs, the malicious code attempts
to implement the CWE model. In more practical terms, the code creates a scenario where the particular CWE 
can happen, then attempts to display it. The tests do not necessarily build a complete exploit model; we believe 
this is out of scope. But a test rather exhibits a glance of the weakness it enumerates, without implementing a fully unquestionable exploit.

Besspin tool-suite's testgen objective is to evaluate whether weaknesses exist, but does not make any assumptions or statements on how exploitable these weaknesses are.   

Each test runs on the target OS, and a logging report is generated. This report contains the stdout output of the target, in addition to some tool specific comments and/or GDB logs. The scoring is performed in the end by parsing each test's report.    

The scoring system is inspired from the common vulnerability scoring
system
([CVSS](https://en.wikipedia.org/w/index.php?title=Common_Vulnerability_Scoring_System&oldid=815384991)).
The scores levels are following the python Enum object `SCORES` defined
[here](./fett/cwesEvaluation/scoreTests.py/scoreTests.py).  The levels are (from *bad* to
*good*):
  1. `NOT-IMPLEMENTED`: this test is not implemented for this OS.
  2. `UNKNOWN`, `INVALID`, `FAIL`: All of these mean that something
     went wrong with either the test or the scoring.  Their individual
     meaning slightly differ from a test to another and from a class
     to another.  Please use the specific class Readme and the report
     files for further investigation.
  3. `DOS`: There was a denial of service; a test attempted to perform
     a legal action, and it was prevented from doing so.
  4. `CALL-ERR`: A call to a particular API has failed.
  5. `HIGH`: High weakness revealed by the test.  This means no
     security.  The non-secure baseline GFE scores `HIGH` on all
     tests.
  6. `MED`
  7. `LOW`
  8. `DETECTED`: The test ran to completion, and the weakness
      exists.  However, the processor was able to detect that a
      violation occurred.  This is a good score.
  9. `NONE`: This is the best achievable score.  Not only that the
      processor was able to detect the violation, it also prevented
      the test from continuing with the breach.


Each vulnerability class has a README document where more details about the testing philosophy and the 
scoring mechanism are provided. All classes use the same Enum object `SCORES`.   

It is worth mentioning that the tool, the tests, the scoring
mechanisms, etc. were are developed using a non-secure baseline
designs.  All our *good scoring* mechanisms were based on our
understanding of the philosophy of the TA-1 teams work and their
reports, and they were designed based on the developers imagination
and speculation.  Enhancements and modifications are expected as the
tool-suite is run on processors with secure features. 