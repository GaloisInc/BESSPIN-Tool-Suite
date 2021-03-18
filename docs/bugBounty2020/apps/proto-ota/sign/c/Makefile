all: keygen

CFLAGS=-Wall -I../../../../../mbedtls/include -L../../../../../mbedtls/library

keygen: keygen.o d.o tweetnacl.o devurandom.o
	$(CC) $(CFLAGS) -o keygen keygen.o tweetnacl.o d.o devurandom.o -lmbedtls -lmbedcrypto

.o: .c
	$(CC) -c $(CFLAGS) %<

clean:
	rm -f *.o keygen
