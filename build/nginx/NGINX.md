# Building NGINX 1.13.2

## Debian

This assumes that the working directory is `$ROOT` and the user is in a `tool-suite` nix shell.

### Dependencies

We ignore all of the following dependencies.
- PCRE (needed for the `rewrite` module)
- zlb (needed for the `gzip` module)
- OpenSSL (needed for the `ssl` module)

### Building NGINX

It seems nginx [does not officially support cross-compilation](https://forum.nginx.org/read.php?2,279437,279441#msg-279441), so these steps are adapted from [this](http://tiebing.blogspot.com/2014/09/cross-compile-nginx-for-arm.html) blog post.

1. Fetch and unpack the source tarball.
```
$ wget https://nginx.org/download/nginx-1.13.2.tar.gz
$ tar zxf nginx-1.13.2.tar.gz
$ cd nginx-1.13.2
```

2. Configure and make the build scripts on the current host.
```
$ ./configure \
  --with-http_v2_module \
  --without-http_gzip_module \
  --without-http_rewrite_module --without-pcre \
  --prefix=$ROOT/nginx-build
$ make
```

4. Replace the first section (lines 2-5) in `$ROOT/nginx-1.13.2/objs/Makefile` with the following.
```
CC =	riscv64-unknown-linux-gnu-gcc
CFLAGS =  -march=rv64imafdc -mabi=lp64d -Wall -O0
LINK =	$(CC)
```

5. Clean the old build.
```
$ find . -name "*.o" | xargs rm -f
```

3. Install a cross-compiled NGINX into `$ROOT/nginx-build`. The executable can be found at `$ROOT/nginx-build/sbin/nginx`.
```
$ make
$ make install
```
