# Building Firesim Binaries on an F1 Instance #

This document details the process of building important Firesim binaries on an
f1 instance.

## Install Build Dependencies ##

Use the following `yum` command to install the necessary build dependencies:

```bash
sudo yum install -y autoconf automake gcc zlib-devel flex bison make sudo wget rpm-build net-tools bc openssl python-devel java-devel gettext ncurses-devel dtc glib2-devel pixman-devel python3-pip python3-devel gmp-devel
```

## Mount Additional Storage ##

The root partition on an f1.2xlarge does not have enough free space to build
the Firesim binaries, so you'll need to format and mount the provided SSD:

```bash
sudo mkfs -t xfs /dev/nvme0n1
sudo mkdir /data
sudo mount /dev/nvme0n1 /data
sudo chown centos /data
```

## Prepare Firesim Repository ##

Clone the firesim repo, and run the included setup script to pull down all
submodules.

```bash
cd /data
git clone --depth=1 https://github.com/firesim/firesim.git
cd firesim
./build-setup.sh --submodules-only
```

The build scripts expect a newer version of `git` than exists on the f1, so
you'll need to remove the `--depth 1` argument to `git submodule` in
`target-design/chipyard/scripts/build-toolchains.sh`.
You can do this with sed:

```bash
sed -i 's/--depth 1//g' target-design/chipyard/scripts/build-toolchains.sh
```

Now you can finish the build setup process with:

```bash
./build-setup.sh --fast
```

This script takes a while to run.
It sets various environmental variables you'll need to build `FireSim-f1` and
`switch0`, and builds the shared object files and kernel modules we require.
Relative to the root of the firesim repo, the outputs will be located:

* `build/nbd.ko`
* `platforms/f1/aws-fpga/sdk/linux_kernel_drivers/xdma/xdma.ko`
* `target-design/chipyard/riscv-tools-install/lib/libdwarf.so.1.0.0`
* `target-design/chipyard/riscv-tools-install/lib/libelf-0.175.so`


## Building FireSim-f1 ##

Before building `FireSim-f1`, you must source `sourceme-f1-manager.sh`.
Part of that script sets up ssh to manage child FireSim instances.
Since we don't care about that, you should remove that portion of the script
before sourcing it.

```bash
echo "" > deploy/ssh-setup.sh
source sourceme-f1-manager.sh
```

Now you can build `FireSim-f1`:

```bash
cd sim
make `pwd`/generated-src/f1/FireSim-FireSimRocketConfig-BaseF1Config/FireSim-f1
```

Relative to the root of the firesim repo, the output binary will be at
`sim/generated-src/f1/FireSim-FireSimRocketConfig-BaseF1Config/FireSim-f1`

## Building switch0 ##

Before you can build `switch0`, you'll need to create
`target-design/switch/switchconfig.h` with the parameters you would like the
switch to have.
Use the following template to create this file:

```C++
// Clients config
#ifdef NUMCLIENTSCONFIG
#define NUMPORTS 0  // Replace with the number of ports you want
#define NUMDOWNLINKS 0  // Replace with the number of downlinks you want
#define NUMUPLINKS 0  // Replace with the number of uplinks you want
#endif  // NUMCLIENTSCONFIG

#ifdef PORTSETUPCONFIG
// Define each uplink and downlink
// ports[<index>] = ShmemPort OR SocketServerPort
#endif // PORTSETUPCONFIG

// MAC to port mapping
#ifdef MACPORTSCONFIG
uint16_t mac2port[/* size */] { /* elements */ };
#endif
```

Once `switchconfig.h` is in place, you can build `switch0`:

```bash
cd target-design/switch
make
mv switch switch0
```

The FireSim build scripts always build `switch` then move it to `switch<N>`, so
this document does the same for completeness.
