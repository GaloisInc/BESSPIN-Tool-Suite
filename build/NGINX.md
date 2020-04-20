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
