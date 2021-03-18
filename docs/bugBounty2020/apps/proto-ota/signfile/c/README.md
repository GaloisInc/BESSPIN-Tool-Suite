## VerifyFile (C Version)

The main program here (verifyfile.c) verifies the Ed25519 signature of a given file, using the FETT OTA application public key.

## Dependencies

This program uses the WolfSLL library.

The Makefile assumes that WolfSSL is configured, built, and installed in /usr/local/include (include files) and /usr/local/lib (static libraries).

For the purposes of this project, WolfSSL should be configured, built and installed as follows, using the FETT-Target nix-shell environment:

```Shell
sudo apt-get install autoconf automake libtool
git clone https://github.com/wolfSSL/wolfssl.git
cd wolfssl
./autogen.sh
./configure --enable-curve25519 --enable-ed25519 --disable-shared --enable-static
make
make check # Should report 6 out of 6 test suites passing
sudo make install
```


## Build

This program is designed to build and run on Linux, using the FETT-Target project nix-shell environment.

From within nix-shell, a simple "make" in this directory should suffice.
