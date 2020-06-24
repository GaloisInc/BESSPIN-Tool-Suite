# `ssith-aws-fpga` for Fett Target

This procedure describes how build the [ssith-aws-fpga](https://github.com/acceleratedtech/ssith-aws-fpga) project for FPGA on the FETT AMI. The build process is identical to the README presented on the project repo, but the build environment setup is different.

## Procedure

1. Create a Nix shell that uses the pinned packages in [SSITH-FETT-Environment](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Environment).

   **shell.nix**

   ```nix
   {}:
   
   let
     pkgs = import /path/to/ssith-fett-environment/pinned-pkgs.nix {};
     inherit (pkgs) mkShell;
   in mkShell {
     buildInputs = with pkgs; with besspin; [
       cmake
       libelf
   }
   ```

2. Clone the ssith-aws-fpga repository

   ```
   nix-shell /path/to/shell.nix
   git clone https://github.com/acceleratedtech/ssith-aws-fpga.git 
   cd ssith-aws-fpga
   ```

3. Follow the "Building and running `ssith_aws_fpga` on FPGA" section

   ```
   mkdir build
   cd build
   cmake -DFPGA=1 ..
   make
   ```


