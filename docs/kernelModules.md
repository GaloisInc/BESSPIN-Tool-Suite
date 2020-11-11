# Kernel Modules

## Overview

This document is for dump/design/plan the investigation about designing and building kernel modules that might be needed for some of the CWEs evaluation. So far, the only investigation was done for Debian.

## Linux Debian

### Design Kernel Modules

The following is a simple Hello World module:
```c
#include <linux/module.h>
#include <linux/kernel.h>

MODULE_AUTHOR("BESSPIN");
MODULE_DESCRIPTION("A hello world example Linux kernel module.");

int init_module(void) {
    printk(KERN_INFO "Hello, World!\n");
    return 0;
}

void cleanup_module(void) {
    printk(KERN_INFO "Goodbye, World!\n");
}
```

For example, accessing a CSR value that is not accessible in user mode, but accessible in supervisor mode can be done as follows (where `<REGNAME>` is the register in question):
```c
unsigned long tmp;
asm volatile ("csrr %0, <REGNAME>" : "=r" (tmp));
printk(KERN_INFO "<REGNAME> value = <%lx>\n", tmp);
```

### Debian Image 

The current debian image does not support custom kernel modules. The branch `debian-w-loadable-kmod` has the debian kernel configuration that support it. So make sure your nix-shell builds that image first. The configuration was created by enabling the load and exit for modules using the configuration wizard:
```bash
cd ${GFE}/bootmem/build-linux
make KCONFIG_CONFIG=${SSITH-FETT-Target}/SSITH-FETT-Environment/nix/gfe/debian-linux.config ARCH=riscv menuconfig
```

Note that the image created by that branch does not boot on vcu118 due to rcu stalling. Still not solved yet.


### Building Kernel Module

I managed to compile kernel modules doing the following (in nix-shell):

```bash
cd $WRKDIR
git clone git@gitlab-ext.galois.com:ssith/riscv-linux.git
cd riscv-linux
git checkout 333e6ab0dd399fe5f668ac038a2cebd7be3e25b3
touch .scmversion #This is crucial to avoid the dirty notion that would lead to kernel version mismatch
cp ${SSITH-FETT-Target}/SSITH-FETT-Environment/nix/gfe/debian-linux.config nix-debian.config
make ARCH=riscv CROSS_COMPILE=riscv64-unknown-linux-gnu- KCONFIG_CONFIG=./debian-nix.config modules_prepare

cd $WRKDIR
make V=1 ARCH=riscv CROSS_COMPILE=riscv64-unknown-linux-gnu- KDIR=./riscv-linux
```

The simple makefile is as follows (assuming the kernel module sources are in `$WRKDIR` and have the prefix `km`, and the extension `.c`): 

```make
PWD := $(shell pwd)

TARGETS := $(patsubst %.c, %.ko, $(wildcard km*.c))

all: $(TARGETS)

%.ko: %.c
    make -C $(KDIR) M=$(PWD) obj-m=$(<:.c=.o) modules

clean:
    make -C $(KDIR) M=$(PWD) clean
```