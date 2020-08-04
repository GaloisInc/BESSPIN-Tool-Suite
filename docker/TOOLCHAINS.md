# Toolchain Docker images

## Vanilla GFE

This image, available on Docker Hub as `galoisinc/besspin:gfe`,
contains the standard GCC and LLVM toolchains for RISC-V
processors. Programs in each GCC toolchain are prefixed with the name
of their target. The targets are:
- `riscv64-unknown-elf`
- `riscv64-unknown-linux-gnu`
- `riscv64-unknown-freebsd12.1`

The `riscv64-unknown-elf` target is for binaries running on bare
metal. Binaries compiled for this target will not run on Debian or
FreeBSD.

If you are using Clang, you will need to use the `--sysroot` flag to
specify the location of the headers and libraries for your target
platform. The sysroot locations on the GFE image are:
- `/opt/riscv-llvm/riscv32-unknown-elf` for 32-bit bare metal targets
- `/opt/riscv-llvm/riscv64-unknown-elf` for 64-bit bare metal targets
- `/opt/riscv-freebsd/sysroot` for FreeBSD targets
- `/opt/riscv/sysroot` for Linux targets

When using Clang and LLD, it is necessary to use the `-mno-relax`
flag, as LLD does not support linker relaxation for RISC-V targets.

# SRI/Cambridge (CHERI)

The CHERI RISC-V processors have their own LLVM toolchain. This is
included in the image along with versions of GDB and QEMU that work
with CHERI processors. A CheriBSD sysroot can be found at
`/opt/cheri/sdk/sysroot`.

Here is an example of compiling a simple C program with the CHERI
toolchain:
```
clang -target riscv64-unknown-freebsd13.0 --sysroot /opt/cheri/sdk/sysroot \
    -march=rv64imafdcxcheri -mabi=l64pc128d -mno-relax -fuse-ld=lld \
    -o prog prog.c
```

If you want to run CheriBSD in QEMU, `/opt/cheri` contains a kernel
and a compressed disk image.
```
zstd -d /opt/cheri/disk-image-cheri.img.zst

qemu-system-riscv64cheri -machine virt -m 2048M -nographic \
    -kernel /opt/cheri/kernel-cheri.elf -bios /opt/cheri/sdk/bbl/riscv64-purecap/bbl \
    -drive file=/opt/cheri/disk-image-cheri.img,format=raw,id=hd0 \
    -device virtio-blk-device,drive=hd0
```

Consult the [CHERI C/C++ Programming
Guide](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-947.pdf) for
more information.

# University of Michigan (Morpheus)

Instructions on how to use the Morpheus toolchain can be found on the
image in `/opt/morpheus/README`. The FreeRTOS demo source can be found
in `/opt/morpheus/FreeRTOS-10.0.1/FreeRTOS/Demo/RISC-V_Galois_P1`.
