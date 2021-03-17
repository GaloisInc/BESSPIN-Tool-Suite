# Security Evaluation Platform #

This is the documentation for running the tool in the `evaluateSecurityTests` mode.

## Overview

A list of the classes in addition to the NIST CWEs mapped to each class are summarized in [ssithCWEsList.md](./ssithCWEsList.md).
A class-specific description is provided in each vulnerability class [directory](../../fett/cwesEvaluation/).

The philosophy of the platform and the methodology of the testing are explained in details in the [BESSPIN philosophy document](./besspinPhilosophy.md).

## Summary of Contents ##

- [BESSPIN-Coeffs.md](./BESSPIN-Coeffs.md) The values of the BESSPIN coefficients. This document is automatically generated based on the values in the [JSON file](../../fett/cwesEvaluation/utils/besspinCoeffs.json). More explanation can be found in the BESSPIN Scale document (next).

- [BESSPIN-Scale.pdf](./BESSPIN-Scale.pdf) White paper explaining the BESSPIN Scale, which is the security figure of merit.

- [BESSPIN-Scale.tex](./BESSPIN-Scale.tex) The LaTex source of the BESSPIN-Scale pdf which gets compiled on [Overleaf](https://www.overleaf.com/). Please note that we use this unfortunately incompatible `git` format for the sake of displaying the mathematical formulas in a more readable way.

- [besspinPhilosophy.md](./besspinPhilosophy.md) As explained above, this explains the philosophy of the platform and the methodology of the testing.

- [configuration.md](./configuration.md) Detailed documentation of all the configuration options related to this mode of operation.

- [constrainBufferErrors.md](./constrainBufferErrors.md) Detailed explanation of the use of the configuration options concerning the use of a custom error model for buffer errors tests.

- [kernelModules.md](./constrainBufferErrors.md) How to cross-compile a kernel module for RISC-V Linux Debian. This flow has not been integrated with the tool, and there is no plan for doing that soon.

- [ssithCWEsList.md](./ssithCWEsList.md) The full list of the CWEs and vulnerability classes supported by the SSITH program and the BESSPIN tool. This document is automatically generated based on a DARPA spreadsheet, and is compared against the various tool's parts using the [ssithCWEsList.py](../../utils/ssithCWEsList.py) utility.

## Tool's Mode of Operation ##

When the tool is configured to run in the `evaluateSecurityTests` mode, it runs the CWEs tests on the selected target/OS configuration. This also loads the configuration of the `evaluateSecurityTests` section, and optionally other sections. The configuration details are provided in [configuration.md](./configuration.md).

*Here summarize what the tool will do*

## Example ##

*Run example with screenshots*




