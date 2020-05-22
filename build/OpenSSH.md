# Building OpenSSH v7.3

## General Description

The OpenSSH project includes a client `ssh`, a server `sshd` , the `scp` and `sftp` protocols, a key generation tool `ssh-keygen` , a run-time key storage tool `ssh-agent` and other utilities. 

### Dependencies 

* `autoconf` and `make`
* A C compiler and standard library
* `zlib`
* `libcrypto` from either LibreSSL or OpenSSL
* (optional) `libfido2` for FIDO security token support

### Customizations

* PAM support
* `libedit` support for sftp
* Kerberos/GSSAPI support
* SELinux support
* U2F/FIDO2 security keys

## Build Steps

#### Environment Setup

1. Enter the FETT Nix environment.
2. Setup `CROSS_PREFIX`, dependent on whether FreeBSD or Debian target

```bash
$ CROSS_PREFIX=riscv64-unknown-linux-gnu 		# Debian
$ CROSS_PREFIX=riscv64-unknown-freebsd12.1 	# FreeBSD
```

3. Refer to the build variables

```bash
$ ARCH_ABI="-march=rv64imafdc -mabi=lp64d"	
$ BUILD_DIR=`pwd`
```

If using GCC:
```bash
$ CFLAGS="${ARCH_ABI} -Wall -lrt -fPIC"
$ CC=${CROSS_PREFIX}-gcc
$ AR=${CROSS_PREFIX}-ar
$ RANLIB=${CROSS_PREFIX}-ranlib
$ STRIP=${CROSS_PREFIX}-strip
```
If using Clang:
```bash
$ SYSROOT=$(${CROSS_PREFIX}-gcc -print-sysroot)
$ CFLAGS="-target ${CROSS_PREFIX} ${ARCH_ABI} -Wall -lrt -fPIC --sysroot=${SYSROOT} -fuse-ld=lld -mno-relax"
$ CC=clang
$ AR=llvm-ar
$ RANLIB=llvm-ranlib
$ STRIP=llvm-strip
```

#### Build Zlib v1.2.11

4. Clone , configure, build and install zlib

```bash
$ mkdir zlib-riscv
$ git clone https://github.com/madler/zlib.git && cd zlib
$ git checkout cacf7f1
$ ./configure --prefix=${BUILD_DIR}/zlib-riscv 
# host option doesn't exist in configure, so modify make variables
$ make CC="${CC} ${CFLAGS}" LD="${CC}" LDFLAGS="${CFLAGS}" AR="${AR}" RANLIB="${RANLIB}" 
$ make install
$ cd ${BUILD_DIR}
```

#### Build OpenSSL v1.0.2

5. Depending on which platform you are compiling for, set the variable
   `OPENSSL_CONFIG`.

```bash
$ OPENSSL_CONFIG=linux-generic64 # debian
$ OPENSSL_CONFIG=BSD-generic64   # FreeBSD
```

Clone, configure, build and install OpenSSL. If using Clang, omit the
`--cross-compile-prefix` flag when running `Configure`.

```bash
$ mkdir openssl-riscv
$ git clone https://github.com/openssl/openssl.git && cd openssl
$ git checkout origin/OpenSSL_1_0_2-stable
$ ./Configure ${OPENSSL_CONFIG} --cross-compile-prefix=${CROSS_PREFIX}- --openssldir=${BUILD_DIR}/openssl-riscv 
$ make CC="${CC} ${CFLAGS}" LD="${CC} ${CFLAGS}" AR="${AR} r"
$ make install
$ cd ${BUILD_DIR}
```

#### Build OpenSSH v7.3

6. Clone and configure OpenSSH

```bash
$ mkdir openssh-riscv
$ git clone https://github.com/openssh/openssh-portable.git && cd openssh-portable
$ git checkout origin/V_7_3
$ autoreconf
$ ./configure --prefix=${BUILD_DIR}/openssh-riscv --with-privsep-path=${BUILD_DIR}/openssh-riscv/var/empty --host=${CROSS_PREFIX} --with-libs --with-zlib=${BUILD_DIR}/zlib-riscv --with-ssl-dir=${BUILD_DIR}/openssl-riscv --disable-etc-default-login CC="${CC} ${CFLAGS}" LD="${CC} ${CFLAGS}" AR="${AR}" RANLIB="${RANLIB}"
```

If you are building for debian, you may have to run the following command.
```bash
# FETT environment sysroot doesn't have <utmp.h>, so BTMP has to be disabled in config.h
$ sed 's/#define USE_BTMP .*/\/\* #define USE_BTMP 1 \*\//' -i config.h

```

7. Build and install OpenSSH.
```bash
$ make
$ make STRIP_OPT="--strip-program=${STRIP} -s" install-files
$ cd ${BUILD_DIR}/openssh-riscv
```

7. The cross built files are in `BUILD_DIR/openssh-riscv`
