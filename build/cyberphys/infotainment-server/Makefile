CANLIB = ../canlib/lib

SERVER_SRCS =	source/main.c \
				source/infotainment_server.c \
				source/infotainment_utils.c \
				$(CANLIB)/*.c

TEST_SRCS = source/test_client.c \
			source/infotainment_utils.c \
			$(CANLIB)/*.c

LINUX_CC = riscv64-unknown-linux-gnu-gcc
FREEBSD_CC = clang -target riscv64-unknown-freebsd12.1 --sysroot=$(FETT_GFE_FREEBSD_SYSROOT)

all: native linux freebsd

native: infotainment_server_native test_client_native

linux: infotainment_server_linux test_client_linux

freebsd: infotainment_server_freebsd test_client_freebsd

infotainment_server_native:
    # uses the local GCC, whatever it is
	gcc -I$(CANLIB) $(SERVER_SRCS) -o infotainment_server

test_client_native:
    # uses the local GCC, whatever it is
	gcc -I$(CANLIB) $(TEST_SRCS) -o test_client

infotainment_server_linux:
	$(LINUX_CC) -I$(CANLIB) $(SERVER_SRCS) -o infotainment_server_linux

test_client_linux:
	$(LINUX_CC) -I$(CANLIB) $(TEST_SRCS) -o test_client_linux
	
infotainment_server_freebsd:
	$(FREEBSD_CC) -I$(CANLIB) $(SERVER_SRCS) -o infotainment_server_freebsd

test_client_freebsd:
	$(FREEBSD_CC) -I$(CANLIB) $(TEST_SRCS) -o test_client_freebsd
	
clean:
	@find . -name "*.out" -type f -delete
	@find . -name "*.asm" -type f -delete
	@find . -name "*.elf" -type f -delete
	rm -f infotainment_server* test_client*

.PHONY: infotainment_server test_client infotainment_server_freebsd test_client_freebsd infotainment_server_linux test_client_linux clean
