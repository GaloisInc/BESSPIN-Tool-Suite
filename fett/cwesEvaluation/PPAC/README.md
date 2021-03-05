# PPAC (Permission, Privileges and Access Control) #    

This vulnerability allows execution of unauthorized operations in a system.
A privilege vulnerability can allow inappropriate access to system privileges.
A permission vulnerability can allow inappropriate permission to perform functions.
An access vulnerability can allow inappropriate control of the authorizing policies for the hardware.

------------------

## Testing ## 

Three created CWE concepts are introduced that enumarate the SSITH-relevant concepts from the NIST list.

## Notes on P1s ##

Given that for P1s, SSITH only supports FreeRTOS (and neither safeRTOS nor secureRTOS), and FreeRTOS provides neither of the following:   

    - A standard access control system
    - Access Control List (ACL)
    - POSIX compliant
    - Users control
    - Standard filesystem

PPAC tests and assessments will be restrained for UNIX systems.

------------------

### CWE-PPAC-1 ###

Missing authorization in privileged resource access.

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).   
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).   
- [CWE-288](https://cwe.mitre.org/data/definitions/288.html).
- [CWE-668](https://cwe.mitre.org/data/definitions/668.html).   
- [CWE-669](https://cwe.mitre.org/data/definitions/669.html). 
- [CWE-862](https://cwe.mitre.org/data/definitions/862.html).  
- [CWE-863](https://cwe.mitre.org/data/definitions/863.html).  

------------------

### CWE-PPAC-2 ###

Reliance on OS and software authentication. The hardware solely relies on the OS for authenticating a user, or an administrator.

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).   
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).   
- [CWE-288](https://cwe.mitre.org/data/definitions/288.html).   

**Test**   
The test attempts to login as a user on SSH using the user's password, then attempts to switch user to `root` using the root's password. This behavior is allowed on the OS by default. A `HIGH` score is assigned if the test was able to `su` to `root`, and a `LOW` score is granted if only the non-`root` logging in was permitted. 

------------------

### CWE-PPAC-3 ###

Security exceptions are not logged. When the hardware throws a security exception, it does not report/log it to a privileged location.

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).   

------------------
