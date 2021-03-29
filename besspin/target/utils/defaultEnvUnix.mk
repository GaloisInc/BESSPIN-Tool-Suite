# This file has the necessary includes to cross-compile files for Unix

ifeq ($(BIN_SOURCE),SRI_Cambridge)
	ARCH_ABI := -march=rv64imafdcxcheri -mabi=l64pc128d
else
	ARCH_ABI := -march=rv64imafdc -mabi=lp64d
endif
BESSPIN_DEFS += -DtestgenOnUnix -DtestgenOn$(OS_IMAGE)
ifeq ($(TARGET),QEMU)
	BESSPIN_DEFS += -DtestgenQEMU
else
	BESSPIN_DEFS += -DtestgenFPGA -Dtestgen$(TARGET)
endif

CFLAGS := $(ARCH_ABI) -Wall -O0 $(BESSPIN_DEFS)

ifeq ($(BIN_SOURCE),SRI_Cambridge)
	PREFIX_FreeBSD := riscv64-unknown-freebsd13.0
else
	PREFIX_FreeBSD := riscv64-unknown-freebsd12.1
endif
ifeq ($(BIN_SOURCE),LMCO)
	#In the docker image, this is v8.3.0
	PREFIX_Debian := riscv64-unknown-elf
else
	PREFIX_Debian := riscv64-unknown-linux-gnu
endif
CFLAGS_FreeBSD_CLANG := -Wno-error=sign-compare -mno-relax
CFLAGS += ${CFLAGS_$(OS_IMAGE)_$(COMPILER)} -DBIN_SOURCE_$(BIN_SOURCE)

LDFLAGS := $(ARCH_ABI) ${LD_FLAGS_$(OS_IMAGE)}

CC_GCC := ${PREFIX_$(OS_IMAGE)}-gcc
SYSROOT_Debian = $(shell $(CC_GCC) -print-sysroot)
ifeq ($(BIN_SOURCE),SRI_Cambridge)
	SYSROOT_FreeBSD := /opt/cheri/sdk/sysroot-$(SOURCE_VARIANT)
else
	SYSROOT_FreeBSD := $(BESSPIN_GFE_FREEBSD_SYSROOT)
endif
CLANG ?= clang
SYSROOT ?= $(SYSROOT_$(OS_IMAGE))
CC_CLANG := $(CLANG) -target ${PREFIX_$(OS_IMAGE)} --sysroot=$(SYSROOT)

LD_GCC_GCC := $(CC_GCC)
LD_CLANG_GCC := $(LD_GCC_GCC)
LD_CLANG_LLD := $(CC_CLANG)

GCC_LIB_DIR = $(shell dirname $(shell $(CC_GCC) -print-libgcc-file-name))
LDFLAGS_Debian_LLD = -L$(GCC_LIB_DIR) -B$(GCC_LIB_DIR)
LDFLAGS_FreeBSD_LLD := -fuse-ld=lld

LDFLAGS += ${LDFLAGS_$(OS_IMAGE)_$(LINKER)}

CC := ${CC_$(COMPILER)}
LD := ${LD_$(COMPILER)_$(LINKER)}
