# Configuration of the CWEs Evaluation Mode #

When `mode` is set to `evaluateSecurityTests` in the `functionality` section, the following sections are loaded:    
- `target`: The target's settings as explained in [targets.md](../base/targets.md).
- `common`: The common settings as explained in [configuration.md](../base/configuration.md).
- `build`: The compiler/linker settings as explained in [configuration.md](../base/configuration.md). These could be ignored as explained in the [`customizedCompiling` section](#customize-compiling).
- `evaluateSecurityTests`: The main settings for controlling this mode ([details](#main-mode-settings)).
- `customizedScoring`: Loaded if `useCustomScoring` is enabled ([details](#customize-scoring)).
- `customizedCompiling`: Loaded if `useCustomCompiling` is enabled ([details](#customize-compiling)).
- `${vulClass}`: Each vulnerability class has a section for its specific settings ([details](#vulnerability-classes)).

Additionally, The directory [configSecurityTests](../../configSecurityTests) contains an INI file for each vulnerability class. These control the selective CWEs testing and the self-assessment modes ([details](#vulnerability-classes)). Also, please note that the utility [configCWEs.py](../../utils/configCWEs.py) can be used to manipulate these files in a convenient way. 

Moreover, some of the SSITH TA-1 teams require specific and known compiling and scoring customization. These are briefly summarized at the [end of this document](#ssith-ta-1-teams).


## Main Mode Settings

The parameters of this section are:
  - `vulClasses`: A list of the vunerability classes to be executed, contained by square brackets and comma
    separated. Choose among the [SSITH CWEs list](./ssithCWEsList.md): *bufferErrors, PPAC, resourceManagement, informationLeakage, numericErrors, hardwareSoC, injection*. When a `${vulClass}` is included, its configuration section is loaded as well ([details](#vulnerability-classes )).
  - `useCustomCWEsConfigsPath`: If enabled, then instead of loading --if needed-- the vulnerability classes INI files from [configSecurityTests](../../configSecurityTests), the tool will look for these INI files inside `pathToCustomCWEsConfigs`. We refer to the chosen path for the INI files as `${CWEsConfigs}` from this point onwards.
  - `pathToCustomCWEsConfigs`: The path containing the CWEs config files in case `useCustomCWEsConfigsPath` is enabled.
  - `useCustomScoring`: Configure the scoring methods as instructed by 
    the parameters in the [`customizedScoring` section](#customize-scoring).
  - `useCustomCompiling`: Configure the tests compilation as instructed
    by the parameters in the [`customizedCompiling` section](#customize-compiling).
  - `FreeRTOStimeout`: How long to wait for a FreeRTOS test to terminate before interrupting it and labeling it as timeout.
  - `runUnixMultitaskingTests`: If enabled, the tool will re-run supported test parts in parallel and score them against the sequential test run. It will report a score as the percentage of CWE scores that matched between both runs. You can limit the number of processes spawned by limiting the number of enabled tests or the number of instances per part configured by the value of `instancesPerTestPart`. The multitasking tests only support buffer errors, resource management, information leakage, and numeric errors classes. Please note that this option only affects Unix OSes and is ignored for FreeRTOS.
  - `instancesPerTestPart`: The number of instances of each test part to be spawned as separate processes when running multitasking tests.


## Customize Scoring

The tool has a default scoring mechanism that varies depending on the
class, test, or even the OS on which the test is being run.  
if the `useCustomScoring` setting is switched on, the
`[customizedScoring]` section can be configured to do any of the
following:
- Score based on a certain set of user-defined keywords on
  STDOUT.  Fill `stdoutKeywords` accordingly.
- Score based on a certain set of user-defined keywords on the output
  of GDB (not compatible with QEMU). Fill `gdbKeywords` accordingly.  These can include signals
  such as SIGTRAP or SEGFAULT.
- Score based on a certain set of checkpoints.  These checkpoints could
  be system functions, methods, interrupts, or exceptions.  Fill
  `funcCheckpoints` accordingly. (Please note that more than a single checkpoint might cause issues depending on the platform limitations).
- Score based on the value of a specific memory location.  Use
  `memAddress` to specify the address, and `memResetValue` with a
  reset value that means no-violation, and then `memViolationValues`
  with the list of violating values. `[*]` may be used as the wild value
  for the violation values list, and thus any value not equal to
  `memResetValue` would be considered as a violation detection.
- Score based on a user-defined python module.  This is chosen by
  switching `useCustomFunction` on, and setting `pathToCustomFunction`
  to the python file.  This path will be loaded as a module, then the
  function `main` will be called with two arguments: 1. the list of
  lines from the log files of the test under investigation, 2. the
  python Enum object `SCORES` (defined in [scoreTests.py](../../besspin/cwesEvaluation/scoreTests.py) and explained in [besspinPhilosophy.md](./besspinPhilosophy.md)).


## Customize Compiling

The tool has a default compilation flow that is configured using the 
`compiler` and `linker` options in the `build` section. However, if the
`useCustomCompiling` setting is switched on, the
`customizedCompiling` section can be configured to to do any of the
following:
- Cross-compile using a user-defined Makefile.
This is chosen by switching
  `useCustomMakefile` on, and setting the `pathToCustomMakefile` to
  the user Makefile.
  * The file will be copied into the tests directory, renamed to
    `Makefile`, and run using the default `make`.
  * For Unix, the makefile will be passed the following variables
  `OS_IMAGE` (`Debian` or `FreeBSD`), `TARGET` (`QEMU`, `VCU118`, or `AWSF1`), `COMPILER` (`GCC` or `CLANG`), `LINKER` (`GCC` or `LLD`), `BIN_SOURCE` (with underscores instead of hyphens), and `SOURCE_VARIANT`.
  * For Unix, the output of the Makefile should be binaries with the
    same tests names with the suffix `.riscv`.  For example,
    `test_128.riscv`.
  * For FreeRTOS, the Makefile will be passed the following variables:
    `XLEN` (32 or 64), `PROC_LEVEL` (`p1`, `p2`, or `p3`), `PROC_FLAVOR` (`chisel` or `bluespec`), `PROG=main_besspin`, `USE_CLANG` (`yes` if the compiler is Clang), `SYSROOT_DIR` (if the compiler is Clang), `INC_BESSPIN_TOOL_SUITE=/path/to/tests`,
    `BSP` (the value of `target`), `RAMDISK_NUM_SECTORS`.  
  * For FreeRTOS, the output of the makefile should always be
    `FreeRTOS.elf`, and they should be copied to `$workDir/osImages/`.
  * Note that the information leakage tests require a more involved Makefile. So in case this is really needed to change, please inspect the [information leakage specific Makefile](../../besspin/cwesEvaluation/informationLeakage/Makefile.xcompileDir).
  * Note that the FreeRTOS compiling is quite involved as the tool compiles using the main [Makefile of the Galois demo](../../FreeRTOS/FreeRTOS/Demo/RISC-V_Galois_P1/Makefile) of the classic FreeRTOS fork.
- Use custom Clang binary with an optional custom Clang sysroot. Enable `useCustomClang` and set `pathToCustomClang` to the custom binary path. Similarly, enable `useCustomSysroot` and set `pathToCustomSysroot` to the desired sysroot path.


## Vulnerability Classes 

In each vulnerability class section, two settings can be configured:
  1. `useSelfAssessment`: If enabled, then instead of running tests for this class, the scores will be loaded from the corresponding INI configuration file in `${CWEsConfigs}`. This is useful in calculating the BESSPIN Scale; especially in case of incremental runs. In the `selfAssessment` section in the INI file in `${CWEsConfigs}`, you may assign any values out of *HIGH, MED, LOW, NONE, DETECTED, NA*.
  2. `runAllTests`: Either run all the existing tests for this class, or
    use the customized INI file in `${CWEsConfigs}` to choose which ones to run.
    Please note that you can use the utility [configCWEs.py](../../utils/configCWEs.py)
    to configure the desired INI file in a more convenient way.  This
    utility can be used to enable, disable, or toggle all or selected
    CWE tests. Note that is non-applicable to buffer errors. For `bufferErrors`, customizing which tests to run is done using the custom error model instead. 

The classes buffer errors, resource management, and information leakage require the generation of some random values. Each of those classes have the following options:
  - `useSeed`: Whether to use a specific seed versus a random one.
  - `seed`: The seed for the random generation if `useSeed` is enabled.

The buffer errors class has the following additional parameters:
  - `useCustomErrorModel`: As explained in [constrainBufferErrors.md](./constrainBufferErrors.md), enable this option to use the error model in `pathToCustomErrorModel` rather than the default error model. 
  - `pathToCustomErrorModel`: The path to the error model when `useCustomErrorModel` is enabled.
  - `numericTypes`: List the numeric types the generated tests should use. You may choose `[ints, floats]` or either one of them (within brackets).
  - `nTests`: The number of random tests generated.  Must be at least 40 for FreeRTOS and at least 100 for debian and FreeBSD.
  - `useCachedInstances`: Enable to use a cache of all possible enumerations of the builtin buffer errors model, rather than generating the enumerations from scratch. Enabling this option will save 10's of minutes of runtime of the buffer errors tool with no impact on the tool's randomness.  The only reason to disable this option is if you have modified the builtin error model definition. Disabling this option will re-generate the cache file, allowing you to safely re-enable this option after a single run with a new model definition. Please note that this option only applies to the builtin error model and has no effect if `useCustomErrorModel` is enabled.
  - `nSkip`: Before generating `nTests` tests, generate and throw away `nSkip` tests.
  - `heapSize`: Maximum heap size.
  - `stackSize`: Maximum stack size.
  - `useExtraTests`: Enable to use the C files in `extraSources` as additional tests to run.
  - `csvFile`: tabulates the generated tests info and results in `${workDir}/cwesEvaluation/bufferErrors/bufferErrors.csv`.


## SSITH TA-1 Teams

### Scoring

These are the special known instructions:   
- LMCO P1: Add `exception_handler` to `funcCheckpoints`.
- LMCO P2: Add `Illegal` to `stdoutKeywords`.
- SRI-Cambridge P2: Add `security exception` and `Signal 34` to `stdoutKeywords`.


### Compiling

SRI-Cambridge, LMCO P2, and Michigan targets require the use of non-default toolchains. The use of these toolchains, via Docker images, is integrated in the tool. Currently, the tool assumes that you have the Docker service running and the needed images available. To ensure that on a CentOS machine, please do the following:
  - Install docker ([instructions source](https://docs.docker.com/engine/install/centos/#install-using-the-repository)):
    ```
    sudo yum install -y yum-utils
    sudo yum-config-manager \
        --add-repo \
        https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install docker-ce docker-ce-cli containerd.io
    ```
  - Start the docker service:
    ```
    sudo systemctl start docker
    ```
  - Make the service start on system boot:
    ```
    sudo systemctl enable docker
    ```
  - Download the docker images containing the toolchains:
    ```
    aws s3 cp s3://ta1-toolchain-images/cambridge-toolchain.tar.gz .
    aws s3 cp s3://ta1-toolchain-images/michigan-toolchain.tar.gz .
    ```
  - Load them to docker
    ```
    sudo docker load -i cambridge-toolchain.tar.gz
    sudo docker load -i michigan-toolchain.tar.gz
    ```

- Note that for LMCO P2, the Docker image (`galoisinc/besspin:gfe-gcc83`) is public on DockerHub, so there is no need to load it. However, the first run that uses it will take considerable extra time due to downloading and unpacking.
