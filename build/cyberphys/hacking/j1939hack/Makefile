BASENAME ?= hack

CANLIB ?= ../../canlib/lib

INCLUDES = -I. \
		-I $(CANLIB)

SRCS = main.c $(CANLIB)/j1939.c $(CANLIB)/canlib.c

DEFAULT: hack

all: hack clean

hack:
	@riscv64-unknown-linux-gnu-gcc -fno-stack-protector -z execstack -O0 -march=rv64imafd -mabi=lp64d $(INCLUDES) $(SRCS) -o $(BASENAME)
	@mv $(BASENAME) $(BASENAME).elf
	@riscv64-unknown-linux-gnu-objdump -S $(BASENAME).elf > $(BASENAME).asm

clean:
	@rm -rf $(BASENAME)*