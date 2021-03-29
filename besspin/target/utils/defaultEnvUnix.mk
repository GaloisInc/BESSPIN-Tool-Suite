# This file has the necessary includes to cross-compile files for Unix

ifeq ($(BIN_SOURCE),SRI_Cambridge)
	ARCH_ABI := -march=rv64imafdcxcheri -mabi=l64pc128d
else
	ARCH_ABI := -march=rv64imafdc -mabi=lp64d
endif
BESSPIN_DEFS += -DBESSPIN_UNIX -DBESSPIN_$(OS_IMAGE) -DBESSPIN_$(TARGET)
ifeq ($(TARGET),$(filter $(TARGET),VCU118 AWSF1))
	BESSPIN_DEFS += -DBESSPIN_FPGA 
endif

CFLAGS := $(ARCH_ABI) -Wall -O0 $(BESSPIN_DEFS)

ifeq ($(BIN_SOURCE),SRI_Cambridge)
	PREFIX_FREEBSD := riscv64-unknown-freebsd13.0
else
	PREFIX_FREEBSD := riscv64-unknown-freebsd12.1
endif
ifeq ($(BIN_SOURCE),LMCO)
	#In the docker image, this is v8.3.0
	PREFIX_DEBIAN := riscv64-unknown-elf
else
	PREFIX_DEBIAN := riscv64-unknown-linux-gnu
endif
CFLAGS_FREEBSD_CLANG := -Wno-error=sign-compare -mno-relax
CFLAGS += ${CFLAGS_$(OS_IMAGE)_$(COMPILER)} -DBIN_SOURCE_$(BIN_SOURCE)

LDFLAGS := $(ARCH_ABI) ${LD_FLAGS_$(OS_IMAGE)}

CC_GCC := ${PREFIX_$(OS_IMAGE)}-gcc
SYSROOT_DEBIAN = $(shell $(CC_GCC) -print-sysroot)
ifeq ($(BIN_SOURCE),SRI_Cambridge)
	SYSROOT_FREEBSD := /opt/cheri/sdk/sysroot-$(SOURCE_VARIANT)
else
	SYSROOT_FREEBSD := $(BESSPIN_GFE_FREEBSD_SYSROOT)
endif
CLANG ?= clang
SYSROOT ?= $(SYSROOT_$(OS_IMAGE))
CC_CLANG := $(CLANG) -target ${PREFIX_$(OS_IMAGE)} --sysroot=$(SYSROOT)

LD_GCC_GCC := $(CC_GCC)
LD_CLANG_GCC := $(LD_GCC_GCC)
LD_CLANG_LLD := $(CC_CLANG)

GCC_LIB_DIR = $(shell dirname $(shell $(CC_GCC) -print-libgcc-file-name))
LDFLAGS_DEBIAN_LLD = -L$(GCC_LIB_DIR) -B$(GCC_LIB_DIR)
LDFLAGS_FREEBSD_LLD := -fuse-ld=lld

LDFLAGS += ${LDFLAGS_$(OS_IMAGE)_$(LINKER)}

CC := ${CC_$(COMPILER)}
LD := ${LD_$(COMPILER)_$(LINKER)}
