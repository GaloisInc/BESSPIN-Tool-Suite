# Building NGINX 1.13.2

## Debian

### Dependencies

We assume OpenSSL 1.0.2, appropriately cross-compiled, is already installed in `$OPENSSL_DIR`.

We ignore the following dependencies.
- PCRE (needed for the `rewrite` module)
- zlb (needed for the `gzip` module)

### Building NGINX

It seems nginx [does not officially support cross-compilation](https://forum.nginx.org/read.php?2,279437,279441#msg-279441), so these steps are adapted from [this](http://tiebing.blogspot.com/2014/09/cross-compile-nginx-for-arm.html) blog post.

1. Enter a FETT nix shell and set `$BUILD_DIR` to the working directory.
```
$ BUILD_DIR=`pwd`
```

2. Fetch and unpack the source tarball.
```
$ wget https://nginx.org/download/nginx-1.13.2.tar.gz
$ tar zxf nginx-1.13.2.tar.gz
$ cd nginx-1.13.2
```

3. Configure and make the build scripts on the current host.
```
$ ./configure \
  --with-http_v2_module \
  --with-http_ssl_module \
  --without-http_gzip_module \
  --without-http_rewrite_module --without-pcre \
  --prefix=$BUILD_DIR/nginx-riscv
$ make
```

4. Modify `$BUILD_DIR/nginx-1.13.2/objs/Makefile`.

   - Replace the first section (lines 2-5) with the following.
     ```
     CC =  riscv64-unknown-linux-gnu-gcc
     CFLAGS =  -march=rv64imafdc -mabi=lp64d -Wall -O0 -I $(OPENSSL_DIR)/include
     LINK =  $(CC)
     ```
     
   - Replace the line "`-ldl -lpthread -lcrypt -lssl -lcrypto -ldl \`" (line 357) with the following.
     ```
     -ldl -lpthread -lcrypt $(OPENSSL_DIR)/lib/libssl.a $(OPENSSL_DIR)/lib/libcrypto.a -ldl \
     ```

5. Clean the old build.
```
$ find . -name "*.o" | xargs rm -f
```

6. Install a cross-compiled NGINX into `$BUILD_DIR/nginx-riscv`. The executable can be found at `$BUILD_DIR/nginx-riscv/sbin/nginx`.
```
$ make OPENSSL_DIR=$OPENSSL_DIR
$ make install
```

## FreeBSD

## Dependencies

We ignore the following dependencies.
- PCRE (needed for the `rewrite` module)

All other dependencies should aready be included in FreeBSD.

### Building NGINX

The approach for building on Debian does not work here, as configuring
on a Linux host will lead to errors when compiling for
FreeBSD. Instead we apply the changes from
[here](https://github.com/CTSRD-CHERI/nginx/commit/7346e0c792ab6608546a8f8cf55c6a505a70c2b9),
which allow the configure checks to pass when cross compiling.

1. Enter a FETT nix shell and set `$BUILD_DIR` to the working directory.
```
$ BUILD_DIR=`pwd`
```

2. Fetch and unpack the source tarball.
```
$ wget https://nginx.org/download/nginx-1.13.2.tar.gz
$ tar zxf nginx-1.13.2.tar.gz
$ cd nginx-1.13.2
```

3. Apply the patch located at
`build/0001-Pass-configure-checks-when-cross-compiling.patch` relative
to this directory.
```
$ patch -p1 <path/to/0001-Pass-configure-checks-when-cross-compiling.patch
```

4. Set the variable `SYSROOT` to  the location of the sysroot for your
   FreeBSD RISC-V toolchain. If you have an installation of GCC, then
   this can be done as follows:
```
$ SYSROOT=$(riscv64-unknown-freebsd12.1-gcc -print-sysroot)
```
  Set `CFLAGS`:
```
$ CFLAGS="-target riscv64-unknown-freebsd12.1 -march=rv64imafdc -mabi=lp64d -Wno-error=sign-compare --sysroot=${SYSROOT}"
```

5. Configure for the target platform, explicitly defining the settings
   which the build scripts are unable to detect when cross compiling.
```
$ env NGX_HAVE_TIMER_EVENT=yes \
      NGX_SIZEOF_int=4 \
      NGX_SIZEOF_long=8 \
      NGX_SIZEOF_long_long=8 \
      NGX_SIZEOF_void_p=8 \
      NGX_SIZEOF_sig_atomic_t=8 \
      NGX_SIZEOF_size_t=8 \
      NGX_SIZEOF_off_t=8 \
      NGX_SIZEOF_time_t=8 \
      NGX_HAVE_MAP_ANON=yes \
      NGX_HAVE_SYSVSHM=yes \
      NGX_HAVE_MAP_DEVZERO=yes \
      NGX_HAVE_POSIX_SEM=yes \
      ./configure \
          --without-pcre \
          --without-http_rewrite_module \
          --with-http_v2_module \
          --with-http_ssl_module \
          --crossbuild=FreeBSD \
          --with-cc=clang \
          --with-cc-opt="${CFLAGS}" \
          --with-ld-opt="${CFLAGS}" \
          --sysroot=${SYSROOT} \
          --prefix=$BUILD_DIR/nginx-riscv
```

6. Build a cross-compiled NGINX and install into
   `$BUILD_DIR/nginx-riscv`. The executable can be found at
   `$BUILD_DIR/nginx-riscv/sbin/nginx`.
```
$ make
$ make install
```
