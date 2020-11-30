# use EXTRA_LINUX_CFLAGS/EXTRA_FREEBSD_CFLAGS to specify anything extra, like OpenSSL library location
LINUX_CC = riscv64-unknown-linux-gnu-gcc
LINUX_CFLAGS = -fno-stack-protector -z execstack -O0 -march=rv64imafd -mabi=lp64d -g -lcrypto
LINUX_OBJDUMP = riscv64-unknown-linux-gnu-objdump
FREEBSD_CC = riscv64-unknown-freebsd12.1-gcc
FREEBSD_CFLAGS = -fno-stack-protector -z execstack -O0 -march=rv64imafd -mabi=lp64d -g -lcrypto
FREEBSD_OBJDUMP = riscv64-unknown-freebsd12.1-objdump
# for CHERI: CC = riscv64-unknown-freebsd-cc
# for CHERI: CFLAGS = -fno-stack-protector -z execstack -O0 -g --sysroot=/some/path/to/cheri/output/sdk/sysroot-riscv64-purecap -march=rv64imafdcxcheri -mno-relax
# for CHERI: OBJDUMP = riscv64-unknown-freebsd-objdump

# Internal varriables.
#
# SRCS contains the list of all `.c` sources
# found under `./src`.
SRCS := $(shell find ./src/*.c)

all: linux freebsd

# Builds main binary responsible for running
# the HSTATIC server (`./hstatic.out`).
linux: ./cmd/main.c $(SRCS)
	$(LINUX_CC) $(EXTRA_LINUX_CFLAGS) $(LINUX_CFLAGS) -Wall $^ -o ./main-linux.elf
	$(LINUX_OBJDUMP) -S main-linux.elf > main-linux.asm

freebsd: ./cmd/main.c $(SRCS)
	$(FREEBSD_CC) $(EXTRA_FREEBSD_CFLAGS) $(FREEBSD_CFLAGS) -Wall $^ -o ./main-freebsd.elf
	$(FREEBSD_OBJDUMP) -S main-freebsd.elf > main-freebsd.asm

# Removes any binary generated.
clean:
	@find . -name "*.out" -type f -delete
	@find . -name "*.asm" -type f -delete

.PHONY: build clean
