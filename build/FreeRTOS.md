# Building FreeRTOS OTA application

## Building
1. In order to build FreeRTOS FETT application, make sure that your `config.ini` is configured for building FreeRTOS, and that `buildApps` is enabled:
    ```
    buildApps = yes
    ```
2. Run:
    ```
    ./fett.py -c config.ini
    ```
3. Wait untill you see `(Info)~  Files cross-compiled successfully.` in the output, then you can interrupt the FETT execution:
    ```
    $ ./fett.py -c config.ini 
    (Info)~  Welcome to FETT!
    (Info)~  Configuration loaded successfully.
    (Info)~  Preparing the environment...
    (Info)~  Cross-compiling...
    (Info)~  Files cross-compiled successfully.
    CTRL+C
    (Info)~  End of FETT! [Exit code 10:Interrupted]
    ```
4. The resulting binary is in `workDir/osImages`
5. Header and source files are copied in `workDir/build`
5. If you want to test the binary, don't interrupt FETT and wait for it to run the full cycle (the target platform depends on your `config.ini` file)

## Customization

What FETT-target is doing behind the scenes, is that it generates some header files and a makefile and places them into the `workDir/build` folder.
Then it compiles `main_fett` target, including these generated files. To reproduce the compilation, do:

1. `cd FreeRTOS/FreeRTOS/Demo/RISC-V_Galois_P1`
2. `PROG=main_fett INC_FETT_APPS=../../../../workDir/build/ XLEN=32 BSP=aws make clean`
3. `PROG=main_fett INC_FETT_APPS=../../../../workDir/build/ XLEN=32 BSP=aws make`

If you need to modify the application, the easiest is to copy the contents of `workDir/build`, and modify them accordingly. In your `FreeRTOS` folder, then call `make` with `PROG=main_fett` and set `INC_FETT_APPS` to point to your modified FETT application files (copied from `workDir/build`).
Use other compilation flags (`USE_CLANG` etc.) as needed.

Once you are happy with your resulting binary, modify your `config.ini` file so `pathToCustomImage` points to your binary, set `buildApps = no`, and run `fett.py -c config.ini` to run a full test. Once you are done testing, commit your binary to `SSITH-FETT-Binaries`

**NOTE:** `workDir` is cleaned at the beginning of each run of the FETT tool, so make sure you copy your files and binaries elsewhere. 

## FreeRTOS versions

The FETT bug bounty in the summer of 2020 was using FreeRTOS-10.0.1 in order to include some known vulnerabilities in the FreeRTOS kernel and network stack. However, the current tool version uses a more recent FreeRTOS version. In order to build a binary identical to the one used in the bug bounty, please use an older release of the tool.