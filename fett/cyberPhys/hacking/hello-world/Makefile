all: linux freebsd

linux:
	riscv64-unknown-linux-gnu-gcc -fno-stack-protector -z execstack -O0 -march=rv64imafd -mabi=lp64d main.c -o hello-world-linux.elf
	riscv64-unknown-linux-gnu-objdump -S hello-world-linux.elf > hello-world-linux.asm

freebsd:
	riscv64-unknown-freebsd12.1-gcc -fno-stack-protector -z execstack -O0 -march=rv64imafd -mabi=lp64d main.c -o hello-world-freebsd.elf
	riscv64-unknown-freebsd12.1-objdump -S hello-world-freebsd.elf > hello-world-freebsd.asm

clean:
	@rm -rf hello-world*.elf hello-world*.asm