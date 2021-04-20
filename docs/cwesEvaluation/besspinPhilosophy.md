# BESSPIN Security Evaluation Philosophy #

## Introduction ##

A part of the TA-2 work of the SSITH program was to evaluate the security features of the designed systems; how to validate the claims made by the hardware and firmware designers? The security evaluation mode of this tool is a test suite that evaluates processor/operating system pairs against the sets of MITRE Common Weakness Enumerations (CWEs). We believe that an attack, distinct from a weakness, is a crafted plot that exploits several weaknesses, stringing them together in order to achieve its malicious purpose. Abstractly, the weaknesses form a surface of dots, and an attack is a certain connection of those dots. By plugging each hole separately, we end up with an attack surface that exposes fewer dots, and thus crafting an attack plot becomes more challenging. 

The test suite methodology is to generate tests for each CWE, or for sets of CWEs, each of which creates a scenario where an instance of this particular CWE gets activated, then checks whether it went unnoticed. The objective is to evaluate whether each of those weaknesses exist, but we do not make any assumptions on how exploitable those weaknesses are; this is left to the security researchers.

---

## SSITH CWEs ##

*[CWE](https://cwe.mitre.org/) is a community-developed list of software and hardware weakness types. It serves as a common language, a measuring stick for security tools, and as a baseline for weakness identification, mitigation, and prevention efforts.* 

### Definitions ###

This section attempts to clarify the confusion between a set of terms that sometimes are nonchalantly -and mistakenly- used interchangeably: CWE, CVE, weakness, vulnerability, exploit, attack. We understand that some definitions or subtleties might be debatable, and thus the following definitions conforms with what we actually mean by those terms throughout the documents. 

We use the term *computer system* to mean hardware, firmware, software, or the interaction between them.

The term *weakness* does not have a standard definition. NIST's dictionary defines it as *"Poor coding practices, as exemplified by CWEs"*. Our stab at it would be that a weakness is a mistake or a missing feature in the design of a computer system.

A CWE is a *weakness type*, i.e. a classification of several weaknesses. For example, a weakness would be to read a stack string beyond its end. Another weakness would be to read a value from a heap array of integers before it begins. Both of these weaknesses can be classified into CWE-125: Out-of-bounds Read.

Both *vulnerability* and *exploit* define each other. A *vulnerability* is a weakness that could be exploited or triggered by a threat source. And an *exploit* is a piece of software that takes advantage of a vulnerability in a computer system.

*CVE* is a list of records —-each containing an identification number, a description, and at least one public reference—- for publicly known cybersecurity vulnerabilities. 

Basically, a CVE is a known vulnerability, a vulnerability is an exploitable weakness, and a weakness is a member of one or more CWEs.

An *attack* is any kind of malicious activity that attempts to collect, disrupt, deny, degrade, or destroy information system resources or the information itself. That is, an attack is an exploit attempt. And an *attack surface* is the set of points on the boundary of a system, a system element, or an environment where an attacker can try to enter, cause an effect on, or extract data from, that system, system element, or environment.


### Vulnerability Classes ###

The SSITH program seeks to develop hardware security architectures and associated design tools to protect systems against classes of hardware vulnerabilities exploited through software. The program identified the following seven classes of vulnerability:
- Buffer Errors
- Permission, Privileges and Access Control
- Resource Management
- Information Leakage
- Numeric Errors
- Injection
- Hardware SoC

For each class, the program chose a set of CWEs that addresses that class. The full list of CWEs are in [ssithCWEsList.md](./ssithCWEsList.md).

---

## Test Suite ##

The testing philosophy is that for each CWE or a set of CWEs, the malicious code attempts
to implement the CWE model. In more practical terms, the tool creates a scenario where an instance of a particular CWE 
occurs. The tests do not necessarily build a complete exploit model, but a test rather exhibits a glance of the weakness type it enumerates, without implementing a fully unquestionable exploit.

Besspin tool-suite's objective is to evaluate whether weaknesses exist, but it does not make any assumptions or statements on how exploitable these weaknesses are. 

Each test runs on top of an OS-backend pair, and the related output gets recorded in a separate report file per test. This report contains the stdout/stderr of the target plus any kernel messages, in addition to some tool specific comments and GDB logs if applicable. 

---

## Scoring ##

The scoring system, as well the Besspin Scale, are inspired from the common weakness scoring system ([CWSS](https://cwe.mitre.org/cwss/cwss_v1.0.1.html)). The scoring is performed in the end of a vulnerability class run (see [modes.md](../base/modes.md) for mode details) by parsing each test's report. The possible score values are detailed below (see the Python Enum object `SCORES` defined in [scoreTests.py](../../besspin/cwesEvaluation/scoreTests.py)). Please note that `HIGH` is the worst security score, and `NONE` is the best.  

1. `NOT_APPLICABLE` (`NA`): This CWE is not applicable to this OS-backend combination.
2. `NOT-IMPLEMENTED` (`NoImpl`): One or more tests are not yet implemented for this OS-backend pair.
3. `CALL-ERR`: The test encountered a known runtime error. For example, the difference between two pointer values is not as expected, or a memory allocation has failed, or an API call returned an erroneous code.
4. `FAIL`: Scoring has failed. This is probably due to a fatal unexpected error in the test, such as the test not starting, or it generated an empty log.
5. `HIGH`: High weakness revealed by the test. This means no security. The non-secure baseline GFE scores `HIGH` on the vast majority of tests.
6. `MED`
7. `LOW`
8. `DETECTED`: The processor was able to detect that a violation had occurred. In such case, the test scores `DETECTED` whether the test has run to completion or was interrupted mid-run. This reflects a perfect score.
9. `NONE`: This is another perfect score; The weakness type does not exist.

Each vulnerability class has a README in [cwesEvaluation/](../../besspin/cwesEvaluation/) with more details about the testing methodology and the scoring. 

It is worth mentioning that the tool, the tests, the scoring mechanisms, etc. were developed using a non-secure baseline
designs.  All our *good scoring* mechanisms were based on our understanding of the philosophy of the TA-1 teams work and their
reports, and they were designed based on the developers' imagination and speculation.  Enhancements and modifications are expected as the tool-suite is run on more processors with various secure features. 


### OS vs CPU ###

The line between the supervisor and the machine role in security is quite wide. This makes the tool-suite's job more difficult as we are trying to evaluate the security of a processor. Also, isolating the processor's role from any related firmware, or the OS running on top of it makes little sense in modern computer systems. This is the reason it is crucial to speak about processor-OS pairs when inspecting the tool-suite results. 

However, this complicates the evaluation process since modern OSes contain some mechanisms and practices that are related to the weaknesses under test. In the tool-suite, we made the following two assumptions/decisions:

1. *A baseline OS-processor pair can be protected against a specific weakness type.* For example, the accountability category (see [BESSPIN-Scale.pdf](./BESSPIN-Scale.pdf)) is about guaranteeing the tracking of suspicious activity, i.e. logging security exception in a privileged location. Most -if not all- modern Unix OSes guarantee that by default. In such a case, any processor would score `NONE` on that particular CWE type, and we decided to score it as such without expecting anything more from the processor, since the weakness type does not apply to the computer system as a whole.

2. *A kernel signal is not enough to protect against a specific weakness type.* This is a more subtle point and led to many discussions. What should the score be if the test for the weakness causes a segmentation fault? For example, [CWE-672](https://cwe.mitre.org/data/definitions/672) is about operating on a resource after expiration or release. One of the tests that covers this CWE is to allocate some memory bytes to a few pointers, then free one of them, and then access the memory location referenced by that freed pointer. In Debian for instance, this behavior leads to a segmentation fault. The question is: should this be considered as weakness type is not present in the OS-processor pair? Or can this be exploited somehow? In general, the tool treats segmentation faults as an artifact of tests that are not aware of the memory space of a process and therefore make no attempt to respect the bounds of that memory space.  However, a more sophisticated attacker could exploit the underlying weakness in a way that does not trigger a segmentation fault by leveraging awareness of the process's memory space.  Therefore, the tool scores `HIGH` for an uncaught segmentation fault.  We make a rare exception to this rule when a segmentation fault is sufficient to address the weakness.  For example, dereferencing a null pointer ([CWE-476](https://cwe.mitre.org/data/definitions/476)) on systems that never map virtual memory address `0x0` to a physical address always produces a segmentation fault, and is therefore sufficient to address the weakness.  These exceptional cases are noted in the test READMEs.

---

## BESSPIN Scale ##

The BESSPIN score is the security figure of merit that is used to evaluate the SSITH hardware. As any security metric, it is more subjective than empirical, but more structured than qualitative. The scale is represented by a percentage, where 0% means there is no protection against any SSITH CWEs, and 100% means that the processor protects against all SSITH CWEs. A detailed explanation of how this figure of merit is calculated is in [BESSPIN-Scale.pdf](./BESSPIN-Scale.pdf).

---

## Naïve CWEs Tally ##

For each vulnerability class, the CWEs scores are counted in a binary way: `1` for `NONE` or `DETECTED`, and `0` otherwise. Then, a percentage score will be computed as 100 times the sum of the binary scores divided by the number of CWEs of that class. Also, an overall single figure of merit will be computed in a similar fashion for all CWEs in the list. 