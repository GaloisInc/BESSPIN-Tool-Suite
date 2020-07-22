# This file has the necessary includes to run Testgen on Linux

ARCH_ABI = -march=rv64imafdc -mabi=lp64d
TESTGEN_DEFS := -DtestgenOnLinux -DtestgenOn$(OS_IMAGE) -Dtestgen$(BACKEND)

CFLAGS := $(ARCH_ABI) -Wall -O0 $(TESTGEN_DEFS)
PREFIX_FreeBSD := riscv64-unknown-freebsd12.1
PREFIX_Debian := riscv64-unknown-linux-gnu

CFLAGS_FreeBSD_CLANG := -mno-relax
CFLAGS += ${CFLAGS_$(OS_IMAGE)_$(COMPILER)}

LD_FLAGS_FreeBSD := -L$(PREFIX_FreeBSD)-ld -lpam -lrt
LD_FLAGS_Debian := -lpam -lpam_misc -lrt -lkeyutils 
LD_FLAGS_Debian += -I$(BESSPIN_TESTGEN_PAM_DIR)/include  -L$(BESSPIN_TESTGEN_PAM_DIR)/lib
LD_FLAGS_Debian += -I$(BESSPIN_TESTGEN_KEYUTILS_DIR)/include -L$(BESSPIN_TESTGEN_KEYUTILS_DIR)/lib
LDFLAGS := $(ARCH_ABI) ${LD_FLAGS_$(OS_IMAGE)}

CC_GCC := ${PREFIX_$(OS_IMAGE)}-gcc
SYSROOT := $(shell $(CC_GCC) -print-sysroot)
CC_CLANG := clang -target ${PREFIX_$(OS_IMAGE)} --sysroot=$(SYSROOT)

LD_GCC_GCC := $(CC_GCC)
LD_CLANG_GCC := $(LD_GCC_GCC)
LD_CLANG_LLD := $(CC_CLANG)

GCC_LIB_DIR := $(shell dirname $(shell $(CC_GCC) -print-libgcc-file-name))
LDFLAGS_Debian_LLD := -L$(GCC_LIB_DIR) -B$(GCC_LIB_DIR)
LDFLAGS_FreeBSD_LLD := -fuse-ld=lld

LDFLAGS += ${LDFLAGS_$(OS_IMAGE)_$(LINKER)}

CC := ${CC_$(COMPILER)}
LD := ${LD_$(COMPILER)_$(LINKER)}
