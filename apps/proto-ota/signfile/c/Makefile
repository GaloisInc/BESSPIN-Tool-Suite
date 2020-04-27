all: verifyfile

verifyfile: verifyfile.o
	gcc -o verifyfile verifyfile.o -lwolfssl

.o:.c
	gcc -c -Wall $<

clean:
	rm -f verifyfile *.o
