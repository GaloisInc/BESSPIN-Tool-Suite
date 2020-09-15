# SSITH-FETT-Target
The target platform for the SSITH FETT bug bounty exercise.


## Software Requirements and Setup

To clone the repo and start `the nix-shell`, please use:

```bash
git clone git@github.com:DARPA-SSITH-Demonstrators/SSITH-FETT-Target.git
cd SSITH-FETT-Target
./init_submodules.sh
nix-shell
```

* For `nix-shell` issues, please check the instructions in [SSITH-FETT-Environment](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Environment).   

* Regarding local `fpga` target:   
    1. A GFE SoC on a Xilinx VCU118 FPGA should be accessible, in
  addition to executing all the [GFE setup instructions](https://gitlab-ext.galois.com/ssith/gfe/tree/develop).   
    2. Note that the name of the ethernet adaptor connected to the VCU118 might change from a system to
      another. Please review the [FPGA host network configuration setup
      instructions](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Docs/blob/develop/CI-CD/HostNetworkSetup.md)
      for more details about the adaptors and IP settings. In case you
      intend to use a different setup, please change
      [setupEnv.json](fett/base/utils/setupEnv.json) accordingly.

* Sudo privileges:
  - Note that some parts of the tool might need sudo privileges, especially for network setup. If you do not wish to be attentive to the tool, you may just allow any sudo member to execute a group of commands without password by adding the following to the sudoers file:
  ```bash
    %sudo ALL=NOPASSWD: <path>/ip, <path>/sysctl, <path>/iptables, <path>/pkill, <path>/kill
  ```

### AWS Setup

To utilize its FireSim and Connectal integration, an AMI was made to run the FETT Target on a F1 instance. It hosts an environment that combines the requirements of the FireSim, Connectal, and FETT projects. The most recent AMI is referenced ID is in the newest release tag.

#### Contents

The image is based on the `FPGA Developer AMI - 1.6.0-40257ab5-6688-4c95-97d1-e251a40fd1fc-ami-0b1edf08d56c2da5c.4 (ami-02b792770bf83b668)` AMI. It runs CentOS 7 and is the AMI used for Firesim. It adds

* An updated version of Git, required by the FETT Environment nix shell installation
* Git LFS, needed by FETT Binaries
* [The Nix Package Manager](https://nixos.org/nix/)
* [SSITH-FETT-Environment](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Environment) with the environment pre-populated at `/nix/store`
* [Cloudwatch](https://aws.amazon.com/cloudwatch/)

After launching, it is necessary to setup the git `name` and `email`, as well as register SSH keys with github and gitlab accounts that have the correct access.

See the instructions in [docs/createFettAMI.md](./docs/createFettAMI.md) to recreate the image manually.


## User Manual ##

To run the tool, use the following:
```
usage: fett.py [-h] [-c CONFIGFILE | -cjson CONFIGFILESERIALIZED]
               [-w WORKINGDIRECTORY] [-l LOGFILE] [-d]
               [-ep {devHost,ciOnPrem,ciAWS,awsProd,awsDev}] [-job JOBID]

FETT (Finding Exploits to Thwart Tampering)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGFILE, --configFile CONFIGFILE
                        Overwrites the default config file: ./config.ini
  -cjson CONFIGFILESERIALIZED, --configFileSerialized CONFIGFILESERIALIZED
                        Overwrites and augments the default production
                        settings
  -w WORKINGDIRECTORY, --workingDirectory WORKINGDIRECTORY
                        Overwrites the default working directory: ./workDir/
  -l LOGFILE, --logFile LOGFILE
                        Overwrites the default logFile: ./${workDir}/fett.log
  -d, --debug           Enable debugging mode.
  -ep {devHost,ciOnPrem,ciAWS,awsProd,awsDev}, --entrypoint {devHost,ciOnPrem,ciAWS,awsProd,awsDev}
                        The entrypoint
  -job JOBID, --jobId JOBID
                        The job ID in production mode.
```

All the needed configuration is done using the main [INI
file](https://en.wikipedia.org/wiki/INI_file) configuration.  The
default file is [config.ini](./config.ini).

[config.ini](./config.ini) is heavily commented with descriptions of
the meaning of every parameter.  Please note that:
  - Keep the comments on separate lines from values.  Order of
    parameters does not matter.
  - Section headers are required (Between square brackets).  The
    `[backend]` is the top-level section to configure the main
    options. 
  - Parameters names are case sensitive.
  - For boolean parameters, you can use 0/1, False/True, Yes/No [all
  case insensitive].

Some useful configuration options:
- `mode`: Choose either `test` for the testing flow, or `production` for leaving the apps switched on for researchers interactions, or `evaluateSecurityTests` for the BESSPIN CWEs evaluation tests.
- `binarySource`: Choose the team's binary srouces from `['GFE', 'LMCO', 'Michigan', 'MIT', or 'SRI-Cambridge']`.
- `target`: Choose either `aws` for the main FETT target, `fpga` for Xilinx VCU118 hardware
    emulation, or `qemu` for [QEMU](https://www.qemu.org/) emulation.
- `processor`: One of the GFE processors or the TA-1 teams processors.
- `osImage`: The operating system on which the tests will run.  The
    SSITH OSs are either [FreeRTOS](https://www.freertos.org/),
    [FreeBSD](https://www.freebsd.org/), or [Linux Debian](https://www.debian.org/),
    or [Busybox](https://busybox.net/about.html).
- `useCustomOsImage`: If disabled, Nix (if image is available) or FETT-Binaries images will be used.
- `useCustomProcessor`: If disabled, Nix (if applicable) or FETT-Binaries bitfiles will be used. If enabled, a source directory has to be provided where the required files exist.
- `openConsole`: returns an open console for Unix targets.
- `buildApps`: Cross-compile as instructed in `fett/apps/build.py`.
hello
Note that the AWS platform variant is determined based on the `binarySource`-`processor`-`osImage` choice. More information about these decisions can be found in [the cloudGFE TA-1 and GFE tracker spreadsheet](https://docs.google.com/spreadsheets/d/1J8MSDQS1X0V-wPHiNdCTgu7Pwf8GcgTy91kcn8u9mt0/edit#gid=0).


## Developer Manual ##

- To control which files to be transferred to target, edit the corresponding function inside `fett/apps/build.py`. You'd have to tar the files into a tar file named `os.path.join(getSetting('buildDir'),getSetting('tarballName'))`, and enable the setting for sending the files: `setSetting('sendTarballToTarget',True)`.
- To execute, modify the function `runApp` inside `fett/apps/<appName>/run.py` to do whatever you want. 
- The most important functions provided inside the `target` object which will be given by default to `runApp()`, is `runCommand`, `switchUser`, and `openSshConn` (all of which are defined inside `fett/target/common.py`.
- There are other functions that can help you while coding whether the build or the execute functions for your experiments. These functions are defined inside `fett/base/utils/misc.py`:
    - `printAndLog(message, doPrint=True)`
    - `warnAndLog(message, doPrint=True, exc=None)`
    - `errorAndLog(message, doPrint=True, exc=None)`
    - `logAndExit(message, exc=None, exitCode=EXIT.Unspecified)`
    - exitCodes are define in the object `EXIT`.
    - `getSetting(setting)`: returns the value of `setting`.
    - `setSetting(setting,val)`: sets the value of `setting`.
    - `isEnabled(setting)`: returns the value of a boolean `setting`.
    - `isEqSetting(setting,val)`: returns True if the setting's value is equal to `val`.
    - `getSettingDict(setting,hierarchy)`: parses a setupEnv dictionary and returns the value.
    - `mkdir(dirPath,addToSettings=None)`: makes a directory `dirPath`. If `addToSettings=STR`, then a setting called STR will be created and equal to this path.
    - `cp(src,dest,pattern=None)`: copy (only files for now). If the `pattern=*.c` for example, it will expand the pattern before copying.
    - `tar(tarFileName, filesList=[])`: Create a tar archive of the files in `filesList`. `filesList` is a list of either:
      (1) file names, to be copied to the tar archive as-is. (2) `(dest name, file name)` pairs, i.e. `file name` will be copied to the archive as `dest name`. Useful for copying files from deeply nested trees.
    - `renameFile(src,dest)`: To rename files.
    - `copyDir(src,dest,renameDest=False,copyContents=False)`: Copy directory `src` to `dest`. If `renameDest` is enabled, the `src` becomes `dest` instead of its child. If `copyContents` is enabled, the `src` contents are copied to `dest`.
    - `make(argsList,dirPath)`: makes a makefile inside dirPath. The `-C` flag is added in the function, you add any other flags to make.
    - `ftOpenFile(filePath,mode)`: safely opens a file, and stores its handle in the trash can. You should still close it cleanly, but if the error handling is complicated, then don't worry about it, everything in the trash can object will be destroyed upon exit.
    - `ftReadLines (filePath)`: Returns the contents in `filePath` as a list of strings
    - `matchExprInLines (expr,lines)`: If you pass a regex `expr` and a list of strings, it returns the matched string.

- To add a configuration option, you have to update the json dictionary in `fett/base/utils/configData.json`.
- To add/change a system setting, you have to update the json dictionary in `fett/base/utils/setupEnv.json`.


## CWE Evaluation Mode (Testgen) ##

Instructions for running the FETT tool in CWE evaluation mode can be found here: [docs/evaluateSecurityTestsMode.md](docs/evaluateSecurityTestsMode.md).
