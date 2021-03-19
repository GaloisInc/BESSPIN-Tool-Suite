# Targets/Backends #

In this document, we explain in more details the different supported targets/backends and their setup requirements.

## Implementation ##

The target base class is `commonTarget` and is defined in [common.py](../../fett/target/common.py). This class implements the methods that are shared among all types of backends, and depends on defining the lower level methods in backend-specific classes. There is also an `fpgaTarget` class (defined in [fpga.py](../../fett/target/fpga.py)) that has the methods related to having an FPGA, like openining an OpenOCD connection, and starting a GDB process. 

For any target choice, which are `vcu118`, `qemu`, `awsf1`, there is a class that defines the lowest level methods. The `vcu118Target` class, for instance, inherits both `fpgaTarget` and `commonTaret`. While `qemuTarget` only inherits `commonTarget`.


## QEMU ##

The Nix shell has an installed `qemu-system-riscv64` and the tool uses it to start a Qemu process and interacts with it using `pexpect`. There are no special setup requirements for Qemu, except for having enough memory to start it.

For Unix OSes, we need to have a network access to the Qemu target. The tool creates a tap adaptor, and adds a virtual network device to the Qemu. This requires sudo privileges. Please note that ticket #975 is a feature request for adding a setting to the tool that chooses to use TCP forwarding instead of a TAP adaptor, which would remove the sudo requirement for some modes.

## AWSF1 ##

An AMI is built to run the tool on a F1 instance. It hosts an environment that combines the requirements for running the tool. The most recent AMI is referenced ID is in the newest release tag.

The image is based on the `FPGA Developer AMI - 1.6.0-40257ab5-6688-4c95-97d1-e251a40fd1fc-ami-0b1edf08d56c2da5c.4 (ami-02b792770bf83b668)` AMI. It runs CentOS 7. We add to it:

* An updated version of Git, required by the nix shell installation
* Git LFS, needed by the binaries repo.
* [The Nix Package Manager](https://nixos.org/nix/)
* [SSITH-FETT-Environment](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Environment) with the environment pre-populated at `/nix/store`
* [Cloudwatch](https://aws.amazon.com/cloudwatch/)

The document [createFettAMI.md](../docs/AWS/createFettAMI.md) has the complete instructions to recreate the image manually.

*SPEAK ABOUT CLOUD GFE*


