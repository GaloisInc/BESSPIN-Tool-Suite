CANLIB = ../../canlib/lib

SERVER_SRCS =	./main.c \
				./infotainment_server.c \
				./infotainment_utils.c \
				$(CANLIB)/*.c

TEST_SRCS =	./test_client.c \
			./infotainment_utils.c \
			$(CANLIB)/*.c

all: infotainment_server test_client

infotainment_server:
	gcc -I$(CANLIB) $(SERVER_SRCS) -o infotainment_server

test_client:
	gcc -I$(CANLIB) $(TEST_SRCS) -o test_client

clean:
	@find . -name "*.out" -type f -delete
	@find . -name "*.asm" -type f -delete
	@find . -name "*.elf" -type f -delete
	rm -f infotainment_server test_client

.PHONY:	infotainment_server test_client clean
