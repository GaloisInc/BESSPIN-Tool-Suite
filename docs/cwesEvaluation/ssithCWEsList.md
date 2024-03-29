# SSITH CWEs List
This file is automatically generated. Please do not edit.

To generate, please download a `.csv` version of the `Final List` sheet of the [Phase 3 CWEs Agreement](https://docs.google.com/spreadsheets/d/1xFl9oFcYGb6rLQpCbqQ_AiOPXq3P1GJKk5FxiY1o6XQ/edit#gid=1605695275) spreadsheet, and use [this utility](../../utils/ssithCWEsList.py).

## Totals Summary
---
| Vulnerability Classes | # of CWEs |
|-|-|
| Buffer Errors | 21 |
| PPAC | 3 |
| Resource Management | 26 |
| Information Leakage | 10 |
| Numeric Errors | 15 |
| Hardware SoC | 48 |
| Injection | 3 |
## Buffer Errors
---
| CWE | Description |
|-|-|
| [CWE-118](https://cwe.mitre.org/data/definitions/118) | Incorrect Access of Indexable Resource ('Range Error') |
| [CWE-119](https://cwe.mitre.org/data/definitions/119) | Improper Restriction of Operations within the Bounds of a Memory Buffer |
| [CWE-120](https://cwe.mitre.org/data/definitions/120) | Buffer Copy without Checking Size of Input ('Classic Buffer Overflow') |
| [CWE-121](https://cwe.mitre.org/data/definitions/121) | Stack-based Buffer Overflow |
| [CWE-122](https://cwe.mitre.org/data/definitions/122) | Heap-based Buffer Overflow |
| [CWE-123](https://cwe.mitre.org/data/definitions/123) | Write-what-where Condition |
| [CWE-124](https://cwe.mitre.org/data/definitions/124) | Buffer Underwrite ('Buffer Underflow') |
| [CWE-125](https://cwe.mitre.org/data/definitions/125) | Out-of-bounds Read |
| [CWE-126](https://cwe.mitre.org/data/definitions/126) | Buffer Over-read |
| [CWE-127](https://cwe.mitre.org/data/definitions/127) | Buffer Under-read |
| [CWE-129](https://cwe.mitre.org/data/definitions/129) | Improper Validation of Array Index |
| [CWE-130](https://cwe.mitre.org/data/definitions/130) | Improper Handling of Length Parameter Inconsistency |
| [CWE-131](https://cwe.mitre.org/data/definitions/131) | Incorrect Calculation of Buffer Size |
| [CWE-680](https://cwe.mitre.org/data/definitions/680) | Integer Overflow to Buffer Overflow |
| [CWE-785](https://cwe.mitre.org/data/definitions/785) | Use of Path Manipulation Function without Maximum-sized Buffer |
| [CWE-786](https://cwe.mitre.org/data/definitions/786) | Access of Memory Location Before Start of Buffer |
| [CWE-787](https://cwe.mitre.org/data/definitions/787) | Out-of-bounds Write |
| [CWE-788](https://cwe.mitre.org/data/definitions/788) | Access of Memory Location After End of Buffer |
| [CWE-805](https://cwe.mitre.org/data/definitions/805) | Buffer Access with Incorrect Length Value |
| [CWE-806](https://cwe.mitre.org/data/definitions/806) | Buffer Access Using Size of Source Buffer |
| [CWE-823](https://cwe.mitre.org/data/definitions/823) | Use of Out-of-range Pointer Offset |
## PPAC
---
| CWE | Description |
|-|-|
| [CWE-PPAC-1](../../besspin/cwesEvaluation/PPAC/README.md) | Missing authorization in privileged resource access; Related to CWEs 284-285-288-668-669-862-863. |
| [CWE-PPAC-2](../../besspin/cwesEvaluation/PPAC/README.md) | Reliance on OS and software authentication; Related to CWEs 284-287-288. |
| [CWE-PPAC-3](../../besspin/cwesEvaluation/PPAC/README.md) | Security exceptions are not logged to a privileged location; Related to CWE-284. |
## Resource Management
---
| CWE | Description |
|-|-|
| [CWE-188](https://cwe.mitre.org/data/definitions/188) | Reliance on Data/Memory Layout |
| [CWE-400](https://cwe.mitre.org/data/definitions/400) | Uncontrolled Resource Consumption |
| [CWE-404](https://cwe.mitre.org/data/definitions/404) | Improper Resource Shutdown or Release |
| [CWE-415](https://cwe.mitre.org/data/definitions/415) | Double Free |
| [CWE-416](https://cwe.mitre.org/data/definitions/416) | Use After Free |
| [CWE-463](https://cwe.mitre.org/data/definitions/463) | Deletion of Data Structure Sentinel |
| [CWE-467](https://cwe.mitre.org/data/definitions/467) | Use of sizeof() on a Pointer Type |
| [CWE-468](https://cwe.mitre.org/data/definitions/468) | Incorrect Pointer Scaling |
| [CWE-476](https://cwe.mitre.org/data/definitions/476) | NULL Pointer Dereference |
| [CWE-562](https://cwe.mitre.org/data/definitions/562) | Return of Stack Variable Address |
| [CWE-587](https://cwe.mitre.org/data/definitions/587) | Assignment of a Fixed Address to a Pointer |
| [CWE-588](https://cwe.mitre.org/data/definitions/588) | Attempt to Access Child of a Non-structure Pointer |
| [CWE-590](https://cwe.mitre.org/data/definitions/590) | Free of Memory not on the Heap |
| [CWE-672](https://cwe.mitre.org/data/definitions/672) | Operation on a Resource after Expiration or Release |
| [CWE-690](https://cwe.mitre.org/data/definitions/690) | Unchecked Return Value to NULL Pointer Dereference |
| [CWE-761](https://cwe.mitre.org/data/definitions/761) | Free of Pointer not at Start of Buffer |
| [CWE-762](https://cwe.mitre.org/data/definitions/762) | Mismatched Memory Management Routines |
| [CWE-763](https://cwe.mitre.org/data/definitions/763) | Release of Invalid Pointer or Reference |
| [CWE-770](https://cwe.mitre.org/data/definitions/770) | Allocation of Resources Without Limits or Throttling |
| [CWE-771](https://cwe.mitre.org/data/definitions/771) | Missing Reference to Active Allocated Resource |
| [CWE-772](https://cwe.mitre.org/data/definitions/772) | Missing Release of Resource after Effective Lifetime |
| [CWE-789](https://cwe.mitre.org/data/definitions/789) | Uncontrolled Memory Allocation |
| [CWE-825](https://cwe.mitre.org/data/definitions/825) | Expired Pointer Dereference |
| [CWE-908](https://cwe.mitre.org/data/definitions/908) | Use of Uninitialized Resource |
| [CWE-909](https://cwe.mitre.org/data/definitions/909) | Missing Initialization of Resource |
| [CWE-911](https://cwe.mitre.org/data/definitions/911) | Improper Update of Reference Count |
## Information Leakage
---
| CWE | Description |
|-|-|
| [CWE-200](https://cwe.mitre.org/data/definitions/200) | Exposure of Sensitive Information to an Unauthorized Actor |
| [CWE-201](https://cwe.mitre.org/data/definitions/201) | Exposure of Sensitive Information Through Sent Data |
| [CWE-202](https://cwe.mitre.org/data/definitions/202) | Exposure of Sensitive Information Through Data Queries |
| [CWE-203](https://cwe.mitre.org/data/definitions/203) | Observable Discrepancy |
| [CWE-205](https://cwe.mitre.org/data/definitions/205) | Observable Behavioral Discrepancy |
| [CWE-206](https://cwe.mitre.org/data/definitions/206) | Observable Internal Behavioral Discrepancy |
| [CWE-212](https://cwe.mitre.org/data/definitions/212) | Improper Removal of Sensitive Information Before Storage or Transfer |
| [CWE-226](https://cwe.mitre.org/data/definitions/226) | Sensitive Information Uncleared in Resource Before Release for Reuse |
| [CWE-244](https://cwe.mitre.org/data/definitions/244) | Improper Clearing of Heap Memory Before Release ('Heap Inspection') |
| [CWE-524](https://cwe.mitre.org/data/definitions/524) | Use of Cache Containing Sensitive Information |
## Numeric Errors
---
| CWE | Description |
|-|-|
| [CWE-128](https://cwe.mitre.org/data/definitions/128) | Wrap-around Error |
| [CWE-190](https://cwe.mitre.org/data/definitions/190) | Integer Overflow or Wraparound |
| [CWE-191](https://cwe.mitre.org/data/definitions/191) | Integer Underflow (Wrap or Wraparound) |
| [CWE-192](https://cwe.mitre.org/data/definitions/192) | Integer Coercion Error |
| [CWE-194](https://cwe.mitre.org/data/definitions/194) | Unexpected Sign Extension |
| [CWE-195](https://cwe.mitre.org/data/definitions/195) | Signed to Unsigned Conversion Error |
| [CWE-196](https://cwe.mitre.org/data/definitions/196) | Unsigned to Signed Conversion Error |
| [CWE-197](https://cwe.mitre.org/data/definitions/197) | Numeric Truncation Error |
| [CWE-234](https://cwe.mitre.org/data/definitions/234) | Failure to Handle Missing Parameter |
| [CWE-369](https://cwe.mitre.org/data/definitions/369) | Divide By Zero |
| [CWE-456](https://cwe.mitre.org/data/definitions/456) | Missing Initialization of a Variable |
| [CWE-457](https://cwe.mitre.org/data/definitions/457) | Use of Uninitialized Variable |
| [CWE-665](https://cwe.mitre.org/data/definitions/665) | Improper Initialization |
| [CWE-681](https://cwe.mitre.org/data/definitions/681) | Incorrect Conversion between Numeric Types |
| [CWE-824](https://cwe.mitre.org/data/definitions/824) | Access of Uninitialized Pointer |
## Hardware SoC
---
| CWE | Description |
|-|-|
| [CWE-208](https://cwe.mitre.org/data/definitions/208) | Observable Timing Discrepancy |
| [CWE-385](https://cwe.mitre.org/data/definitions/385) | Covert Timing Channel |
| [CWE-920](https://cwe.mitre.org/data/definitions/920) | Improper Restriction of Power Consumption |
| [CWE-1037](https://cwe.mitre.org/data/definitions/1037) | Processor Optimization Removal or Modification of Security-critical Code |
| [CWE-1050](https://cwe.mitre.org/data/definitions/1050) | Excessive Platform Resource Consumption within a Loop |
| [CWE-1189](https://cwe.mitre.org/data/definitions/1189) | Improper Isolation of Shared Resources on System-on-Chip (SoC) |
| [CWE-1193](https://cwe.mitre.org/data/definitions/1193) | Power-On of Untrusted Execution Core Before Enabling Fabric Access Control |
| [CWE-1209](https://cwe.mitre.org/data/definitions/1209) | Failure to Disable Reserved Bits |
| [CWE-1220](https://cwe.mitre.org/data/definitions/1220) | Insufficient Granularity of Access Control |
| [CWE-1221](https://cwe.mitre.org/data/definitions/1221) | Incorrect Register Defaults or Module Parameters |
| [CWE-1222](https://cwe.mitre.org/data/definitions/1222) | Insufficient Granularity of Address Regions Protected by Register Locks |
| [CWE-1223](https://cwe.mitre.org/data/definitions/1223) | Race Condition for Write-Once Attributes |
| [CWE-1224](https://cwe.mitre.org/data/definitions/1224) | Improper Restriction of Write-Once Bit Fields |
| [CWE-1231](https://cwe.mitre.org/data/definitions/1231) | Improper Implementation of Lock Protection Registers |
| [CWE-1232](https://cwe.mitre.org/data/definitions/1232) | Improper Lock Behavior After Power State Transition |
| [CWE-1233](https://cwe.mitre.org/data/definitions/1233) | Improper Hardware Lock Protection for Security Sensitive Controls |
| [CWE-1234](https://cwe.mitre.org/data/definitions/1234) | Hardware Internal or Debug Modes Allow Override of Locks |
| [CWE-1239](https://cwe.mitre.org/data/definitions/1239) | Improper Zeroization of Hardware Register |
| [CWE-1240](https://cwe.mitre.org/data/definitions/1240) | Use of a Risky Cryptographic Primitive |
| [CWE-1241](https://cwe.mitre.org/data/definitions/1241) | Use of Predictable Algorithm in Random Number Generator |
| [CWE-1242](https://cwe.mitre.org/data/definitions/1242) | Inclusion of Undocumented Features or Chicken Bits |
| [CWE-1243](https://cwe.mitre.org/data/definitions/1243) | Exposure of Security-Sensitive Fuse Values During Debug |
| [CWE-1245](https://cwe.mitre.org/data/definitions/1245) | Improper Finite State Machines (FSMs) in Hardware Logic |
| [CWE-1246](https://cwe.mitre.org/data/definitions/1246) | Improper Write Handling in Limited-write Non-Volatile Memories |
| [CWE-1251](https://cwe.mitre.org/data/definitions/1251) | Mirrored Regions with Different Values |
| [CWE-1252](https://cwe.mitre.org/data/definitions/1252) | CPU Hardware Not Configured to Support Exclusivity of Write and Execute Operations |
| [CWE-1253](https://cwe.mitre.org/data/definitions/1253) | Incorrect Selection of Fuse Values |
| [CWE-1254](https://cwe.mitre.org/data/definitions/1254) | Incorrect Comparison Logic Granularity |
| [CWE-1256](https://cwe.mitre.org/data/definitions/1256) | Hardware Features Enable Physical Attacks from Software |
| [CWE-1257](https://cwe.mitre.org/data/definitions/1257) | Improper Access Control Applied to Mirrored or Aliased Memory Regions |
| [CWE-1259](https://cwe.mitre.org/data/definitions/1259) | Improper Protection of Security Identifiers |
| [CWE-1260](https://cwe.mitre.org/data/definitions/1260) | Improper Handling of Overlap Between Protected Memory Ranges |
| [CWE-1261](https://cwe.mitre.org/data/definitions/1261) | Improper Handling of Single Event Upsets |
| [CWE-1262](https://cwe.mitre.org/data/definitions/1262) | Register Interface Allows Software Access to Sensitive Data or Security Settings |
| [CWE-1264](https://cwe.mitre.org/data/definitions/1264) | Hardware Logic with Insecure De-Synchronization between Control and Data Channels |
| [CWE-1268](https://cwe.mitre.org/data/definitions/1268) | Agents Included in Control Policy are not Contained in Less-Privileged Policy |
| [CWE-1270](https://cwe.mitre.org/data/definitions/1270) | Generation of Incorrect Security Identifiers |
| [CWE-1271](https://cwe.mitre.org/data/definitions/1271) | Missing Known Value on Reset for Registers Holding Security Settings |
| [CWE-1272](https://cwe.mitre.org/data/definitions/1272) | Debug/Power State Transitions Leak Information |
| [CWE-1273](https://cwe.mitre.org/data/definitions/1273) | Device Unlock Credential Sharing |
| [CWE-1274](https://cwe.mitre.org/data/definitions/1274) | Insufficient Protections on the Volatile Memory Containing Boot Code |
| [CWE-1276](https://cwe.mitre.org/data/definitions/1276) | Hardware Block Incorrectly Connected to Larger System |
| [CWE-1277](https://cwe.mitre.org/data/definitions/1277) | Firmware Not Updateable |
| [CWE-1279](https://cwe.mitre.org/data/definitions/1279) | Cryptographic Primitives used without Successful Self-Test |
| [CWE-1280](https://cwe.mitre.org/data/definitions/1280) | Access Control Check Implemented After Asset is Accessed |
| [CWE-1281](https://cwe.mitre.org/data/definitions/1281) | Sequence of Processor Instructions Leads to Unexpected Behavior (Halt and Catch Fire) |
| [CWE-1282](https://cwe.mitre.org/data/definitions/1282) | Assumed-Immutable Data Stored in Writable Memory |
| [CWE-1283](https://cwe.mitre.org/data/definitions/1283) | Mutable Attestation or Measurement Reporting Data |
## Injection
---
| CWE | Description |
|-|-|
| [CWE-INJ-1](../../besspin/cwesEvaluation/injection/README.md) | Untrusted Data Accessed as Machine Language Instructions |
| [CWE-INJ-2](../../besspin/cwesEvaluation/injection/README.md) | Untrusted Data Accessed as Heap Metadata |
| [CWE-INJ-3](../../besspin/cwesEvaluation/injection/README.md) | Untrusted Data Accessed as Trusted Data |
