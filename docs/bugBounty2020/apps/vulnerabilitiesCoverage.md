# Vulnerabilities Coverage #

This document has detailed description of the vulnerabilities coverage of FETT applications.

## FreeRTOS ##

[FreeRTOS v.10.0.1](https://github.com/FreeRTOS/FreeRTOS/releases/tag/V10.0.1) and [amazon-freertos v.1.3.1](https://github.com/aws/amazon-freertos/releases/tag/v1.3.1) have the following:

- **CWEs Coverage:**
    - Buffer Errors
    - Permission, Privileges and Access Control
    - Resource Management
    - Information Leakage
    - Numeric Errors
    - Information Leakage

- **CVEs Details:**
    - [CVE-2018-16603](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16603): An issue was discovered in Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component. Out of bounds access to TCP source and destination port fields in xProcessReceivedTCPPacket can leak data back to an attacker.
    - [CVE-2018-16602](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16602): An issue was discovered in Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component. Out of bounds memory access during parsing of DHCP responses in prvProcessDHCPReplies can be used for information disclosure.
    - [CVE-2018-16601](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16601): An issue was discovered in Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component. A crafted IP header triggers a full memory space copy in prvProcessIPPacket, leading to denial of service and possibly remote code execution.
    - [CVE-2018-16600](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16600): An issue was discovered in Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component. Out of bounds memory access during parsing of ARP packets in eARPProcessPacket can be used for information disclosure.
    - [CVE-2018-16598](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16598): An issue was discovered in Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component. In xProcessReceivedUDPPacket and prvParseDNSReply, any received DNS response is accepted, without confirming it matches a sent DNS request.
    - [CVE-2018-16527](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16527): Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component allow information disclosure during parsing of ICMP packets in prvProcessICMPPacket.
    - [CVE-2018-16526](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16526): Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component allow remote attackers to leak information or execute arbitrary code because of a Buffer Overflow during generation of a protocol checksum in usGenerateProtocolChecksum and prvProcessIPPacket.
    - [CVE-2018-16525](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16525): Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component allow remote attackers to execute arbitrary code or leak information because of a Buffer Overflow during parsing of DNS\LLMNR packets in prvParseDNSReply.
    - [CVE-2018-16524](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16524): Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component allow information disclosure during parsing of TCP options in prvCheckOptions.
    - [CVE-2018-16523](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16523): Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware `TCP/IP` component allow division by zero in prvCheckOptions.
    - [INJECTED-1]: Using `strcpy()`, a potentially dangerous function, without checking the size of the received TFTP header, which might lead to a buffer overflow.


   ### WolfSSL 3.6 ###

- **CWEs Coverage:**
    - None

- **CVEs Details:**
    - None

The use of WolfSSL in the FETT FreeRTOS application is limited to the use of the Ed25519 algorithm for OTA signature verification. There are no known CVEs for this particular module.

## Unix ##

These are the applications for Linux Debian and FreeBSD.

### Web Server (Nginx v.1.13.12) ###

- **CWEs Coverage:**
    - Resource Management
    - Code Injection
    - Numeric Errors
    - Others

- **CVEs Details:**
    - [CVE-2020-5863](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-5863): In NGINX Controller versions prior to 3.2.0, an unauthenticated attacker with network access to the Controller API can create unprivileged user accounts. The user which is created is only able to upload a new license to the system but cannot view or modify any other components of the system.
    - [CVE-2019-9516](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-9516): Some `HTTP/2` implementations are vulnerable to a header leak, potentially leading to a denial of service. The attacker sends a stream of headers with a 0-length header name and 0-length header value, optionally Huffman encoded into 1-byte or greater headers. Some implementations allocate memory for these headers and keep the allocation alive until the session dies. This can consume excess memory.
    - [CVE-2019-9513](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-9513): Some `HTTP/2` implementations are vulnerable to resource loops, potentially leading to a denial of service. The attacker creates multiple request streams and continually shuffles the priority of the streams in a way that causes substantial churn to the priority tree. This can consume excess CPU.
    - [CVE-2019-9511](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-9511): Some `HTTP/2` implementations are vulnerable to window size manipulation and stream prioritization manipulation, potentially leading to a denial of service. The attacker requests a large amount of data from a specified resource over multiple streams. They manipulate window size and stream priority to force the server to queue the data in 1-byte chunks. Depending on how efficiently this data is queued, this can consume excess CPU, memory, or both.
    - [CVE-2019-20372](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-20372): NGINX before 1.17.7, with certain `error_page` configurations, allows HTTP request smuggling, as demonstrated by the ability of an attacker to read unauthorized web pages in environments where NGINX is being fronted by a load balancer.
    - [CVE-2018-16845](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16845): nginx before versions 1.15.6, 1.14.1 has a vulnerability in the `ngx_http_mp4_module,` which might allow an attacker to cause infinite loop in a worker process, cause a worker process crash, or might result in worker process memory disclosure by using a specially crafted mp4 file. The issue only affects nginx if it is built with the `ngx_http_mp4_module` (the module is not built by default) and the .mp4. directive is used in the configuration file. Further, the attack is only possible if an attacker is able to trigger processing of a specially crafted mp4 file with the `ngx_http_mp4_module.`
    - [CVE-2018-16844](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16844): nginx before versions 1.15.6 and 1.14.1 has a vulnerability in the implementation of `HTTP/2` that can allow for excessive CPU usage. This issue affects nginx compiled with the `ngx_http_v2_module` (not compiled by default) if the 'http2' option of the 'listen' directive is used in a configuration file.
    - [CVE-2018-16843](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16843): nginx before versions 1.15.6 and 1.14.1 has a vulnerability in the implementation of `HTTP/2` that can allow for excessive memory consumption. This issue affects nginx compiled with the `ngx_http_v2_module` (not compiled by default) if the 'http2' option of the 'listen' directive is used in a configuration file.
    - [CVE-2017-7529](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-7529): Nginx versions since 0.5.6 up to and including 1.13.2 are vulnerable to integer overflow vulnerability in nginx range filter module resulting into leak of potentially sensitive information triggered by specially crafted request.

### Database (SQLite v.3.22.0) ###

- **CWEs Coverage:**
    - Resource Management
    - Numeric Errors
    - Others

- **CVEs Details:**
    - [CVE-2020-11656](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-11656): In SQLite through 3.31.1, the ALTER TABLE implementation has a use-after-free, as demonstrated by an ORDER BY clause that belongs to a compound SELECT statement.
    - [CVE-2020-11655](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-11655): SQLite through 3.31.1 allows attackers to cause a denial of service (segmentation fault) via a malformed window-function query because the AggInfo object's initialization is mishandled.
    - [CVE-2019-16168](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-16168): In SQLite through 3.29.0, whereLoopAddBtreeIndex in sqlite3.c can crash a browser or other application because of missing validation of a `sqlite_stat1` sz field, aka a "severe division by zero in the query planner."
    - [CVE-2018-8740](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-8740): In SQLite through 3.22.0, databases whose schema is corrupted using a CREATE TABLE AS statement could cause a NULL pointer dereference, related to build.c and prepare.c.
    - [CVE-2018-20506](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20506): SQLite before 3.25.3, when the FTS3 extension is enabled, encounters an integer overflow (and resultant buffer overflow) for FTS3 queries in a "merge" operation that occurs after crafted changes to FTS3 shadow tables, allowing remote attackers to execute arbitrary code by leveraging the ability to run arbitrary SQL statements (such as in certain WebSQL use cases). This is a different vulnerability than CVE-2018-20346.
    - [CVE-2018-20346](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20346): SQLite before 3.25.3, when the FTS3 extension is enabled, encounters an integer overflow (and resultant buffer overflow) for FTS3 queries that occur after crafted changes to FTS3 shadow tables, allowing remote attackers to execute arbitrary code by leveraging the ability to run arbitrary SQL statements (such as in certain WebSQL use cases), aka Magellan.

### SSH Server (OpenSSH 7.3) ###

- **CWEs Coverage:**
    - Buffer Errors
    - Permission, Privileges and Access Control
    - Resource Management
    - Information Leakage
    - Buffer Errors
    - Others

- **CVEs Details:**
    - [CVE-2017-15906](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-15906)
    The process_open function in sftp-server.c in OpenSSH before 7.6 does not
    properly prevent write operations in readonly mode, which allows attackers to
    create zero-length files.
    - [CVE-2016-10708](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-10708)
    sshd in OpenSSH before 7.4 allows remote attackers to cause a denial of service
    (NULL pointer dereference and daemon crash) via an out-of-sequence NEWKEYS
    message, as demonstrated by Honggfuzz, related to kex.c and packet.c.
    - [CVE-2016-10012](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-10012)
    The shared memory manager (associated with pre-authentication compression) in
    sshd in OpenSSH before 7.4 does not ensure that a bounds check is enforced by
    all compilers, which might allows local users to gain privileges by leveraging
    access to a sandboxed privilege-separation process, related to the m_zback and
    m_zlib data structures.
    - [CVE-2016-10011](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-10011)
    authfile.c in sshd in OpenSSH before 7.4 does not properly consider the effects
    of realloc on buffer contents, which might allow local users to obtain sensitive
    private-key information by leveraging access to a privilege-separated child
    process.
    - [CVE-2016-10010](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-10010)
    sshd in OpenSSH before 7.4, when privilege separation is not used, creates
    forwarded Unix-domain sockets as root, which might allow local users to gain
    privileges via unspecified vectors, related to serverloop.c.
    - [CVE-2016-10009](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-10009)
    Untrusted search path vulnerability in ssh-agent.c in ssh-agent in OpenSSH
    before 7.4 allows remote attackers to execute arbitrary local PKCS#11 modules by
    leveraging control over a forwarded agent-socket.
    - [CVE-2018-8858](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-8858)
    ** DISPUTED ** The kex_input_kexinit function in kex.c in OpenSSH 6.x and 7.x
    through 7.3 allows remote attackers to cause a denial of service (memory
    consumption) by sending many duplicate KEXINIT requests. NOTE: a third party
    reports that "OpenSSH upstream does not consider this as a security issue."
