SRCS =  ./lib/canlib.c \
        ./lib/j1939.c \

client:
	gcc -I./lib $(SRCS) client.c -o client

clean:
	@find . -name "*.out" -type f -delete
	@find . -name "*.asm" -type f -delete
	@find . -name "*.elf" -type f -delete

.PHONY: client clean