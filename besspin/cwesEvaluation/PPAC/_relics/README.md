# PPAC (Permission, Privileges and Access Control) #    

This vulnerability allows execution of unauthorized operations in a system.
A privilege vulnerability can allow inappropriate access to system privileges.
A permission vulnerability can allow inappropriate permission to perform functions.
An access vulnerability can allow inappropriate control of the authorizing policies for the hardware.

This directory has all the tests to evaluate PPAC vulnerabilities. The [testgen progress spreadsheet](https://docs.google.com/spreadsheets/d/1CNLjQN4VRd9_hAgm4UTgeuvEYDbKerKS5G_X0KlsMgA/edit?usp=sharing) logs the progress of which tests are implemented on which OS, and which system calls/modules should be supported.    

Note that each CWE has one test associated with it, however, a certain test could be testing other CWEs as well. In other words, to claim that a processor does not have a certain CWE means that it passes all the tests that are relevant to the CWE in question. This is illustrated by the *related CWEs* section under each test, and by the PPAC clafer model in this directory.

------------------

## Scoring Approach ##

Each test part gives a score from the testgen Enum `SCORES` object based on the subjective estimation of the 
severity of the test part. Some parts are only to check that the API is working as intended, and they will always 
either score `NONE` if the API is working, or `DoS` or `CALL-ERR` if they do not go through. Regarding the parts that 
give a weakness score (from `V-LOW` and `V-HIGH`), the codes either attempted to demonstrate the mere existence of a weakness 
or attempted a breach of this weakness. Either way, the tests assume a main concept: the user (i.e. the codes) is mis-using 
the API in a way that the weakness will be exposed. Then, the tests report what happens. If the processor reacts to this 
exposure, then they score *stronger*. If they do not react, then the weakness exists, and they score *weaker*.   

The overall test score is the minimum score achieved among this test's parts.

------------------

## Background ##
We hereby explain a few concepts/terms that are used throughout the tests description.

### Pluggable Authentication Module (PAM) ###
[PAM](https://en.wikipedia.org/wiki/Pluggable_authentication_module) is a mechanism to integrate multiple low-level authentication schemes into a high-level API. It allows programs that rely on authentication to be written independent of the underlying authentication scheme. 

[Linux-PAM](http://linux-pam.org/Linux-PAM-html/sag-introduction.html) is a suite of shared libraries that enable the local system administrator to choose how applications authenticate users. It is the purpose of the Linux-PAM project to separate the development of privilege granting software from the development of secure and appropriate authentication schemes. This is accomplished by providing a library of functions that an application may use to request that a user be authenticated. This PAM library is configured locally with a system file, `/etc/pam.conf` (or a series of configuration files located in `/etc/pam.d/`) to authenticate a user request via the locally available authentication modules.

### Transport Layer Security (TLS) ###
[TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security), and its now-deprecated predecessor, Secure Sockets Layer (SSL), are cryptographic protocols designed to provide communications security over a computer network. Several versions of the protocols find widespread use in applications such as web browsing, email, instant messaging, and voice over IP (VoIP). Websites can use TLS to secure all communications between their servers and web browsers.

The [TLS handshake](https://www.networkworld.com/article/2303073/lan-wan-what-is-transport-layer-security-protocol.html) is a multi-step process. A basic TLS handshake involves the client and server sending *hello* messages, and the exchange of keys, cipher message and a finish message. The multi-step process is what makes TLS flexible enough to use in different applications because the format and order of exchange can be modified.

A [digital certificate](https://en.wikipedia.org/wiki/Transport_Layer_Security#TLS_1.2) certifies the ownership of a public key by the named subject (subject common name (CN)) of the certificate, and indicates certain expected usages of that key. This allows others (relying parties) to rely upon signatures or on assertions made by the private key that corresponds to the certified public key.

In cryptography, a [certification authority (CA)](https://en.wikipedia.org/wiki/Certificate_authority) is an entity that issues digital certificates. The format of these certificates is specified by the X.509 standard. One particularly common use for certificate authorities is to sign certificates used in HTTPS, the secure browsing protocol for the World Wide Web. Another common use is in issuing identity cards by national governments for use in electronically signing documents.

------------------

## CIF (Control of Interaction Frequency Bugs) ##
The software does not properly limit the number of repeating interactions per specified unit \[[more](https://samate.nist.gov/BF/Classes/CIF.html)\].
Related CWEs:


### TEST-799 ###
Improper Control of Interaction Frequency \[[CWE-799](https://cwe.mitre.org/data/definitions/799.html)\].

**Related CWEs**
- [CWE-799](https://cwe.mitre.org/data/definitions/799.html).
- [CWE-837](https://cwe.mitre.org/data/definitions/837.html).
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).   
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).   

**Notes:**
- nAllowedInteractions>0 (used here as N)

**FreeRTOS:**
- WolfSSL is used for TLS v1.2 connection over TCP/IP. The target is a server that uses client verification. The target is always listening. When a connection is requested, the *actor* identity is considered to be the *subject CN* of the client certificate (that is presumably signed by a trusted CA authority). 
- A verification task is used to verify whether the *actor* had already submitted a request. If it is the first time, the task creates a counting semaphore with *N* as max count, otherwise, it requests a corresponding semaphore token for this actor.
- The test philosophy is that the structure that contains the names of the actors and their corresponding semaphores should both be protected and only accessible by the the special verification task. 
- A *breach* is when the `(N+1)th` request is granted permission.  

*Test Parts:*
- p01: *Baseline sanity part:* Use static structure with static semaphore. Attempt to request `N+1` times. `V-HIGH` if breached. `DoS` if blocked before `N+1`. 
- p02: *Expose the semaphore:* Use a non-static semaphore handle. After the Nth request, execute a malicious part that externs the handle and attempts to give tokens to it. Attempt to request `N+1` times. `V-HIGH` if granted, `HIGH` if was able to give the semaphore a token, `MED` if was able to obtain the semaphore handle. `V-LOW` if allowed before `N+1`.
- p03: *Expose the whole structure:* Use a non-static strucutre pointer. After the Nth request, execute a malicious part that externs the structure pointer and redirects it to NULL. Attempt to request `N+1` times. `V-HIGH` if breached, `HIGH` if was able to obtain the structure pointer, `V-LOW` if allowed before `N+1`.

**Linux Debian:**    
- The test philosophy is that there is a service that the user should be allowed to access for N times (per user). A root process is the one which is responsible of giving such authorization. The root process creates a root message queue `/Qroot`, and keeps listening on it. If a user process wants to access the service, it sends the user name to the root queue. When the root process receives the request, it sends N tokens on the user queue `/Qusername` (which means the user process should create this queue before submitting a request). For each token the user process receives, it is allowed to access the service once. This is protected by two policies: 1. `pam_limits` that enforces the user process queue size to be equal to `N*tokenSize bytes`. 2. `pam_listfile` that checks if the user had previously submitted a request. 

*Test Parts:*
- p01: Using an exposed `test799users` file that the attacker can delete its name from it. `V-HIGH` weakness if breached.
- p02: Use an exposed `limits.conf` file and create a longer queue in terms of number of messages. `LOW` weakness if breached.
- p03: Use an exposed `limits.conf` file and create a wider queue in terms of message length. `V-LOW` weakness if breached.
- p04: Use a valid protection using `pam_limits` and `pam_listfile`. Attempt to create a longer queue. `HIGH` weakness if breached.
- p05: Use a valid protection using `pam_limits` and `pam_listfile`. Attempt to receive an extra token. `V-HIGH` weakness if breached.
- p06: Use a valid protection. No attempt to breach. To ensure there is no DoS.

*Possible Extensions:*
- Non-local logins.
- Mess up with the tokens lengths to exploit the mqueue limits.
- Adding a check that the queue owner matches the username in the request. However, this does not affect the test because the test does not attempt to exploit that and it assumes that the user has access to the code (only binaries).
- Write a test part that does not use PAM, but implement one of the CWE code snippet examples.

**FreeBSD:**
- This is very similar to the Debian test. There are two differences: 1. We use PAM account module instead of session to verify that the user is authorized to access the service before granting them the access. 2. This is protected by the `pam_group` policy. After the user submits their request and receives their tokens, the root will add them to `service799` group. This group is denied access by the pam stack.

*Test Parts:*
- p01: Use a valid protection. Get all tokens, then ask for more. To ensure there the API works properly.
- p02: Use a valid protection. Attempt to receive an extra token. `V-HIGH` weakness if breached.
- p03: Expose the `/etc/group` file. The attacker can now remove themselves from the group from. `V-HIGH` weakness if breached.

------------------

### TEST-307 ###
Improper Restriction of Excessive Authentication Attempts \[[CWE-307](https://cwe.mitre.org/data/definitions/307.html)\].    

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-307](https://cwe.mitre.org/data/definitions/307.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-799](https://cwe.mitre.org/data/definitions/799.html).
- [CWE-837](https://cwe.mitre.org/data/definitions/837.html).

**Notes:**
- nAllowedAuthAttempts>0 (used here as N)
- Each part will be run three times:
	* User uses the correct authentication from the first attempt.
	* Correct authentication at the Nth attempt.
	* Correct authentication at the (N+1)th attempt.
- Therefore, for most parts, the output should be Granted, Granted, Denied.    

**FreeRTOS:**
- Use wolfSSL for TLS v1.2 connections over TCP/IP.

*Test Parts:*
- p01: The target is the server and the host machine is the client. `MED` if breached.
- p02: The host machine is the server and the target is the client. `V-HIGH` if breached.

**Linux Debian:**

*Test Parts:*
- p01: Authenticating without any restrictions. `V-LOW` weakness if breached.
- p02: Mis-using PAM by tallying on a non-existing file. `HIGH` weakness if breached.
- p03: Authenticating using a valid PAM configuration. `V-HIGH` weakness if breached.
- p04: Authenticating on a local file and deleting it each time there is an attempt. `V-LOW` if the malicious behavior is allowed but there is no breaching. `V-HIGH` if breached.   

*Possible Extensions:*
- Fake process tree.
- Non-local logins.
- Write a test part that does not use PAM, but implement one of the CWE code snippet examples.

**FreeBSD:**
- Use ssh to login, and use the `MaxAuthTries` in `/etc/ssh/sshd_config` to manipulate the OS.

*Test Parts:*
- p01: Set `MaxAuthTries` to `N+1`. Attempt `N+1` attempts. `NONE` if blocked, `CALL-ERR` if allowed.
- p02: Set `MaxAuthTries` to a large number (32). Attempt `N+1` attempts. `V-HIGH` if allowed.

------------------

### TEST-837 ###
Improper Enforcement of a Single, Unique Action \[[CWE-837](https://cwe.mitre.org/data/definitions/837.html)\].

**Notes:**
- No additional test is needed. This concept is implied by TEST-307 and TEST-799.

------------------

## ATN (Authentication Bugs) ##
The software does not properly protect credentials or check and prove source for access \[[more](https://samate.nist.gov/BF/Classes/ATN.html)\].
Related CWEs:


### TEST-284 ###
Improper Access Control \[[CWE-284](https://cwe.mitre.org/data/definitions/284.html)\].   

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).  
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).  
- [CWE-732](https://cwe.mitre.org/data/definitions/732.html).
- [CWE-863](https://cwe.mitre.org/data/definitions/863.html).

**Notes:**
- There are three main mechanisms of access control that should be tested:
	* **Authentication:** Verifying the actor identity.
	* **Authorization:** Verifying that the actor is authorized to access the service.
	* **Accountability:** Track the actor activity and report service access requests.
- In order to test CWE-284, most of the tests in this class should be run.

**FreeRTOS:**
- Use wolfSSL for TLS v1.2 connections over TCP/IP as in the test of CWE-799 to obtain an actor indentity, i.e. authentication. 
- A verification task verifies whether the *actor* is in the list of authorized users. This list should be protected and only accessible by the the special verification task.   
- Regarding accountability, a queue is used for logging and should be protected as well (same as `auth.log` in Linux). The verification task always sends to the queue whenever it is called. 

*Test Parts:*
- p01: Use a valid protection. Do not list the actor's name. `V-HIGH` if breached. `MED` if not logged.
- p02: Use a valid protection. List the actor's name. `DoS` if not granted. `MED` if not logged.
- p03: Use an exposed list to which the actor checker can add their name. `V-HIGH` if breached, `HIGH` if was able to obtain the list handle, `MED` if not logged.
- p04: Use a valid protection. List the actor's name. Use an exposed logging queue from which the actor can delete their activity. `HIGH` if the actor was able to delete their traces, `MED` if was able to obtain the queue handle, `V-LOW` if granted (because the logging mechanism is exposed). 

**Linux Debian/FreeBSD:**   
- Use a PAM policy stack that checks each the three main mechanisms of access:
	* **Authentication:** Use the account module type with `pam_unix` to verify the actor identity.   
	* **Authorization:** (*debian*): Use `pam_listfile` to check whether the user has the right of access explicitly provided in `test284users` file. (*FreeBSD*): Use `pam_group` to check whether the user belongs to an authorized group that is explicitly specified in the PAM stack. 
	* **Accountability:** Use `pam_warn` (*debian*) or the `debug` flag in `pam_group` (*FreeBSD*) to track the user activity and report that they tried to access that service.
- There are two things to check in the end of each test:
	1. The user was granted the access. (looking for the keyword `<GRANTED>` similar as previous tests)
	2. Checking the `/var/log/auth.log` (*debian*) or `/var/log/debug.log` (*FreeBSD*) for the log of the attempt; whether it succeeded or failed.

*Test Parts:*
- p01: Allow the user/group. `DoS` if not granted. `MED` if not logged.
- p02: Deny the user/group. `V-HIGH` if breached. `MED` if not logged. 
- p03: For Debian, use an exposed `test284users` file to which the user can add their name. For FreeBSD, use an exposed `/etc/group` to which the user can add themselves to any group of their choice. `V-HIGH` if breached. `MED` if not logged.
- p04: Restore the permissions. Allow the user/group. Use an exposed `auth.log` (*debian*) or `debug.log` (*FreeBSD*) file from which the user can delete their activity. `V-LOW` if granted (because it is an exposed logging file). `HIGH` if user was able to delete their traces.  

------------------

### TEST-287 ###
Improper Authentication \[[CWE-287](https://cwe.mitre.org/data/definitions/287.html)\].   

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-306](https://cwe.mitre.org/data/definitions/306.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-732](https://cwe.mitre.org/data/definitions/732.html).
- [CWE-862](https://cwe.mitre.org/data/definitions/862.html).   
- [CWE-863](https://cwe.mitre.org/data/definitions/863.html).

**FreeRTOS:**
- Use wolfSSL for TLS v1.2 connections over TCP/IP.
- A verification task verifies whether the *actor* is in the list of authorized users. This list should be protected and only accessible by the the special verification task.   
- The test philosophy is that the server, i.e. the target, should verify the client certificate to ensure that the incoming connection's identity is not being impersonated. Also, the actor's name should be obtained from the verified certificate, not from the actor, because they might be impersonating an authorized user.

*Test Parts:*
- p01: Baseline sanity check-1. The actor's name is authorized. The target verifies that the client's certificate is signed by a trusted CA authority, and uses the actor's name from within the certificate. `DoS` if not authorized.
- p02: Baseline sanity check-2. The actor's name is not authorized. The target verifies that the client's certificate is signed by a trusted CA authority, and uses the actor's name from within the certificate. `CALL-ERR` if authorized.
- p03: Use a client certificate signed by a non-trusted CA. Do not verify the client's authenticity. Get the username from the connection instead. `V-HIGH` if breached. This is similar to the example in the CWE description webpage. 

**Linux Debian:**    
- The test philosophy is that the `login` and `su` commands use the common authentication policy stack in `/etc/pam.d/common-auth` for authentication. This test asks a single question: will the hardware protect an unaware sysadmin? If the software -The OS here- improperly authenticate a crucial command like `su` and `login` and leaves the *front door* wide open, will the hardware be aware of that?
- Note that for `bluespec_p3`, the FreeBSD test is used instead.

*Test Parts:*
- p01a: The root user attempts to allow any local user access root. And try to access root privileges from a non-authorized user. `HIGH` if `<loginUser-GRANTED>`, `V-HIGH` if `<suRoot-GRANTED>` or `<loginRoot-GRANTED>`.
- p01b: The root user attempts to remove all authentication requirements. And try to access root privileges from a non-authorized user. `HIGH` if `<loginUser-GRANTED>`, `V-HIGH` if `<suRoot-GRANTED>` or `<loginRoot-GRANTED>`.
- p02: Make the common authentication policy writable by a non-root (`GID!=0`) group (using `chgrp`). `MED` if `common-auth` is owned by a group whose `GID!=0`, `HIGH` if writable by that group, and `DoS` if user could not be added to the group.
- p02a: A user from this non-root group attempts to allow any local user access root. And try to access root privileges. `HIGH` if `<loginUser-GRANTED>`, `V-HIGH` if `<suRoot-GRANTED>` or `<loginRoot-GRANTED>`. 
- p02b: A user from this non-root group attempts to remove all authentication requirements. And try to access root privileges. `HIGH` if `<loginUser-GRANTED>`, `V-HIGH` if `<suRoot-GRANTED>` or `<loginRoot-GRANTED>`. 
- p03: Make the common authentication policy writable by everyone. `HIGH` if `common-auth` is open access.
- p03a: A non-root user attempts to allow any local user access root, and try to access root privileges. `HIGH` if `<loginUser-GRANTED>`, `V-HIGH` if `<suRoot-GRANTED>` or `<loginRoot-GRANTED>`. 
- p03b: A non-root user attempts to remove all authentication requirements. And try to access root privileges. `HIGH` if `<loginUser-GRANTED>`, `V-HIGH` if `<suRoot-GRANTED>` or `<loginRoot-GRANTED>`

*Possible Extensions:*
- Login using a fake non-existing user [difficult because both of `su` and `login` read from `/etc/shadow`]
- An identity from the network, like using TLS certificates for instance.
- Write a test part that does not use PAM, but implement one of the CWE code snippet examples.

**FreeBSD:**
- The test philosophy is that the `su` command is a critical system functionality. This test asks a single question: will the hardware protect an unaware sysadmin? If the software -The OS here- improperly authenticate a crucial command like `su` and leaves the *front door* wide open, will the hardware be aware of that? 

- p01: Vanilla `su` pam stack. Attempt to `su root`. `CALL-ERR` if anything other than `DENIED`.
- p02: Change the `su` stack to mistakenly use `pam_permit.so` instead of `pam_rootok.so`. Attempt to `su root`. `V-HIGH` if `GRANTED`.

------------------

### TEST-288 ###
Authentication Bypass Using an Alternate Path or Channel \[[CWE-288](https://cwe.mitre.org/data/definitions/288.html)\].          
**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-288](https://cwe.mitre.org/data/definitions/288.html).
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-613](https://cwe.mitre.org/data/definitions/613.html).
- [CWE-863](https://cwe.mitre.org/data/definitions/863.html).

**FreeRTOS:**
- Use wolfSSL for TLS v1.2 connections over TCP/IP.
- The difference is subtle between this test and test-287. Note that according to the LANDO description, CWE-287 implies test-288 too.
- A verification task verifies whether the *actor* is in the list of authorized users. This list should be protected and only accessible by the the special verification task.   
- The test philosophy is that the server, i.e. the target, should verify the client certificate to ensure that the incoming connection's identity is not being impersonated. Also, the actor's name should be obtained from the verified certificate, not from the actor, because they might be impersonating an authorized user. This is the *correct path* of the authentication.
- The *alternate path* is that this test does not fail when this authentication fails, but instead, it asks the sender to provide their user name, at which point the impersonator obtains the access.

*Test Parts:*
- p01: Baseline sanity check-1. The actor's name is authorized. The target verifies that the client's certificate is signed by a trusted CA authority, and uses the actor's name from within the certificate. `V-LOW` if authorized because the alternate path exists.
- p02: Baseline sanity check-2. The actor's name is not authorized. The target verifies that the client's certificate is signed by a trusted CA authority, and uses the actor's name from within the certificate. `CALL-ERR` if authorized.
- p03: Use a client certificate signed by a non-trusted CA. The client verification should fail. The alternate path is activated, and the target asks the client for their name, at which point the client provides an authorized user name. `MED` if the program keeps going with the alternate path, and `V-HIGH` if breached. 

**Linux Debian:** 
- The test philosophy is that the service that requires authentication use keyrings as a bypass for doing so. It searches for an authentication key created by the root and logs in instead of authenticating. `auth pam_unix.so` is explicitly used to indicate authentication. Keyrings manipulation is performed to check whether the hardware detects that on a service that requires authentication.
- There are two things to check in the end of each test:
	1. The user was granted the access. (looking for the keyword `<GRANTED>` similar as previous tests).
	2. The user was granted the `<KEYAUTH>` for bypassing using a keyring instead.

*Test Parts:*
- p01: Use a valid keyring with valid permissions and proper linking. No key provided. Wrong password. `V-HIGH` if `<KEYAUTH>` or `<GRANTED>`.
- p02: Same as p01, but use the right password. `V-HIGH` if `<KEYAUTH>`, `DoS` if `<DENIED>`.
- p03: Use a valid keyring with valid permissions and proper linking. Use a valid key. `DoS` if `<NOKEY>`. `MED` if `<GRANTED>`.
- p04: Use a valid keyring with valid permissions and proper linking. Create a key with `UID!=0`. `HIGH` if `<KEYAUTH>`. `V-HIGH` if `<GRANTED>` with `<NOKEY>`.
- p05: Create a keyring with `UID!=0`. `V-HIGH` if `<KEYAUTH>` or `<GRANTED>`.

*Possible Extensions:*
- pam_timestamp.so on non-root users.


**FreeBSD:**
- One aspect mentioned in the CWE writeup is that the some applications may
  (ab)use information about the environment to (mistakenly) derive an
  authentication status. Hence, in the FreeBSD test, the test program checks the
  `CWD`: if it is a "privileged" location, then the test skips `PAM`-based
  authentication.

*Test Parts:*
- p01: Run the test in the user's home directory. The test will try to authenticate using PAM configured with `pam_deny` -- and is expected _not_ to grant authentication.
- p02: The test is run from a special directory, "cgi-bin". `V-HIGH` if `<GRANTED>`.

------------------

### TEST-289 ###
Authentication Bypass by Alternate Name \[[CWE-289](https://cwe.mitre.org/data/definitions/289.html)\].  

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-289](https://cwe.mitre.org/data/definitions/289.html). 
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html). 
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).   
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-732](https://cwe.mitre.org/data/definitions/732.html).
- [CWE-863](https://cwe.mitre.org/data/definitions/863.html).

**Notes:**
- This CWE is concerned about two points:   
	1. Using of blacklists instead of whitelists.
	2. Authenticating based on the name of either [1] The actor, or [2] The resource.

**FreeRTOS:**
- Use wolfSSL for TLS v1.2 connections over TCP/IP.
- A verification task verifies whether the *actor's name* is *NOT* in the list of blacklisted users, and the *caller task* is *NOT* in the list of unauthorized tasks. These lists should be protected and only accessible by the the special verification task.
- The test philosophy is that the server, i.e. the target, should verify the client certificate to ensure that the incoming connection's identity is not unauthorized. This technique implements a blacklist. 
- Regarding the name of the actor, the test uses the subject CN name in the client's certificate. The test assumes that the malecious user was able to get another certificate from one of the trusted CA providers while changing the capitalization of their legal name. Consequently, the malecious user would be able to access the service if such bypass is allowed by the hardware.
- Regarding the name of the resource, the test uses the task's name. The test assumes that the malecious task creates another task with a different name, and thus maleciously accesses the service.

*Test Parts:*
- p01: Use everything legally; do not list the user or the task. `V-LOW` if authenticated because it uses a blacklist of names to grant authentication. 
- p02: List the username. Use a different capitalization than the list (for compatibility with other tests, it is easier to start with the wrong list than to change the certificate). `V-HIGH` if breached.
- p03: List the task's name. From the unauthorized task, create another task that asks for permission. `V-HIGH` if breached.

**Linux Debian:**    
- The test philosophy is to use `pam_succeed_if.so` with an inequality condition to implement a blacklist.
- Regarding the name of the actor, the test uses the `username`. It assumes the service is blacklisting a user. Then, the user requests a name change from the admin. The admin renames their account. Consequently, the malecious user would be able to access this service, despite having their home directory with the same blacklisted name.
- Regarding the name of the resource, the test uses the `shell` name. It assumes the service is blacklisting the two installed shells: `/bin/bash` and `/bin/sh`, as resources. The user uses `chsh` to change their shell to a symbolic link `/bin/rbash -> /bin/bash`, and authenticate with it through the service.

*Test Parts:*
- p01: Use everything legally. `V-LOW` if authenticated because it uses a blacklist of names to grant authentication. 
- p02: The admin uses `usermod` to rename the username to `ssithLord`, and then the user attempts to authenticate. `V-HIGH` if breached. 
- p03: The user changes their shell to the symbolic link `/bin/rbash`, and then attempts to authenticate. `V-HIGH` if breached.

**FreeBSD:**
- The test uses `pam_group.so` to implement a blacklist. 

*Test Parts:*
- p01: Sanity check to make sure the blacklist is working. It is an error if auth is granted.
- p02: Blacklist is a group that does not exist. `MED` if auth is granted.
- p03: Blcaklist a real group, but then rename the blacklisted group in the system (without updating the PAM config). `V-HIGH` if auth is granted.


*Possible Extensions:*
- An additional resource test.

------------------

### TEST-290 ###
Authentication Bypass by Spoofing \[[CWE-290](https://cwe.mitre.org/data/definitions/290.html)\].   

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-290](https://cwe.mitre.org/data/definitions/290.html).
- [CWE-291](https://cwe.mitre.org/data/definitions/291.html).
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).

**FreeRTOS:**
- Use UDP connections.
- The test philosophy is that the server, i.e. the target, receives an incoming request for a certain actor, and it allows access to the actor based on the IP of the request.
- A verification task verifies whether the *actor's IP* is in the list of authorized IPs. This list should be protected and only accessible by the the special verification task.
- Test-294 does the same in TCP.

*Test Parts:*
- p01: Baseline sanity check. The actor's IP is authorized. No spoofing. `MED` if authorized; authentication should not be based solely on IP.
- p02: The actor's IP is not authorized. The client (host) spoofs one of the authorized IPs. `V-HIGH` if breached.   

**Linux Debian/FreeBSD:**    
- No additional test is needed. This is covered by TEST-294.

------------------

### TEST-291 ###
Reliance on IP Address for Authentication \[[CWE-291](https://cwe.mitre.org/data/definitions/291.html)\].    

**Notes:**
- No additional test is needed. This concept is implied by TEST-290 and TEST-294.

------------------

### TEST-293 ###
Using Referer Field for Authentication \[[CWE-293](https://cwe.mitre.org/data/definitions/293.html)\].    

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-345](https://cwe.mitre.org/data/definitions/345.html).
- [CWE-346](https://cwe.mitre.org/data/definitions/346.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).

**Notes:**
- Too niche and high-level. TEST-290 and TEST-294 are sufficient in testing the underlying concept. No additional test is needed.

------------------

### TEST-294 ###
Authentication Bypass by Capture-replay \[[CWE-294](https://cwe.mitre.org/data/definitions/294.html)\].   

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-290](https://cwe.mitre.org/data/definitions/290.html).
- [CWE-291](https://cwe.mitre.org/data/definitions/291.html).
- [CWE-294](https://cwe.mitre.org/data/definitions/294.html).
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-863](https://cwe.mitre.org/data/definitions/863.html).

**FreeRTOS:**
- Use TCP connection.
- The test philosophy is that the server, i.e. the target, receives an incoming connection for a certain actor, and it allows access to the actor based on the IP of the connection.
- A verification task verifies whether the *actor's IP* is in the list of authorized IPs. This list should be protected and only accessible by the the special verification task.

*Test Parts:*
- p01: Baseline sanity check. The actor's IP is authorized. No spoofing. `MED` if authorized; authentication should not be based solely on IP.
- p02: The actor's IP is not authorized. The client (host) spoofs one of the authorized IPs, and establishes a TCP connection. `V-HIGH` if breached.   

**Linux Debian/FreeBSD:**    
- The idea here is that CWE-290 and CWE-294 are revolving around the exact same concept. If an aspect of authentication relies on the IP, then spoofing using capture-replay could bypass authentication.
- The tests uses [hosts.allow](https://linux.die.net/man/5/hosts.allow) and [hosts.deny](https://linux.die.net/man/5/hosts.deny) on Debian, and [hosts.allow](https://www.freebsd.org/cgi/man.cgi?query=hosts.allow&sektion=5&n=1) on FreeBSD to determine which IPs are allowed to authenticate using SSH.

*Test Parts:*
- p01: Block everyone from SSH except a certain IP (not the host). Attempt to SSH. `CALL-ERR` if allowed.
- p02: Allow the host's IP. `HIGH` if allowed. `CALL-ERR` if blocked.

------------------

### TEST-257 ###
Storing Passwords in a Recoverable Format \[[CWE-257](https://cwe.mitre.org/data/definitions/257.html)\].   

**Related CWEs**
- [CWE-257](https://cwe.mitre.org/data/definitions/257.html).
- [CWE-260](https://cwe.mitre.org/data/definitions/260.html).
- [CWE-261](https://cwe.mitre.org/data/definitions/261.html).
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-798](https://cwe.mitre.org/data/definitions/798.html).

**FreeRTOS:**
- Use wolfSSL for TLS v1.2 connections over TCP/IP.
- The test philosophy is that the server, i.e. the target, receives an incomming connection. It verifies the actor's name from the certificate, and receives the password through the connection. Then a protected task should verify the password. 

*Test Parts:*
- p01: Baseline non-recoverable check. Use a list of stored password hashes (SHA256). `DoS` if not granted.
- p02: Use a list of base64 encoded passwords. `V-HIGH` if granted.
- p03: Use a list of hard-coded plain-text passwords. `V-HIGH` if granted.   

**Linux Debian/FreeBSD:**    
- p01: Attempt to change a user's password using PAM. The new password is stored in plaintext in the application. `V-HIGH` if the password change succeeds.

------------------

### TEST-259 ###
Use of Hard-coded Password \[[CWE-259](https://cwe.mitre.org/data/definitions/259.html)\].   

**Related CWEs**
- [CWE-257](https://cwe.mitre.org/data/definitions/257.html).
- [CWE-259](https://cwe.mitre.org/data/definitions/259.html).
- [CWE-260](https://cwe.mitre.org/data/definitions/260.html).
- [CWE-261](https://cwe.mitre.org/data/definitions/261.html).
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-798](https://cwe.mitre.org/data/definitions/798.html).

**Notes:**    
- CWE-259 can be divided into three main variants:
	1. Inbound authentication.
	2. Outbound authentication, as in front-end to back-end or vice versa.
	3. Configuration files.

**FreeRTOS:**
- Use wolfSSL for TLS v1.2 connections over TCP/IP.
- Inbound test: the target is the server. It receives an incoming connection for a certain actor, who provides a password. Then, a protected service decides whether this is a regular user or an administrator based on a certain actor/password hardcoded pair.  
- Outbound test: the client, i.e. the target, connects to a server, then provides an admin password.

*Test Parts:*
- p01: Inbound test. Target is the server. Hard-coded password. Once a user account and once an admin account. `V-HIGH` if granted for admin, and `MED` if granted for a user, because the check is against a hardcoded password.
- p02: Outbound test. Target is the client. Hard-coded password to access the server side. `V-HIGH` if granted.

**Linux Debian/FreeBSD:**    
- No additional test is needed. This is covered by TEST-257.

------------------

### TEST-260 ###
Password in Configuration File \[[CWE-260](https://cwe.mitre.org/data/definitions/260.html)\].   

**Related CWEs**
- [CWE-257](https://cwe.mitre.org/data/definitions/257.html).
- [CWE-259](https://cwe.mitre.org/data/definitions/259.html).
- [CWE-260](https://cwe.mitre.org/data/definitions/260.html).
- [CWE-261](https://cwe.mitre.org/data/definitions/261.html).
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-798](https://cwe.mitre.org/data/definitions/798.html).

**FreeRTOS:**
- Since FreeRTOS in SSITH is used without a filesystem, then *configuration files* do not apply.    

**Linux Debian:**    
- TEST-257 is sufficient in testing the underlying concept. No additional test is needed.

------------------

### TEST-261 ###
Weak Cryptography for Passwords \[[CWE-261](https://cwe.mitre.org/data/definitions/261.html)\].   
   
**Notes:**
- No additional test is needed. This concept is implied by TEST-257, and TEST-259.

------------------

### TEST-262 ###
Not Using Password Aging \[[CWE-262](https://cwe.mitre.org/data/definitions/262.html)\].   

**Notes:**    
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-263 ###
Password Aging with Long Expiration \[[CWE-263](https://cwe.mitre.org/data/definitions/263.html)\].   

**Notes:**    
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-301 ###
Reflection Attack in an Authentication Protocol \[[CWE-301](https://cwe.mitre.org/data/definitions/301.html)\].   

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-301](https://cwe.mitre.org/data/definitions/301.html).
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).

**Notes:**    
- The test philosophy is to do two things:
	1. Use an *unbreakable* protocol, but in a *bad* way. It is still *unbreakable* using a simple test, so the test does not actually breach it. However, it is used in a *not-good-security-practice* way. 
	2. Use a simpler protocol that can be breached using a simple reflection attack. 

**FreeRTOS:**
- Authentication protocol over TCP/IP.
- The *unbreakable* protocol is [Diffie-Hellman key exchange](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange). This [article](https://medium.com/@sadatnazrul/diffie-hellman-key-exchange-explained-python-8d67c378701c) provides a simpler explanation. A self-signed certificate is used.
- The *simpler protocol* is using the Diffie-Hellman `p` as the key, and using it for a simple challenge. 

*Test Parts:*
- p01: Regular DH protocol. Use same DH certificate for any request. Use a different key-pair for every connection. `MED` if allowed.
- p02: Regular DH protocol. Use same DH certificate for any request. Use the same key-pair for every connection. `HIGH` if allowed.
- p03: DH-style protocol using challenges. Use same DH certificate for any request. Perform a reflection attack. `V-HIGH` if the client, which does not possess the DH certificate, completes the challenge.

**Linux Debian/FreeBSD:**    
- Protocol level. Will only implement if specifically asked by a SSITH's team.

------------------

### TEST-302 ###
Authentication Bypass by Assumed-Immutable Data \[[CWE-302](https://cwe.mitre.org/data/definitions/302.html)\].   
   
**Notes:**
- No additional test is needed. This concept is implied by TEST-287, TEST-288, TEST-289, TEST-290, TEST-294, and TEST-301.

------------------

### TEST-303 ###
Incorrect Implementation of Authentication Algorithm \[[CWE-303](https://cwe.mitre.org/data/definitions/303.html)\].   
   
**Notes:**
- No additional test is needed. This concept is implied by TEST-257, TEST-259, TEST-287, TEST-288, TEST-289, TEST-290, TEST-294, TEST-301, and TEST-307.

------------------

### TEST-304 ###
Missing Critical Step in Authentication \[[CWE-304](https://cwe.mitre.org/data/definitions/304.html)\].   
   
**Notes:**
- No additional test is needed. This concept is implied by TEST-257, TEST-259,  TEST-287, TEST-288, TEST-289, TEST-290, TEST-294, TEST-301, and TEST-307.

------------------

### TEST-305 ###
Authentication Bypass by Primary Weakness \[[CWE-305](https://cwe.mitre.org/data/definitions/305.html)\].   
   
**Notes:**
- No additional test is needed. This concept is implied by TEST-257, TEST-259, TEST-287, TEST-288, TEST-289, TEST-290, TEST-294, TEST-301, and TEST-307.

------------------

### TEST-306 ###
Missing Authentication for Critical Function \[[CWE-306](https://cwe.mitre.org/data/definitions/306.html)\].   

**FreeRTOS:**
- Since FreeRTOS lacks a standard API that controls users or logins, this CWE does not apply.    

**Linux Debian:**    
- No additional test is needed. This concept is implied by TEST-287.

------------------

### TEST-307 ###
Improper Restriction of Excessive Authentication Attempts \[[CWE-307](https://cwe.mitre.org/data/definitions/307.html)\].    

**Notes:**
- This CWE is already included in the first sub-class: [CIF](#CIF-Control-of-Interaction-Frequency-Bugs).

------------------

### TEST-308 ###
Use of Single-factor Authentication \[[CWE-308](https://cwe.mitre.org/data/definitions/308.html)\].  

**Notes:**    
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-309 ###
Use of Password System for Primary Authentication \[[CWE-309](https://cwe.mitre.org/data/definitions/309.html)\].    

**Notes:**    
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-345 ###
Insufficient Verification of Data Authenticity \[[CWE-345](https://cwe.mitre.org/data/definitions/345.html)\].    

**Notes:**   
- No additional test is needed. This concept is implied by TEST-284, TEST-287, TEST-288, TEST-289, TEST-290, and TEST-294.

------------------

### TEST-346 ###
Origin Validation Error \[[CWE-346](https://cwe.mitre.org/data/definitions/346.html)\].    

**Notes:**   
- No additional test is needed. This concept is implied by TEST-284, TEST-287, TEST-288, TEST-289, TEST-290, and TEST-294.

------------------

### TEST-384 ###
Session Fixation \[[CWE-384](https://cwe.mitre.org/data/definitions/384.html)\].    

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-288](https://cwe.mitre.org/data/definitions/288.html).
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-346](https://cwe.mitre.org/data/definitions/346.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-613](https://cwe.mitre.org/data/definitions/613.html).
- [CWE-732](https://cwe.mitre.org/data/definitions/732.html).
- [CWE-863](https://cwe.mitre.org/data/definitions/863.html).

**FreeRTOS:**
- Since FreeRTOS lacks a standard API for sessions, this CWE does not apply.    

**Linux Debian/FreeBSD:**    
 - The test philosophy is to witness an application that authenticates several
 users, but _reuses_ session data (_i.e._, state). The state is managed using
 `pam_env` on debian, and using `pam_set_env` on FreeBSD. Note that 'session' in
 the CWE does not map cleanly to pam sessions, but rather to the state that
 would be associated with the client application.

*Test Parts:*
- p01: Authenticate the `root` user and set up an environment variable with some
  session info. Then authenticate a non-`root` user and print out the session
  info again. The application does not clear the old session data, and hence if
  the same info is displayed, this indicates a weakness.

------------------

### TEST-521 ###
Weak Password Requirements \[[CWE-521](https://cwe.mitre.org/data/definitions/521.html)\].    

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).

**FreeRTOS:**
- Since FreeRTOS lacks a standard API for authentication, this CWE does not apply.    

**Linux Debian:**    
- Not yet implemented.

------------------

### TEST-522 ###
Insufficiently Protected Credentials \[[CWE-522](https://cwe.mitre.org/data/definitions/522.html)\].    

**Notes:**   
- No additional test is needed. This concept is implied by TEST-257 and TEST-259.

------------------

### TEST-523 ###
Unprotected Transport of Credentials \[[CWE-523](https://cwe.mitre.org/data/definitions/523.html)\]. 

**Notes:**   
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-549 ###
Missing Password Field Masking \[[CWE-549](https://cwe.mitre.org/data/definitions/549.html)\].    

**Notes:**   
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-592 ###
Authentication Bypass Issues \[[CWE-592](https://cwe.mitre.org/data/definitions/592.html)\].    

**Notes:**
- This weakness has been deprecated by Mitre because it covered redundant concepts already described in [CWE-287](cwe-287). 
- No additional test is needed. This concept is implied by TEST-257, TEST-259, TEST-287, TEST-288, TEST-289, TEST-290, TEST-294, TEST-301, TEST-307, and TEST-384.   

------------------

### TEST-593 ###
Authentication Bypass: OpenSSL CTX Object Modified after SSL Objects are Created \[[CWE-593](https://cwe.mitre.org/data/definitions/593.html)\].

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-288](https://cwe.mitre.org/data/definitions/288.html).
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).
- [CWE-863](https://cwe.mitre.org/data/definitions/863.html).

**Notes:**   
- Too niche. No additional test is needed. This concept is implied by TEST-287, TEST-288, TEST-289, TEST-290, TEST-294, TEST-301, TEST-307, and TEST-384.

------------------

### TEST-603 ###
Use of Client-Side Authentication \[[CWE-603](https://cwe.mitre.org/data/definitions/603.html)\].

**Notes:**   
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-620 ###
Unverified Password Change \[[CWE-620](https://cwe.mitre.org/data/definitions/620.html)\].

**Notes:**   
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-640 ###
Weak Password Recovery Mechanism for Forgotten Password \[[CWE-640](https://cwe.mitre.org/data/definitions/640.html)\].

**Notes:**
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-645 ###
Overly Restrictive Account Lockout Mechanism \[[CWE-645](https://cwe.mitre.org/data/definitions/645.html)\].

**Notes**
- This is too subjective to be evaluated. Will not be implemented.

------------------

### TEST-798 ###
Use of Hard-coded Credentials \[[CWE-798](https://cwe.mitre.org/data/definitions/798.html)\].    

**Notes:**   
- No additional test is needed. This concept is implied by TEST-257 and TEST-259.


------------------

### TEST-804 ###
Guessable CAPTCHA \[[CWE-804](https://cwe.mitre.org/data/definitions/804.html)\].

**Notes**
- This is out of SSITH's scope. Will not be implemented.

------------------

### TEST-836 ###
Use of Password Hash Instead of Password for Authentication \[[CWE-836](https://cwe.mitre.org/data/definitions/836.html)\].

**Related CWEs**
- [CWE-284](https://cwe.mitre.org/data/definitions/284.html).
- [CWE-285](https://cwe.mitre.org/data/definitions/285.html).
- [CWE-287](https://cwe.mitre.org/data/definitions/287.html).
- [CWE-288](https://cwe.mitre.org/data/definitions/288.html).
- [CWE-302](https://cwe.mitre.org/data/definitions/302.html).
- [CWE-303](https://cwe.mitre.org/data/definitions/303.html).
- [CWE-304](https://cwe.mitre.org/data/definitions/304.html).
- [CWE-305](https://cwe.mitre.org/data/definitions/305.html).
- [CWE-345](https://cwe.mitre.org/data/definitions/345.html).
- [CWE-346](https://cwe.mitre.org/data/definitions/346.html).
- [CWE-592](https://cwe.mitre.org/data/definitions/592.html).

**Notes:**    
- Crypto-specific. Will only implement if specifically asked by a SSITH's team.

------------------

## AUT (Authorization Bugs) ##
The software does not properly assign/check permissions to resources or privileges to users \[[more](https://samate.nist.gov/BF/Classes/AUT.html)\].
Related CWEs:


### TEST-285 ###
Improper Authorization \[[CWE-285](https://cwe.mitre.org/data/definitions/285.html)\].

**Notes:**    
- No additional test is needed. This concept is implied by TEST-284, TEST-287, TEST-288, TEST-289, TEST-290, TEST-294, TEST-301, TEST-307, TEST-384, and TEST-799. 

------------------

### TEST-613 ###
Insufficient Session Expiration \[[CWE-613](https://cwe.mitre.org/data/definitions/613.html)\].    

**Notes:**   
- No additional test is needed. This concept is implied by TEST-384 and TEST-288.

------------------

### TEST-732 ###
Incorrect Permission Assignment for Critical Resource \[[CWE-732](https://cwe.mitre.org/data/definitions/732.html)\].    

**Notes:**   
- No additional test is needed. This concept is implied by TEST-284, TEST-287, TEST-289, and TEST-384.

------------------

### TEST-862 ###
Missing Authorization \[[CWE-862](https://cwe.mitre.org/data/definitions/862.html)\].    

**Notes:**   
- No additional test is needed. This concept is implied by TEST-287.

------------------

### TEST-863 ###
Incorrect Authorization \[[CWE-863](https://cwe.mitre.org/data/definitions/863.html)\].    

**Notes:**   
- No additional test is needed. This concept is implied by TEST-284, TEST-287, TEST-288, TEST-289, TEST-294, and TEST-384. 

------------------




