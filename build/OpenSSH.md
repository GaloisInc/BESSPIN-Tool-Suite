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

## Debian Specifics

Setup the variables

```
CC=riscv64-unknown-linux-gnu-gcc  			# name of C compiler
CROSS_PREFIX=riscv64-unknown-linux-gnu   	# cross compilation host name
```

Then follow the build steps.

## FreeBSD Specifics

Setup the variables

```
CC=riscv64-unknown-freebsd12.1-gcc	 		# name of C compiler
CROSS_PREFIX=riscv64-unknown-freebsd12.1-	# cross compilation host name
```

Then follow the build steps.

## Build Steps

#### Environment Setup

1. Enter the `tool-suite` nix shell

```bash
nix-shell /path/to/tool/suite/shell.nix
```

2. Refer to the build variables

```bash
ARCH_ABI= -march=rv64imafdc -mabi=lp64d 	# architecture/abi
CFLAGS=$(ARCH_ABI) -Wall -lrt -fPIC
BUILD_DIR=`pwd`
```

#### Build Zlib

3. Clone , configure, build and install zlib

```bash
mkdir zlib-riscv
git clone https://github.com/madler/zlib.git && cd zlib
./configure --prefix=${build_dir}/zlib-riscv
make CC="${CROSS_PREFIX}gcc ${CFLAGS}" LD="${CROSS_PREFIX}gcc ${CFLAGS}" AR="${CROSS_PREFIX}ar r" RANLIB="${CROSS_PREFIX}ranlib" 
make install
cd $(BUILD_DIR)
```

#### Build OpenSSL v1.0.2

4. Clone, configure, build and install OpenSSL

```bash
mkdir openssl-riscv
git clone https://github.com/openssl/openssl.git && cd openssl
git checkout origin/OpenSSL_1_0_2-stable
./Configure linux-generic64 --cross-compile-prefix=${CROSS_PREFIX}- --openssldir=${BUILD_DIR}/openssl-riscv
make 
make install
cd $(BUILD_DIR)
```

#### Build OpenSSH v7.3

5. Clone, configure, build and install OpenSSH

```bash
mkdir openssh-riscv
git clone https://github.com/openssh/openssh-portable.git && cd openssh-portable
git checkout origin/V_7_3
./configure --prefix=${BUILD_DIR}/openssh-riscv --with-privsep-path=${build_dir}/openssh-riscv/var/empty --host=${CROSS_PREFIX} --with-libs --with-zlib=${BUILD_DIR}/zlib-riscv --with-ssl-dir=${BUILD_DIR}/openssl-riscv --disable-etc-default-login
# tool-suite sysroot doesn't have <utmp.h>, so BTMP has to be disabled
sed 's/#define USE_BTMP .*/\/\* #define USE_BTMP 1 \*\//' -i config.h
make 
make STRIP_OPT="--strip-program=${cross}strip -s" install-files
cd $(BUILD_DIR)/openssh-riscv
```

6. The cross built files are in `BUILD_DIR/openssh-riscv`

