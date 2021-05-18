BASENAME ?= hack

CANLIB ?= ../../canlib/lib

INCLUDES = -I. \
		-I $(CANLIB)

SRCS = main.c $(CANLIB)/j1939.c $(CANLIB)/canlib.c

DEFAULT: hack

all: hack hack-x86 clean

hack:
	@riscv64-unknown-linux-gnu-gcc -march=rv64imafd -mabi=lp64d $(INCLUDES) $(SRCS) -o $(BASENAME).elf
	@riscv64-unknown-linux-gnu-objdump -S $(BASENAME).elf > $(BASENAME).asm

hack-x86:
	@gcc $(INCLUDES) $(SRCS) -o $(BASENAME).elf

clean:
	@rm -rf $(BASENAME)*