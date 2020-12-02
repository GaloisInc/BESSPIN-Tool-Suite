# PPAC (Permission, Privileges and Access Control) #    

This vulnerability allows execution of unauthorized operations in a system.
A privilege vulnerability can allow inappropriate access to system privileges.
A permission vulnerability can allow inappropriate permission to perform functions.
An access vulnerability can allow inappropriate control of the authorizing policies for the hardware.

------------------

## Notes on P1s ##

Given that for P1s, SSITH only supports FreeRTOS (and neither safeRTOS nor secureRTOS), and FreeRTOS provides neither of the following:   
    - A standard access control system
    - Access Control List (ACL)
    - POSIX compliant
    - Users control
    - Standard filesystem
PPAC tests will be restrained for UNIX systems.

## Scoring Approach ##

Each test part gives a score from the testgen Enum `SCORES` object based on the subjective estimation of the 
severity of the test part. Some parts are only to check that the API is working as intended, and they will always 
either score `NONE` if the API is working, or `CALL-ERR` if they do not go through. Regarding the parts that 
give a weakness score (from `V-LOW` and `V-HIGH`), the codes either attempted to demonstrate the mere existence of a weakness or attempted a breach of this weakness. Either way, the tests assume a main concept: the user (i.e. the codes) is mis-using the API in a way that the weakness will be exposed. Then, the tests report what happens. If the processor reacts to this exposure, then they score *stronger*. If they do not react, then the weakness exists, and they score *weaker*.   

The overall test score is the minimum score achieved among this test's parts.

------------------

### CWE-PPAC-1 ###

Missing authorization in privileged resource access. A system call does not check the caller process privileges while accessing a privileged resource.

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).   
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).   
- [CWE-288](https://cwe.mitre.org/data/definitions/288.html).   
- [CWE-862](https://cwe.mitre.org/data/definitions/862.html).  
- [CWE-863](https://cwe.mitre.org/data/definitions/863.html).  

**Notes:**

- Test is to be implemented.

------------------

### CWE-PPAC-2 ###

Reliance on OS and software authentication. The hardware solely relies on the OS for authenticating a user, or an administrator.

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).   
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).   
- [CWE-288](https://cwe.mitre.org/data/definitions/288.html).   

**Notes:**

- This is a design recommendation. No test to be implemented. 

------------------

### CWE-PPAC-3 ###

Security exceptions are not logged. When the hardware throws a security exception, it does not report/log it to a privileged location.

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).   

**Notes:**

- Test is to be implemented.

------------------
