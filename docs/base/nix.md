# NIX Shell #

[The Nix Package Manager](https://nixos.org/nix/) is a tool that takes a unique approach to package management and system configuration. It is a purely functional package manager. This means that it treats packages like values in purely functional programming languages; they are built by functions that don’t have side-effects, and they never change after they have been built. Nix stores packages in the Nix store, usually the directory `/nix/store`, where each package has its own unique subdirectory. You can have multiple versions or variants of a package installed at the same time. This is especially important when different applications have dependencies on different versions of the same package. Because of the hashing scheme, different versions of a package end up in different paths in the Nix store, so they don’t interfere with each other.

---

## Setup ##

Nothing is required from the tool's user other than installing the package manager, then running `nix-shell` in the repo's main directory. This will start an interactive shell that has all the required tools and binaries.

More details can be found in the [submodule](../../SSITH-FETT-Environment) documentation.

---

## Environment Variables ##

Inside the interactive shell, all the tools will be available as Nix manipulates the path with its store symlinks, so for example `riscv64-unknown-elf-gdb` is the RISC-V GDB toolchain, and the command is just available in the shell. 

Regarding binaries, such as OS images, they are available as environment variables. For example, the baseline Debian for VCU118 is `$FETT_GFE_DEBIAN_VCU118`.

The [shell.nix](../../SSITH-FETT-Environment/nix/shell.nix) is the top level file that is executed by `nix-shell` and it lists all the packages and environment variables defined in the shell.

---

## Artifactory ##

Instead of re-building everything --which would take a *long* *long* time--, we upload some pre-built binaries (the ones that have the longest build time) to the artifactory. Any package enlisted in `cachePackages` in [shell.nix](../../SSITH-FETT-Environment/nix/shell.nix) is cached whenever we modify the Nix builds. 

To configure Nix to use the binary cache in the artifactory, please follow [these instructions](https://gitlab-ext.galois.com/ssith/tool-suite#setup).
