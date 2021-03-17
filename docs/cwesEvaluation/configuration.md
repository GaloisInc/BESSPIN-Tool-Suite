# Configuration of the CWEs Evaluation Mode #

*This document is still under construction*

All the needed configuration is done using the main `fett` configuration. When the tool is configured
to run in the `evaluateSecurityTests` mode, the `evaluateSecurityTests` section in the configuration file is loaded. The parameters in this section are:
  - `vulClasses`: A list of the vunerability classes to be executed, contained by square brackets and comma
    separated. Choose among the NIST list: *bufferErrors, PPAC, resourceManagement, informationLeakage, numericErrors*. The names follow [attachment 3 of the
    SSITH BAA](https://www.ntsc.org/assets/uploads/HR001117S0023.pdf). When a `$vulClass` is included, its configuration section is loaded as well. Please note that the classes *codeInjection* and *cryptoErrors* are yet to be implemented.
  - `useCustomCWEsConfigsPath`: If disabled, then the `.ini` files in [./configSecurityTests](./configSecurityTests) will be used by default, which we reference as `${CWEsConfigs}` in the rest of this document.
  - `pathToCustomCWEsConfigs`: The path containing the CWEs config files in case `useCustomCWEsConfigsPath` is enabled.
  - `useCustomScoring`: Configure the scoring methods as instructed in
    the parameters in the `[customizedScoring]` section.  More
    details are in the scoring section in this document.
  - `useCustomCompiling`: Configure the compilation flow as instructed
    in the parameters in the `[customizedCompiling]` section.  More
    details are in the compiling section in this document.
  - `FreeRTOStimeout`: How long to wait for a FreeRTOS non-interactive test to terminate.


Regarding each vulnerability class section, it is worth mentioning that:
  - `useSelfAssessment`: If enabled, then instead of running tests for this class, the scores will be loaded from the `.ini` configuration files in `${CWEsConfigs}`. This is useful in calculating the security figure of merit (TBD), especially in case of incremental runs. 
  - `runAllTests`: Either run all the existing tests to this class, or
    use the customized `${CWEsConfigs}/$vulClass.ini` to choose which ones to run.  Note that
    you can use the utility [configSecurityTests/configCWEs.py](./configSecurityTests/configCWEs.py)
    to configure the desired `$vulClass.ini` automatically.  This
    utility can be used to enable, disable, or toggle all or selected
    CWE tests. Note that is non-applicable to buffer errors. For `bufferErrors`, customizing which tests to run is done using `useCustomErrorModel` instead. More details are provided in [constrainBufferErrors.md](./constrainBufferErrors.md). 
  - `test_<parameterName>`: Any parameter that starts with the prefix
    `test_` is a test related parameter.
  - `randomizeParameters`: If this is enabled, then all the tests
    related parameters values are ignored for this vulnerability
    class, and the tests will use randomized values instead. [Not yet implemented]


## Customize Results Scoring

FETT has a default scoring mechanism that varies depending on the
class, test, or even the OS on which the test is being run.  However,
if the `useCustomScoring` setting is switched on, the
`[customizedScoring]` section can be configured to do any of the
following:
- Score based on a certain set of user-defined keywords on
  STDOUT.  Fill `stdoutKeywords` accordingly.
- Score based on a certain set of user-defined keywords on the output
  of GDB.  Fill `gdbKeywords` accordingly.  These can include signals
  such as SIGTRAP or SEGFAULT.
- Score based on a certain set of checkpoints.  These checkpoints could
  be system functions, methods, interrupts, or exceptions.  Fill
  `funcCheckpoints` accordingly.
- Score based on the value of a specific memory location.  Use
  `memAddress` to specify the address, and `memResetValue` with a
  reset value that mean no-violation, and then `memViolationValues`
  with the list of violating values. `[*]` may used as the wild value
  for the violation values list, and thus any value not equal to
  `memResetValue` would be considered as a violation detection.
- Score based on a user-defined python module.  This is chosen by
  switching `useCustomFunction` on, and setting `pathToCustomFunction`
  to the python file.  This path will be loaded as a module, then the
  function `main` will be called with two arguments: 1. the list of
  lines from the log files of the test under investigation, 2. the
  python Enum object `SCORES`.

## Scoring for non-GFE CPUs

These are the special known instructions:   
- LMCO P1: Add `exception_handler` to `funcCheckpoints`.
- LMCO P2: Add `Illegal` to `stdoutKeywords`.
- SRI-Cambridge P2: Add `security exception` and `Signal 34` to `stdoutKeywords`.

## Customize Tests Compiling

FETT has a default compilation path that is configured using the 
`compiler` and `linker` options in the `[build]` section. However, if the
`useCustomCompiling` setting is switched on, the
`[customizedCompiling]` section can be configured to cross-compile using a user-defined Makefile.
This is chosen by switching
  `useCustomMakefile` on, and setting the `pathToCustomMakefile` to
  the user Makefile.
  * The file will be copied into the tests directory, renamed to
    `Makefile`, and run using the default `make`.
  * For Linux, the makefile will be passed the following variables
  `OS_IMAGE`, `TARGET`, `COMPILER`, `LINKER`, and `BIN_SOURCE`.
  * For Linux, the output of the makefile should be binaries with the
    same tests names with the suffix `.riscv`.  For example,
    `test_307.riscv`.
  * For FreeRTOS, the makefile will be passed the following variables:
    `XLEN`, `PROG=main_fett`, `USE_CLANG`, `INC_FETT_APPS=/path/to/tests`,
    `BSP`, `RAMDISK_NUM_SECTORS`.  
  * For FreeRTOS, the output of the makefile should always be
    `FreeRTOS.elf`, and they should be copied to `$workDir/osImages/`.


## Compiling for non-GFE CPUs

SRI-Cambridge, LMCO P2, and Michigan targets require the use of non-default toolchains. The use of these toolchains, via Docker images, is integrated in the tool. Currently, the tool assumes that you have the Docker service running and the needed images available. To ensure that on a CentOS machine, do the following:
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
