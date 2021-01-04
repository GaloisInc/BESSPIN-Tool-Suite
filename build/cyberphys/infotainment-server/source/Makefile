CANLIB = ../../canlib/lib

SRCS =	./main.c \
		./infotainment_server.c \
		$(CANLIB)/*.c

infotainment_server:
	gcc -I$(CANLIB) $(SRCS) -o infotainment_server

clean:
	@find . -name "*.out" -type f -delete
	@find . -name "*.asm" -type f -delete
	@find . -name "*.elf" -type f -delete
	rm -f infotainment_server

.PHONY:	infotainment_server clean
