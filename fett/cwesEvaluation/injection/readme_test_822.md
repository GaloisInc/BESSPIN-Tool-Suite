### TEST-822 ###

Untrusted Pointer Dereference
\[[CWE-822](https://cwe.mitre.org/data/definitions/822.html)\].


**Notes:**
- The program obtains a value from an untrusted source, converts this 
value to a pointer, and dereferences the resulting pointer.

**FreeRTOS:**
- Implemented.

**Linux Debian and FreeBSD:** 
- The test demonstrates the consequences of untrusted Pointer Dereference.
 
- The `compare` function compares two strings character by character. 
- The `do_malicious_modification` function: 
  If the pointer is de-referenced for a write operation, the attack 
  might allow modification of critical program state variables,
  cause a crash, or execute code.

------------------ 