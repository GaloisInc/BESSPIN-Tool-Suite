## Makefile for loading files to flash
## Required Variables: PROG, XLEN, BIN_SOURCE
PREFIX=riscv64-unknown-elf

ifeq ($(XLEN),32)
	ARCH_ABI := -march=rv32im -mabi=ilp32
else 
	ifeq ($(BIN_SOURCE),SRI_Cambridge)
		ARCH_ABI := -march=rv64imafdcxcheri -mabi=l64pc128d
	else
		ARCH_ABI := -march=rv64imafdc -mabi=lp64d
	endif
endif

# Decide which compiler to use
ifeq ($(USE_CLANG),yes)
	CC		= clang --target=riscv$(XLEN) 
	OBJCOPY	= llvm-objcopy
	WERROR ?= 
else
	CC		= $(PREFIX)-gcc
	OBJCOPY	= $(PREFIX)-objcopy
	WERROR ?= -Werror
endif

# Default target
default: bootmem.bin

# Stripped binary
$(PROG).bin: $(PROG)
	$(OBJCOPY) -O binary $< $@

# Non-stripped binary (intermediate step)
bootmem: bootmem.S linker.ld $(PROG).bin
	@rm -rf bbl.bin
	@ln -s $(PROG).bin bbl.bin
	$(CC) $(ARCH_ABI) -Tlinker.ld $< -nostdlib -static -Wl,--no-gc-sections -o $@

# Stripped Binary file for booting from flash
bootmem.bin: bootmem
	$(OBJCOPY) -O binary $< $@

clean:
	@rm -f bootmem bootmem.bin $(PROG).bin
	
.PHONY: default
