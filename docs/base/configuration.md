# Configuration #

The needed configuration is done using [INI
file](https://en.wikipedia.org/wiki/INI_file) configuration. The
default file is [config.ini](../../config.ini).

---

## Overview ##

[config.ini](../../config.ini) is commented with brief descriptions of
the meaning of every parameter and the possible values/types. Please note the following:
  - Keep the comments on separate lines from values. Order of
    parameters does not matter.
  - Section headers are required and they are between square brackets.
  - Parameter names and string values are treated as case sensitive. The only exception is boolean parameters; you can use 0/1, False/True, Yes/No [all case insensitive].

The configuration(s) is loaded in [config.py](../../besspin/base/config.py) and the dictionary of the sections, parameter names, supported data types, value ranges and choices, and conditions are listed in [configData.json](../../besspin/base/utils/configData.json).

This document has explanations for each parameter, either by defining them or linking to the document that has the definitions.

---

## [functionality] ##

The tool's functionality has a single parameter: `mode`. The document [modes.md](./modes.md) explains each mode, and links to all other documentation and resources about each of them.

---

## [cyberPhys] ##

This section is only loaded in the `cyberPhys` mode. Please refer to [cyberPhys/configuration.md](../cyberPhys/configuration.md) for details about each parameter. 

---

## [target] ##

This section determines the backend details of the tool's run. In `cyberPhys` mode, this section is not loaded from the main configuration INI file, but a separate `target` section per target is loaded from the additional `cyberPhys` INI file. Please refer to [cyberPhys/configuration.md](../cyberPhys/configuration.md) for more details.

The document [targets.md](./targets.md) has detailed explanation of the supported targets, their required setup, and the assumptions the tool makes. We explain the parameters here though:

- `binarySource`: The SSITH program has several TA-1 teams; each of which has their own processor design. The differences between these processors are the sources of many operational corner cases and exceptions. These exceptions are spread out all over the tool. We only support the following options for `binarySource`:
  - `GFE`: The government furnished equipment (GFE) is the baseline (Vanilla) implementation of the processors of the program. This is the safest choice for the use of a processor that does not belong to the other teams, and activates the least amount of exceptions.
  - `LMCO`: Lockheed Martin Corporation.
  - `Michigan`: University of Michigan.
  - `MIT`: Massachusetts Institute of Technology.
  - `SRI-Cambridge`: The CHERI work by SRI International and University of Cambridge.

- `sourceVariant`: This parameter serves in distinguishing between different *flavors* or *designs* when happen to exist for the same binarySource-processor for any reason. For `SRI-Cambridge`, the acceptable values are `default`, `purecap`, and `temporal`. Please refer to the [CHERI wesbite](https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/) for more details. For `LMCO`, the acceptable value for non-vcu118 P2/3 targets and all P1s is `default`, while for vcu118 P2/3 targets, the acceptable values are `combo-100` and `combo-015-017-100-101-103`; the values reflect which HARD pipelines are implemented in the bitstream.

- `target`: The backend of the target. The tool supports `qemu`, `vcu118`, and `awsf1`. The document [targets.md](./targets.md) has more details.

- `vcu118Mode`: Applicable iff the target is set to `vcu118`. Whether to choose the `nonPersistent` memory for programming the bitstream and loading the FPGA, or use the flash. `flashProgramAndBoot` is for initializing the FPGA, so the tool will program the flash first, then boot from it. Please note that this step would require the power cycling of the VCU118 board after programming and before booting. The last option, `flashBoot` is for booting directly from the FPGA flash memory. This assumes that the FPGA was programmed with the correct bitstream and operating system binary. If you need to change either, please use `flashProgramAndBoot` for your changes to take effect on the hardware.

- `processor`: The SSITH program supported the use of two different HDLs/styles to design the processors: BSV (by Bluespec) and Chisel; the tool describes this as *the processor flavor*. Also, throughout the program phases, the teams were designing: `P1`: a 32-bit microcontroller, `P2`: a 64-bit processor that can support Unix, `P3`: a 64-bit processor that supports OoO execution. The tool describes this as *the processor level*. Regarding the configuration, the `processor` setting should be in `{chisel|bluespec}_{p1|p2|p3}`.

- `osImage`: The operating system to be used. The program supports three OSes: Linux Debian, FreeBSD, and FreeRTOS. The tool also supports Linux Busybox for the sake of debugging and smoke testing since it is as light as Linux can get. The allowed values are thus: `debian`, `FreeBSD`, `FreeRTOS`, and `busybox`. The document [OSes.md](./OSes.md) has more details about the OSes building, compatibility with targets and processors, assumptions, etc.

- `elfLoader`: This is only applicable to VCU118 (the parameter name is old and non-ideal, ticket #473 should address this). There are two options to load the OS binary into the FPGA on VCU118: the first one is through JTAG using GDB load, which is the `JTAG` option. The second option is a workaround to speed up the binary loading since JTAG loading takes some time for large binaries. We use a FreeRTOS program that starts a TFTP client. This way, the large binary is uploaded using UDP, which is faster than JTAG. After completing the upload, the FreeRTOS program replaces itself and jumps to the first instruction of the uploaded OS booting sequence. We call this option `netboot`.

- `useCustomOsImage`: By default, the tool retrieves the binary of the chosen OS from its own resources: the binaries LFS checkout, or the Nix package manager (see [nix.md](./nix.md) for more details). Enabling this setting allows the user to provide their own OS binary.

- `pathToCustomOsImage`: The path to the custom OS binary in case `useCustomOsImage` is enabled.

- `useCustomProcessor`: By default, the tool retrieves the bitstreams or any required binaries such as the probe files for VCU118, or the kernel modules for AWS F1, from its own resources: the binaries LFS checkout, or the Nix package manager (see [nix.md](./nix.md) for more details). Enabling this setting allows the user to provide their bitstream and binaries.

- `pathToCustomProcessorSource`: The path to a directory containing all needed processor resources in case `useCustomProcessor` is enabled. For more details about the needed files names and directory structure, please refer to `BESSPIN-LFS`, the LFS repo, and compare.

- `useCustomQemu`: By default, the tool uses `qemu-system-riscv64`, built in Nix, to run the QEMU targets. Enable this setting to use your own binary.

- `pathToCustomQemu`: The path to the qemu binary in case `useCustomQemu` is enabled.

- `useCustomHwTarget`: This is introduced for many-board systems, where many VCU118 boards are connected to the same host. This setting can be enabled so that you can specify a particular HW target to use. When this is disabled, the tool uses the HW targets in whichever order Vivado `get_hw_targets` command returns them.

- `customHwTarget`: The HW target to use in case `useCustomHwTarget` is enabled.

- `useCustomTargetIp`: This is only applicable to VCU118. By default, the tool assigns the targets IP in unity increments from the host IP (which is specified by `vcu118IpHost` in [setupEnv.json](../../besspin/base/utils/setupEnv.json)).

- `customTargetIp`: The target IP to use in case `useCustomTargetIp` is enabled. Please consider the subnet of the host's IP and any additional network configuration that might be needed based on this choice.

---

## [common] ##

This section is loaded in all modes.

- `openConsole`: If suitable to other options/exceptions, instead of terminating the target after performing the configured tasks, the tool returns an console for Unix, or shows the UART output for FreeRTOS while letting it run.

- `gdbDebug`: If `openConsole` is enabled, enable `gdbDebug` so that the tool's GDB process detaches from the OpenOCD connection and provides instructions of how to connect a GDB process to the target. Note that this is not applicable to QEMU targets.

- `useCustomCredentials`: For Unix targets, in case there is a need for creating a non-root user (as in the bug bounty modes for example), which credentials the tool should use? By default, the user name is `researcher` and the password is `besspin_2020`.

- `userName`: The user name in case `useCustomCredentials` is enabled. Note that it must be 1-14 characters long, and may consist only of ASCII alphanumeric characters.

- `userPasswordHash`: The output of `crypt(3)` in SHA-512 of the user password in case `useCustomCredentials` is enabled. You can use `mkpasswd -m sha-512 ${PASSWORD}` on Debian (and other) to generate that.

- `rootUserAccess`: For Unix targets, in case there is a need to create a non-root user (as in the bug bounty modes for example), whether that user should have root access via passwordless `su`.

- `remoteTargetIp`: The IP address on AWS to which to bind the FPGA via a 1:1 NAT. Please refer to [remoteCommunicationWithTarget.md](../AWS/remoteCommunicationWithTarget.md) for more details.

---

## [fett] ##

This section is only loaded in the bug bounty modes (`fettTest` and `fettProduction`). Please refer to [bugBounty2020/README.md](../bugBounty2020/README.md) for details about each parameter. 

---

## [build] ##

This configures the compiler/linker options for any cross-compilation happening, whether it's compiling the FreeRTOS kernel, or a CWE test C file. Not all combinations are allowed and compatible with all settings. The tool issues warning and errors in those cases.

Note that for CWEs, there is a way to customize the compiling beyond this section limitation in some aspects. Please refer to [cwesEvaluation/configuration.md](../cwesEvaluation/configuration.md) for more details.

The two settings are:

- `cross-compiler`: Either GCC or Clang. Both are built in the Nix package manager, and we actually mean the RISC-V 64-bit (multilib) cross-complation.

- `linker`: Either GCC or LLD.

---

## [evaluateSecurityTests] and The Rest ##

This section and all subsequent sections are related to the `evaluateSecurityTests` mode, and are explained in detail in [cwesEvaluation/configuration.md](../cwesEvaluation/configuration.md).
