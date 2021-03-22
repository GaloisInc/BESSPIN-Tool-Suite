# Targets/Backends #

In this document, we explain in more details the different supported targets/backends and their setup requirements.

## Implementation ##

The target base class is `commonTarget` and is defined in [common.py](../../fett/target/common.py). This class implements the methods that are shared among all types of backends, and depends on defining the lower level methods in backend-specific classes. There is also an `fpgaTarget` class (defined in [fpga.py](../../fett/target/fpga.py)) that has the methods related to having an FPGA, like openining an OpenOCD connection, and starting a GDB process. 

For any target choice, which are `vcu118`, `qemu`, `awsf1`, there is a class that defines the lowest level methods. The `vcu118Target` class, for instance, inherits both `fpgaTarget` and `commonTaret`. While `qemuTarget` only inherits `commonTarget`.


## QEMU ##

The Nix shell has an installed `qemu-system-riscv64` and the tool uses it to start a Qemu process and interacts with it using `pexpect`. There are no special setup requirements for Qemu, except for having enough memory to start it.

For Unix OSes, we need to have a network access to the Qemu target. The tool creates a tap adaptor, and adds a virtual network device to the Qemu. This requires sudo privileges. Please note that ticket #975 is a feature request for adding a setting to the tool that chooses to use TCP forwarding instead of a TAP adaptor, which would remove the sudo requirement for some modes.

It is worth mentioning that currently, the tool's default FreeBSD does not have an entropy source. Ticket #333 is open to resolve this. On the other hand, Debian seems to use `virtio-rng-device` properly without any extra setup.

## AWSF1 ##

### Setup ###

An AMI is built to run the tool on a F1 instance. It hosts an environment that combines the requirements for running the tool. The most recent AMI is referenced ID is in the newest release tag.

The image is based on the `FPGA Developer AMI - 1.6.0-40257ab5-6688-4c95-97d1-e251a40fd1fc-ami-0b1edf08d56c2da5c.4 (ami-02b792770bf83b668)` AMI. It runs CentOS 7. We add to it:

* An updated version of Git, required by the nix shell installation
* Git LFS, needed by the binaries repo.
* [The Nix Package Manager](https://nixos.org/nix/)
* [SSITH-FETT-Environment](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Environment) with the environment pre-populated at `/nix/store`
* [Cloudwatch](https://aws.amazon.com/cloudwatch/)

The document [createFettAMI.md](../docs/AWS/createFettAMI.md) has the complete instructions to recreate the image manually.

### Sources ###

We use the term *CloudGFE* to denote the AWS EC2 F1 FPGA programmed with a SSITH processor, in addition to its peripherals including a UART interface, an Ethernet adaptor, and a filesystem. 

AWS F1's primary application is enabling FPGA acceleration for computations running on the AWS cloud; it is *not* geared towards simulating entire computing systems on FPGA. Consequently, the main challenge in porting the GFE SoC to the cloud lies in adapting it to use the peripherals provided within the AWS infrastructure. While the VCU118 board has all the needed peripheral hardware components already on board and connected to the FPGA in standard ways, the interface to the F1 FPGAs is completely virtualized through a PCIe fabric. The CloudGFE is thus a mixture of real hardware and emulated components.

In particular, five main peripherals were needed: a UART, an Ethernet adaptor, a filesystem, a random number generator, and a debugger interface (which was essential to facilitate the design through virtualization). 

Additionally, since the SSITH program has several hardware designs, a one-size-fits-all approach was impractical given time constraints. Therefore, we designed two separate approaches for the two flavors of CPUs in the program. The first is based on the [Berkeley FireSim hardware simulation framework](https://fires.im/), where the peripherals are emulated partly on the host side and partly on the target side. Specifically, the processor interacts through PCIe using a special type of message passing. On the target side, there are components that translate the drivers' data and these messages. On the host side, the FireSim binaries do the same for the host drivers. The second approach uses the [Connectal framework](https://www.connectal.org/) in combination with the exclusive use of Virtio, where the entirety of the peripheral emulation is done in software.

### Usage ###

- Firesim:
  - The files needed are the kernel modules `nbd.ko` and `xdma.ko`, the main firesim binary `FireSim-f1`, the network switch binary `witch0`, and the libraries `libdwarf.so.1` and `libelf.so.1`. The document [buildFireSimBinaries.md](../AWS/buildFireSimBinaries.md) has the instructions of how to build these files.
  - The processor design has to be used to produce/synthesize the AWS bitstream, the AFI.
  - The tool starts with gathering these files and info, then prepares the disk image, clears the shared memory, removes and re-installs the kernel related modules, configure the tap adaptor and iptables, then flashes the FPGA with the AFI.

- Connectal:
  - The files needed are are the kernel modules `pcieportal.ko` and `portalmem.ko`, and the main connectal binary `ssith_aws_fpga`. The document [buildConnectalBinaries.md](../AWS/buildConnectalBinaries.md) has the instructions of how to build these files. 
  - The processor design has to be used to produce/synthesize the AWS bitstream, the AFI.
  - The tool starts with gathering these files and info, then prepares the disk image, configures the tap adaptor and iptables, removes the kernel modules, flashes the FPGA with the AFI, then removes and re-installs the kernel modules.

