# This file has the necessary includes to cross-compile files for Unix

ifeq ($(BIN_SOURCE),SRI_Cambridge)
	ARCH_ABI := -march=rv64imafdcxcheri -mabi=l64pc128d
else
	ARCH_ABI := -march=rv64imafdc -mabi=lp64d
endif
BESSPIN_DEFS := -DbesspinOnLinux -DbesspinOn$(OS_IMAGE) -DbesspinOn$(TARGET) 
BESSPIN_DEFS += -DtestgenOnUnix -DtestgenOn$(OS_IMAGE) -Dtestgen$(TARGET)
ifeq ($(TARGET),VCU118)
	BESSPIN_DEFS += -DtestgenFPGA -DbesspinOnFPGA #for backward compatibility
else
ifeq ($(TARGET),AWSF1)
	BESSPIN_DEFS += -DtestgenAWS -DbesspinOnAWS #for backward compatibility
endif
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

LD_FLAGS_FreeBSD := -L$(PREFIX_FreeBSD)-ld -lpam -lrt
ifneq ($(BIN_SOURCE),LMCO)
	LD_FLAGS_Debian := -lpam -lpam_misc -lrt -lkeyutils 
	LD_FLAGS_Debian += -I$(BESSPIN_TESTGEN_PAM_DIR)/include  -L$(BESSPIN_TESTGEN_PAM_DIR)/lib
	LD_FLAGS_Debian += -I$(BESSPIN_TESTGEN_KEYUTILS_DIR)/include -L$(BESSPIN_TESTGEN_KEYUTILS_DIR)/lib
endif
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
