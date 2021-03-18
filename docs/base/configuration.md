# Configuration #

The needed configuration is done using [INI
file](https://en.wikipedia.org/wiki/INI_file) configuration. The
default file is [config.ini](../../config.ini).

## Overview ##

[config.ini](./config.ini) is commented with brief descriptions of
the meaning of every parameter and the possible values/types. Please note the following:
  - Keep the comments on separate lines from values. Order of
    parameters does not matter.
  - Section headers are required and they are between square brackets.
  - Parameters names and string values are treated as case sensitive. The only exception is boolean parameters; you can use 0/1, False/True, Yes/No [all case insensitive].

The configuration(s) is loaded in [config.py](../../fett/base/config.py) and the dictionary of the sections, parameter names, supported data types, value ranges and choices, and conditions are listed in [configData.json](../../fett/base/utils/configData.json).

This document has explanations for each parameter, either by defining them or linking to the document that has the definitions.

## Functionality ##

The tool's functionality has a single parameter: `mode`. The document [modes.md](./modes.md) explains each mode, and links to all other documentation and resources about each of them.

## cyberPhys ##

This section is only loaded in the `cyberPhys` mode. Please refer to [cyberPhys/configuration.md](../cyberPhys/configuration.md) for details about each parameter. 

## target ##

This section determines the backend details of the tool's run. In `cyberPhys` mode, this section is not loaded from the main configuration INI file, but a separate `target` section per target is loaded from the additional `cyberPhys` INI file. Please refer to [cyberPhys/configuration.md](../cyberPhys/configuration.md) for more details.

The document [targets.md](./targets.md) has detailed explanation of the supported targets, their required setup, and the assumptions the tool makes. We explain the parameters here though:

- `binarySource`: The SSITH program has several TA-1 teams; each of which has their own processor design. The differences between these processors are the sources of many operational corner cases and exceptions. These exceptions are spread out all over the tool. We only support the following options for `binarySource`:
  - `GFE`: The government furnished equipment (GFE) is the baseline (Vanilla) implementation of the processors of the program. This is the safest choice for the use of a processor that does not belong to the other teams, and activates the least amount of exceptions.
  - `LMCO`: Lockheed Martin Corporation.
  - `Michigan`: University of Michigan.
  - `MIT`: Massachusetts Institute of Technology.
  - `SRI-Cambridge`: The CHERI work by Stanford Research Institute and University of Cambridge.

- `sourceVariant`: We introduced this parameter to distinguish between the different *flavors* of the CHERI processors, but it seems a solid parameter to have for future compatibilities as it provides a flexible distinction between processors if they came from the same team and flavor/level (coming up). Currently, this is only compatible with the `SRI-Cambridge` choice for `binarySource`. The acceptable values are `default`, `purecap`, and `temporal`. Please refer to the [CHERI wesbite](https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/) for more details. 

- `target`: The backend of the target. The tool supports `qemu`, `vcu118`, and `awsf1`. The document [targets.md](./targets.md) has more details.

- `vcu118Mode`: Applicable iff the target is set to `vcu118`. Whether to choose the `nonPersistent` memory for programming the bitstream and loading the FPGA, or use the flash. `flashProgramAndBoot` is for initializing the FPGA, so the tool will program the flash first, then boot from it. Please note that this step would require the power recycling of the VCU118 board after programming and before booting. The last option, `flashBoot` is for booting directly from the FPGA flash memory. This assumes that the FPGA was programmed with the correct bitstream and operating system binary. If you need to change either, please use `flashProgramAndBoot` for your changes to take effect on the hardware.
