# Hardware Implementation / SoC #

*Intro TBD*

------------------

## Scoring Approach ##

Each test part gives a score from the testgen Enum `SCORES` object based on the subjective estimation of the 
severity of the test part. As most of the CWEs, and thus tests, of this class asks whether a certain mechanism is implemented/used or not, the score will be `NONE` if that mechanism seems to be in place according to the test's check, or a weakness score ranging from `V-LOW` and `V-HIGH` to denote its absense and severity.
 
In case of a multi-part tests, the overall test score is the minimum score achieved among this test's parts.

------------------

### TEST-1252 ###
CPU Hardware Not Configured to Support Exclusivity of Write and Execute Operations \[[CWE-1252](https://cwe.mitre.org/data/definitions/1252.html)\].

**Related CWEs**   

**Notes:**   

- According to the **privileged** RISC-V instruction set manual, the notion of this CWE can be reflected by the application of the physical memory protection (PMP). 
- This test is GDB dependent as the PMP is configured in machine mode (M). For backends that do not offer GDB support, this test is not implemented, e.g. Connectal on AWS-F1.
- The test interrupts the OS operation to inspect the values of the PMP configuration registers:
  - If the values indicate that the PMP is not being used, or there are not any protected regions, then we deduct that the hardware is not configured to protect write or execute operations, and the score is `V-HIGH`.
  - If a region that is protected against reading exists, but nothing else, then the score is `HIGH`.
  - If a region that is protected against writing exists, but not against execution, then the score is `MED`.
  - If a region that is protected against execution exists, then the score is `NONE`.

  ------------------