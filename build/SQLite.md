# Building SQLite 3.22.0

## Debian

### Dependencies

- `tclsh` (e.g. `apt install tcl`) (should be available in the FETT Nix environment)
- `libpthread`, `libdl` (should be available in the FETT Nix environment)

### Build Steps

0. We'll assume the working directory is $ROOT and that the user is in a FETT Nix environment (e.g. `ix-shell /path/to/fett/shell.nix).
1. Fetch and unpack the source tarball from
   `https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=version-3.22.0`, e.g.
   ```
   $ curl https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=version-3.22.0 -o sqlite.tar.gz
   $ tar xzvf sqlite.tar.gz
   ```
   Verify the version: `cat $ROOT/sqlite/VERSION`
2. Create and switch to a build directory: 
   ```
   $ mkdir $ROOT/sqlite-build && cd $ROOT/sqlite-build
   ```
3. Configure the build scripts: 
   ```
   $ $ROOT/sqlite/configure --host=riscv64-unknown-linux
   ```
4. Generate the source file (yes, one file):
   ```
   $ make sqlite3.c
   ```
5. Compile `sqlite3` with CLI:
   - Compile:
   ```
   $CC -c -o sqlite3.o sqlite3.c $CFLAGS
   $CC -c -o shell.o shell.c $CFLAGS
   ```
   - Link:
   ```
   $LD -o sqlite3 sqlite3.o shell.o -lpthread -ldl $(LDFLAGS)
   ```
   
   The correct values for `CC`, `LD`, `CFLAGS`, and `LDFLAGS` can be obtained by
   setting the environment variables `OS_IMAGE=DEBIAN`, `CC` (to either `GCC` or
   `CLANG`), and `LD` (to either `LLD` or `GCC`), and then running (`env.mk` is provided [here](env.mk))
   ```
   make -f env.mk print-CC print-LD print-CFLAGS print-LDFLAGS
   ```
   e.g.
   ```
   $ COMPILER=GCC LINKER=GCC OS_IMAGE=Debian make -f env.mk print-CC print-LD print-LDFLAGS print-CFLAGS
   ```
   

## Troubleshooting

If `make sqlite3.c` dies, check to see if the error mentions `tcl` or `tclsh`, e.g.:
```
tclsh8.6 /home/besspinuser/tool-suite/sqlite/tool/mkopcodec.tcl opcodes.h >opcodes.c
can't read "label(0)": no such variable
    while executing
"format "    /* %3d */ %-18s OpHelp(\"%s\"),"  $i \"$label($i)\" $synopsis($i)"
    ("for" body line 2)
    invoked from within
"for {set i 0} {$i<=$mx} {incr i} {
  puts [format "    /* %3d */ %-18s OpHelp(\"%s\")," \
         $i \"$label($i)\" $synopsis($i)]
}"
    (file "/home/besspinuser/tool-suite/sqlite/tool/mkopcodec.tcl" line 43)
make: *** [Makefile:972: opcodes.c] Error 1
```

If so, you are missing the `tcl` dependency (see above)! Install `tcl`, run `make distclean` and try again from step 3.
