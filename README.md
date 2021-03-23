# SSITH-FETT-Target #

The core tool of the BESSPIN Framework.

**Disclaimer:** *This is a prototype beta software*, with support
provided to SSITH TA-1 teams.  It does not currently implement all
planned features, and will contain bugs both known and unknown.  If
you encounter a problem or would like to request improvements, please
contact Galois through documented support channels.

## Table of Contents ##

- [Overview](#overview)
- [Software Requirements and Setup](#software-requirements-and-setup)
- [Usage](#usage)
- [Submodules](#submodules)
- [Developer Starter Kit](#developer-starter-kit)

___

## Overview ##

The tool performs a few different *tasks* that all revolve around the same *function*. The motivation behind the core functionality, i.e. the *function*, is to run a *program* on a target-under-test (TUT) in a robust and reproducible manner, where the TUT can be one of different OSes running on one of different processor architectures running on one of different backends.

In particular, the different *tasks* are called *modes*, and their different tool flows are described in details in [modes.md](./docs/base/modes.md). The bug bounty modes have more details in [this directory](./docs/bugBounty2020/), the security evaluation mode is described in details [here](./docs/cwesEvaluation/), and the cyberphysical demonstrator's documentation can be found [here](./docs/cyberPhys).

The different OSes are detailed in [OSes.md](./docs/base/OSes.md), while the different processors are mentioned [here](./docs/base/configuration.md), and the different backends are explained in [targets.md](./docs/base/targets.md).

---

## Software Requirements and Setup

To clone the repo and start `the nix-shell`, please use:

```bash
git clone git@github.com:DARPA-SSITH-Demonstrators/SSITH-FETT-Target.git
cd SSITH-FETT-Target
./utils/init_submodules.sh
nix-shell
```

- The `nix-shell` is the interactive shell for the Nix package manager. Please refer to [nix.md](./docs/base/nix.md) for more setup details. 
- Each backend (target) has different system and setup requirements, these can be found in [targets.md](./docs/base/targets.md).
- Sudo privileges: Some parts of the tool might need sudo privileges, especially for network setup and hardware drivers access. If you do not wish to be attentive to the tool, you may just allow any sudo member to execute a group of commands without password by adding the following to the sudoers file:
```bash
    %sudo ALL=NOPASSWD: /path/to/command [flags], /path/to/another/command [flags]
```

Alternatively, there is a docker container that has the Nix store populated, and is ready to go. The resources needed to build the docker container are currently in [the docker-tools repo](https://gitlab-ext.galois.com/ssith/docker-tools/-/tree/develop/fett_target), but ticket #1046 should fix that by getting the built up to date, and the instructions local to this repo. The docker image is `artifactory.galois.com:5008/fett-target:ci`, and requires Galois artifactory access to fetch. The recommended command to start the image is:
```bash
    sudo docker run -it --privileged=true --network host -v /path/to/SSITH-FETT-Target:/home/besspinuser/SSITH-FETT-Target artifactory.galois.com:5008/fett-target:ci
```

---

## Usage ##

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

Configuration is explained in details in [configuration.md](./docs/base/configuration.md). Although `-cjson` is an alternative option, it is strongly recommended to use an INI file as the document details. The serialized option is specific to the production mode in bug bounty, and is intended to be used automatically by a cloud hook script on a host instantiated by the bug bounty website; more details can be found in [the bug bounty documentation](./docs/bugBounty2020/).

If the tool is executed manually, there is no need to provide an entrypoint (will be assigned `devHost` by default), or a job ID. These are for when the tool is executed in batch test mode and CI.

The debug mode will dramatically increase the size of the log file (`./${workDir}/fett.log` by default), so please use it only if needed.

---

## Submodules ##

The tool has the following submodules:
- [SSITH-FETT-Environment](./SSITH-FETT-Environment): The Nix shell source codes for the required packages and binaries. More details about Nix are in [nix.md](./docs/base/nix.md).
- [SSITH-FETT-Voting](./SSITH-FETT-Voting): As detailed [here](./docs/bugBounty2020/), a voting registration was one of the applications in the attack surface for the Unix targets of the bug bounty. This submodule has documentation, build instructions, source codes, design files, etc.
- [SSITH-FETT-Binaries](./SSITH-FETT-Binaries): This is the Git LFS repo that contains many resources the tool needs for certain configurations, like OS binaries, FPGA bitstreams, AWS AFI IDs, application pre-built binaries, etc.
- [FreeRTOS](./FreeRTOS): The Galois fork of the classic FreeRTOS repo. This is used for building the FreeRTOS binaries since each CWE test and each application needs to be cross-built alongside the FreeRTOS kernel in a single binary. 

---

## Developer Starter Kit ##

- The target classes structure is briefly explained in [targets.md](./docs/base/targets.md). This should be the starting point to add a new OS or a new backend to the tool.
- There are many functions that are used throughout the tool and can help with integration. These functions are defined inside `fett/base/utils/misc.py`. It would be useful to give a look at this file prior to any development work on this codebase. Especially `printAndLog`, `warnAndLog`, `errorAndLog`, `logAndExit`, `getSetting`, `ftOpenFile`, `make`.
- To add a configuration option, you have to update the json dictionary in `fett/base/utils/configData.json`.
- To add/change a system setting, you have to update the json dictionary in `fett/base/utils/setupEnv.json`.
- The directories structure is:
  - `apps`: Bug bounty specific.
  - `base`: The core functionality (ex. target)
  - `cwesEvaluation`: Security evaluation specific.
  - `cyberPhys`: Cyberphysical demonstrator functions.
  - `target`: The backend classes in addition to the start/launch/end functions.
- [modes.md](./docs/base/modes) has some low-level details about how the tool works in different modes. It's definitely a recommended read before development.


