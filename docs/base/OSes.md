# Operating Systems #

In this document, we provide some details about the supported OSes.

---

## Busybox ##

[Busybox](https://busybox.net/downloads/BusyBox.html) combines tiny versions of many common UNIX utilities into a single small executable. It provides minimalist replacements for most of the utilities you usually find in GNU coreutils, util-linux, etc. The utilities in BusyBox generally have fewer options than their full-featured GNU cousins; however, the options that are included provide the expected functionality and behave very much like their GNU counterparts. 

The binaries are built in the Nix package manager. There are two images: `$FETT_GFE_BUSYBOX_VCU118` and `$FETT_GFE_BUSYBOX_QEMU`. 

Because how light it is, Busybox is just used in the tool for smoke testing processors, network, or core target functions. It is not used for running any of the supported modes. It boots, then shuts down right away. 

---

## Debian ##

Debian is built in the Nix package manager. [The images document](../../SSITH-FETT-Environment/IMAGES.md) provides a high-level description of the build steps. The following binaries are provided in the nix-shell:
- `$FETT_GFE_DEBIAN_VCU118`: The baseline Debian image for VCU118.
- `$FETT_GFE_DEBIAN_VCU118_NO_RSYSLOG`: The baseline Debian image for VCU118 with the `rsyslog` service not running. In the `cyberPhys` mode, this service causes problems by consuming all the limited disk space. 
- `$FETT_GFE_DEBIAN_QEMU`: The baseline Debian image for QEMU.
- `$FETT_GFE_DEBIAN_FIRESIM`: The baseline Debian image for Firesim.
- `$FETT_GFE_DEBIAN_ROOTFS_FIRESIM`: The rootfs disk image for Firesim.

---

## FreeBSD ##

FreeBSD is built in the Nix package manager. [The images document](../../SSITH-FETT-Environment/IMAGES.md) provides a high-level description of the build steps. The following binaries are provided in the nix-shell:
- `$FETT_GFE_FREEBSD_VCU118`: The baseline FreeBSD image for VCU118.
- `$FETT_GFE_FREEBSD_QEMU`: The baseline FreeBSD image for QEMU.
- `$FETT_GFE_FREEBSD_DEBUG_VCU118`: The baseline FreeBSD image for VCU118 with kernel debug.
- `$FETT_GFE_FREEBSD_DEBUG_QEMU`: The baseline FreeBSD image for QEMU with kernel debug.
- `$FETT_GFE_FREEBSD_CONNECTAL`: The baseline FreeBSD image for Connectal.
- `$FETT_GFE_FREEBSD_ROOTFS_CONNECTAL`: The rootfs disk image for Connectal.

---

## FreeRTOS ##

FreeRTOS is built through the tool itself. We use the Galois project [Makefile](../../FreeRTOS/FreeRTOS/Demo/RISC-V_Galois_P1/Makefile) with additional `.mk` and additional environment variables during the `make` execution. The building is mainly performed by the `buildFreeRTOS` function in [build.py](../../fett/target/build.py). Also, some additional headers are specifically defined and generated in the tool. 

Unfortunately, building the FreeRTOS is an involved process, and the easiest thing is to just use the tool for it. Some future work will permit the user to write their own C file(s) and provide their `.mk` files and the tool will leverage its capabilities to make it happen. 
