# This file has the necessary includes to cross-compile files for Linux

ifeq ($(BIN_SOURCE),SRI_Cambridge)
	ARCH_ABI := -march=rv64imafdcxcheri -mabi=l64pc128d
else
	ARCH_ABI := -march=rv64imafdc -mabi=lp64d
endif
FETT_DEFS := -DfettOnLinux -DfettOn$(OS_IMAGE) -DfettOn$(TARGET) 
FETT_DEFS += -DtestgenOnLinux -DtestgenOn$(OS_IMAGE) -Dtestgen$(TARGET)
ifeq ($(TARGET),VCU118)
	FETT_DEFS += -DtestgenFPGA -DfettOnFPGA #for backward compatibility
else
ifeq ($(TARGET),AWSF1)
	FETT_DEFS += -DtestgenAWS -DfettOnAWS #for backward compatibility
endif
endif

CFLAGS := $(ARCH_ABI) -Wall -O0 $(FETT_DEFS)

ifeq ($(BIN_SOURCE),SRI_Cambridge)
	PREFIX_FreeBSD := riscv64-unknown-freebsd13.0
else
	PREFIX_FreeBSD := riscv64-unknown-freebsd12.1
endif
PREFIX_Debian := riscv64-unknown-linux-gnu
CFLAGS_FreeBSD_CLANG := -Wno-error=sign-compare -mno-relax
CFLAGS += ${CFLAGS_$(OS_IMAGE)_$(COMPILER)} -DBIN_SOURCE_$(BIN_SOURCE)

LD_FLAGS_FreeBSD := -L$(PREFIX_FreeBSD)-ld -lpam -lrt
LD_FLAGS_Debian := -lpam -lpam_misc -lrt -lkeyutils 
LD_FLAGS_Debian += -I$(BESSPIN_TESTGEN_PAM_DIR)/include  -L$(BESSPIN_TESTGEN_PAM_DIR)/lib
LD_FLAGS_Debian += -I$(BESSPIN_TESTGEN_KEYUTILS_DIR)/include -L$(BESSPIN_TESTGEN_KEYUTILS_DIR)/lib
LDFLAGS := $(ARCH_ABI) ${LD_FLAGS_$(OS_IMAGE)}

CC_GCC := ${PREFIX_$(OS_IMAGE)}-gcc
SYSROOT_Debian = $(shell $(CC_GCC) -print-sysroot)
ifeq ($(BIN_SOURCE),SRI_Cambridge)
	SYSROOT_FreeBSD := /opt/cheri/sdk/sysroot-$(SOURCE_VARIANT)
else
	SYSROOT_FreeBSD := $(FETT_GFE_FREEBSD_SYSROOT)
endif
CC_CLANG := clang -target ${PREFIX_$(OS_IMAGE)} --sysroot=${SYSROOT_$(OS_IMAGE)}

LD_GCC_GCC := $(CC_GCC)
LD_CLANG_GCC := $(LD_GCC_GCC)
LD_CLANG_LLD := $(CC_CLANG)

GCC_LIB_DIR = $(shell dirname $(shell $(CC_GCC) -print-libgcc-file-name))
LDFLAGS_Debian_LLD = -L$(GCC_LIB_DIR) -B$(GCC_LIB_DIR)
LDFLAGS_FreeBSD_LLD := -fuse-ld=lld

LDFLAGS += ${LDFLAGS_$(OS_IMAGE)_$(LINKER)}

CC := ${CC_$(COMPILER)}
LD := ${LD_$(COMPILER)_$(LINKER)}
