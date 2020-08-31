# Notes #

`$CHERIBUILD_SDK` is set up to be `/opt/cheri/sdk`.

`$PATH` is set up to include `/opt/cheri/sdk/bin`, and `$CLANG` is set up to be the `clang` binary within that directory.

`$SYSROOT` is set up to be `/opt/cheri/sdk/sysroot-default` by default. This is the default kernel variant.

The `purecap` and `temporal` sysroots are in `/opt/cheri/sdk/sysroot-purecap` and `/opt/cheri/sdk/sysroot-temporal` respectively.
