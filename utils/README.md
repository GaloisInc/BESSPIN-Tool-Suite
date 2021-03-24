# Out-of-Package Utilities #

This directory includes standalone utilities that are not part of the tool:

- [besspinCoeffsList.py](./besspinCoeffsList.py): Related to the BESSPIN Scale calculation. This utility checks the completeness of the BESSPIN coefficients JSON file, and generates the document [BESSPIN-Coeffs.md](../docs/cwesEvaluation/BESSPIN-Coeffs.md). Please refer to [BESSPIN-Scale.pdf](../docs/cwesEvaluation/BESSPIN-Scale.pdf) and [CWEs evaluation readme](../docs/cwesEvaluation/README.md) for more details.

- [clearFiresimProcesses.sh](./clearFiresimProcesses.sh): Kills all processes related to Firesim and clears the shared memory (used by Firesim). This comes handy during manual development and debugging.

- [clearNetworkSetup.sh](./clearNetworkSetup.sh): Clears/resets the network configuration performed by the tool. For AWS, it deletes the `tap` adaptor, the production IP, and flushes the iptables. For qemu, it flushes the iptables and deletes any leftover tap adaptors.

- [configCWEs.py](./configCWEs.py): Enables/disables/toggles a particular(all) CWE(s) in a specific INI file in vulnerability classes INI files. Please refer to [configuration.md](../docs/cwesEvaluation/configuration.md) for more details. 

- [fetchProdLogs.py](./fetchProdLogs.py): Selectively downloads the FETT bug bounty production logs and artifacts. Please use `./fetchProdLogs.py -h` for a detailed usage.

- [init_submodules.sh](./init_submodules.sh): Initializes and fetches the submodules recursively.

- [loadFreertosDiskImage.sh](./loadFreertosDiskImage.sh): Loads and mounts the FreeRTOS disk image in `workDir` to `/loopfs`.

- [ssithCWEsList.py](./ssithCWEsList.py): This verifies that all moving parts containing the SSITH CWEs list are synchronized, so it requires the `csv` of the internal CWEs spreadsheet. Also, it generates the final document [ssithCWEsList.md ](../docs/cwesEvaluation/ssithCWEsList.md )

- [unloadFreertosDiskImage.sh](./unloadFreertosDiskImage.sh): Unmounts and unloads what `loadFreertosDiskImage.sh` has done.

- [vulClassScore.py](./vulClassScore.py): Runs the BESSPIN scoring functions of the tool. This assumes that the tests log files are already existent in the working directory. This is mostly a debugging utility.
