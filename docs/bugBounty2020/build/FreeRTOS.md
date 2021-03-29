# Building FreeRTOS OTA application

## Building
1. In order to build FreeRTOS BESSPIN application, make sure that your `config.ini` is configured for building FreeRTOS, and that `buildApps` is enabled:
    ```
    buildApps = yes
    ```
2. Run:
    ```
    ./besspin.py -c config.ini
    ```
3. Wait untill you see `(Info)~  Files cross-compiled successfully.` in the output, then you can interrupt the BESSPIN execution:
    ```
    $ ./besspin.py -c config.ini 
    (Info)~  Welcome to BESSPIN!
    (Info)~  Configuration loaded successfully.
    (Info)~  Preparing the environment...
    (Info)~  Cross-compiling...
    (Info)~  Files cross-compiled successfully.
    CTRL+C
    (Info)~  End of BESSPIN! [Exit code 10:Interrupted]
    ```
4. The resulting binary is in `workDir/osImages`
5. Header and source files are copied in `workDir/build`
5. If you want to test the binary, don't interrupt BESSPIN and wait for it to run the full cycle (the target platform depends on your `config.ini` file)

## Customization

What BESSPIN-target is doing behind the scenes, is that it generates some header files and a makefile and places them into the `workDir/build` folder.
Then it compiles `main_besspin` target, including these generated files. To reproduce the compilation, do:

1. `cd FreeRTOS/FreeRTOS/Demo/RISC-V_Galois_P1`
2. `PROG=main_besspin INC_BESSPIN_TOOL_SUITE=../../../../workDir/build/ XLEN=32 BSP=aws make clean`
3. `PROG=main_besspin INC_BESSPIN_TOOL_SUITE=../../../../workDir/build/ XLEN=32 BSP=aws make`

If you need to modify the application, the easiest is to copy the contents of `workDir/build`, and modify them accordingly. In your `FreeRTOS` folder, then call `make` with `PROG=main_besspin` and set `INC_BESSPIN_TOOL_SUITE` to point to your modified BESSPIN application files (copied from `workDir/build`).
Use other compilation flags (`USE_CLANG` etc.) as needed.

Once you are happy with your resulting binary, modify your `config.ini` file so `pathToCustomImage` points to your binary, set `buildApps = no`, and run `besspin.py -c config.ini` to run a full test. Once you are done testing, commit your binary to `BESSPIN-LFS`

**NOTE:** `workDir` is cleaned at the beginning of each run of the BESSPIN tool, so make sure you copy your files and binaries elsewhere. 

## FreeRTOS versions

The FETT bug bounty in the summer of 2020 was using FreeRTOS-10.0.1 in order to include some known vulnerabilities in the FreeRTOS kernel and network stack. However, the current tool version uses a more recent FreeRTOS version. In order to build a binary identical to the one used in the bug bounty, please use an older release of the tool. In particular, [V3.13](https://github.com/GaloisInc/BESSPIN-Tool-Suite/releases/tag/v3.13-ami-0c7a133b9c07d8682) was the last one used in the bug bounty, and [V4.1](https://github.com/GaloisInc/BESSPIN-Tool-Suite/releases/tag/v4.1-ami-01da26a5a7972c4b8) is the last version that uses FreeRTOS-10.0.1 for the binaries builds.