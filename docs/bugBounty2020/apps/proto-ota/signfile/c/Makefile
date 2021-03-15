all: verifyfile

CFLAGS=-I/usr/local/include -Wall
LFLAGS=-L/usr/local/lib

verifyfile: verifyfile.o
	gcc -o verifyfile $(LFLAGS) verifyfile.o -lwolfssl

.o:.c
	gcc -c $(CFLAGS) $<

clean:
	rm -f verifyfile *.o
