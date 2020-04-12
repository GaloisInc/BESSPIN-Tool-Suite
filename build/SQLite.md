# Building SQLite 3.22.0

## Debian

### Dependencies

- `tclsh` (e.g. `apt install tcl`)
- `libpthread`, `libdl` (should be available in the Tool Suite Nix environment)

### Build Steps

0. We'll assume the working directory is $ROOT and that the user is in a Tool Suite Nix environment (e.g. `nix-shell /path/to/tool-suite/shell.nix).
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
   ```
   $ riscv64-unknown-linux-gnu-gcc shell.c sqlite3.c -ldl -lpthread -o sqlite3` 
   ```
   (`clang` works as well)
