CANLIB = ../canlib/lib

SERVER_SRCS =	source/main.c \
				source/infotainment_server.c \
				source/infotainment_utils.c \
				$(CANLIB)/*.c

HACKED_SRCS =	source/hacked.c \
				source/hacked_server.c \
				source/hacked_utils.c \
				$(CANLIB)/*.c

TEST_SRCS = source/test_client.c \
			source/infotainment_utils.c \
			$(CANLIB)/*.c

LINUX_CC = riscv64-unknown-linux-gnu-gcc
FREEBSD_CC = clang -target riscv64-unknown-freebsd12.1 --sysroot=$(BESSPIN_GFE_FREEBSD_SYSROOT)
FREEBSD_FLAGS = -Wno-error=sign-compare -mno-relax -fuse-ld=lld
ARCH_FLAGS = -march=rv64imafdc -mabi=lp64d
DEBUG := 0
DEBUG_FLAGS = -DINFOTAINMENT_DEBUG_FLAG=$(DEBUG)
HACKED_BROADCAST_ADDRESS := 255.255.255.255
HACKED_POSITION_ADDRESS := -1.-1.-1.-1
HACKED_FLAGS = -DHACKED_BROADCAST_ADDRESS="\"${HACKED_BROADCAST_ADDRESS}\"" -DHACKED_POSITION_ADDRESS="\"${HACKED_POSITION_ADDRESS}\""

all: native linux freebsd

native: infotainment_server_native hacked_server_native test_client_native

linux: infotainment_server_linux hacked_server_linux test_client_linux

freebsd: infotainment_server_freebsd hacked_server_freebsd test_client_freebsd

infotainment_server_native:
    # uses the local GCC, whatever it is
	gcc -I$(CANLIB) $(DEBUG_FLAGS) $(SERVER_SRCS) -o infotainment_server

hacked_server_native:
    # uses the local GCC, whatever it is
	gcc -I$(CANLIB) $(DEBUG_FLAGS) ${HACKED_FLAGS} $(HACKED_SRCS) -o hacked_server

test_client_native:
    # uses the local GCC, whatever it is
	gcc -I$(CANLIB) $(DEBUG_FLAGS) $(TEST_SRCS) -o test_client

infotainment_server_linux:
	$(LINUX_CC) $(ARCH_FLAGS) $(DEBUG_FLAGS) -I$(CANLIB) $(SERVER_SRCS) -o infotainment_server_linux

hacked_server_linux:
	$(LINUX_CC) $(ARCH_FLAGS) $(DEBUG_FLAGS) ${HACKED_FLAGS} -I$(CANLIB) $(HACKED_SRCS) -o hacked_server_linux

test_client_linux:
	$(LINUX_CC) $(ARCH_FLAGS) $(DEBUG_FLAGS) -I$(CANLIB) $(TEST_SRCS) -o test_client_linux
	
infotainment_server_freebsd:
	$(FREEBSD_CC) $(FREEBSD_FLAGS) $(ARCH_FLAGS) $(DEBUG_FLAGS) -I$(CANLIB) $(SERVER_SRCS) -o infotainment_server_freebsd

hacked_server_freebsd:
	$(FREEBSD_CC) $(FREEBSD_FLAGS) $(ARCH_FLAGS) $(DEBUG_FLAGS) ${HACKED_FLAGS} -I$(CANLIB) $(HACKED_SRCS) -o hacked_server_freebsd

test_client_freebsd:
	$(FREEBSD_CC) $(FREEBSD_FLAGS) $(ARCH_FLAGS) $(DEBUG_FLAGS) -I$(CANLIB) $(TEST_SRCS) -o test_client_freebsd
	
besspin_binaries: linux freebsd
	cp infotainment_server_linux hacked_server_linux ../../../BESSPIN-LFS/GFE/appsBinaries/infotainment-server/debian/infotainment_server
	cp infotainment_server_freebsd hacked_server_freebsd ../../../BESSPIN-LFS/GFE/appsBinaries/infotainment-server/FreeBSD/infotainment_server

clean:
	@find . -name "*.out" -type f -delete
	@find . -name "*.asm" -type f -delete
	@find . -name "*.elf" -type f -delete
	rm -f infotainment_server* hacked_server* test_client*

.PHONY: infotainment_server hacked_server test_client infotainment_server_freebsd hacked_server_freebsd test_client_freebsd infotainment_server_linux hacked_server_linux test_client_linux clean
