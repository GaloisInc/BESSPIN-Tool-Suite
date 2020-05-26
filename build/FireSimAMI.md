# Building FETT Target AMI with FireSim

## Overview

This guide outlines how to modify a FPGA Developer AMI to run both FETT Target and FireSim built FPGA tools. This image is designed for FETT Target development, and contains a minimal cloudGFE to start with a working OS boot. The critical modifications are

* Update `git` so that the FETT Environment can aquire its sources correctly
* Produce a FETT Environment by populating packages in `nix/store`
* Setup the FPGA tools, and required kernel modules

## Procedure

1. Launch a `f1.2xlarge` instance. Importantly, search for the AMI

   ```
   FPGA Developer AMI - 1.6.0-40257ab5-6688-4c95-97d1-e251a40fd1fc-ami-0b1edf08d56c2da5c.4 (ami-02b792770bf83b668)
   ```

   to acquire a FireSim compatible image. Follow the usual AWS procedure, selecting a VPC with a public subnet. Ideally, add protection from accidental termination. Increase the storage to ~100GB and remove the ephemeral storage drive. 

2. Install the Nix Package Manager. In this case, the `no-daemon` pathway was used due to difficulties in installing in CentOS 7. The command

   ```
   $ sh <(curl https://nixos.org/nix/install) --no-daemon
   ```

   was used. 

3. Install git 2.x.x. You can install git using whatever technique you want, but since nix was just installed, it can be done conveniently,

   ```
   $ nix-env -i git
   ```

4. As FETT Environment is based on tool-suite, all of the relevant accesses need to be setup in order for the shell to function correctly. Provided that you have access to the correct repositories, it will help to setup SSH keys with [http://gitlab-ext.galois.com](https://docs.gitlab.com/ee/ssh/) and [www.github.com](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent). Also, tool-suite utilizes a binary cache that will need to be accessed. This is done by [following the tool-suite setup instructions](https://gitlab-ext.galois.com/ssith/tool-suite). The general steps are to create two files, a `nix.conf` configuration file and a `netrc` file with the relevant artifactory login credentials.

   **/home/centos/.config/nix/nix.conf**

   ```
   trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= besspin.galois.com-1:8IqXQ2FM1J5CuPD+KN9KK4z6WHve4KF3d9zGRK+zsBw=
   substituters = https://artifactory.galois.com/besspin_generic-nix/ https://cache.nixos.org/
   netrc-file = /home/centos/.config/nix/netrc
   ```

   **/home/centos/.config/netrc**

   ```
    machine artifactory.galois.com
    login <your username>
    password <your password>
   ```

5. Clone the [FETT Target Repository](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Target). Initialize and update the submodules, and then run

   ```
   $ git clone https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Target.git && cd SSITH-FETT-Target
   $ git submodule init
   $ git submodule update
   $ nix-shell
   $ exit
   ```

   Nix will now perform the first time builds and installation of the FETT Environment. This will take ~20 minutes. After the first time installation, subsequent re-runs will only take a few seconds.

6. Clone the SSITH fork of FireSim. 

   ```
   $ cd ~
   $ git clone https://github.com/DARPA-SSITH-Demonstrators/firesim.git 
   ```

   Not much is configured for this project out of the box. It is cloned for convenience when developing FETT Target.

7. Copy over the minimal CloudGFE

   ```
   $ cd ~
   $ aws s3 cp s3://firesim-845509001885/minimal_cloudgfe.tgz .
   $ tar xzvf minimal_cloudgfe.tgz
   $ rm minimal_cloudgfe.tgz
   $ cd minimal_cloudgfe
   $ ./setup.sh
   ```

   Importantly, do not run `setup.sh` in a nix shell. The toolchain that it uses to build inside the `aws-fpga ` task will fail, as it relies on a toolchain shipped with the AMI.

8. Clear personal items and prepare image for AMI creation. 
   * remove git usernames if they are configured
   * **delete the contents of `/home/centos/.config/nix` as they contain your login credentials**
   * **delete/deactivate the SSH keys associated with your GitHub/GitLab accounts**
   * clear your command history

9. Go to `Instances` in the EC2 dashboard. Select the `f1` instances, and `Image->Create Image`. The AMI will be created and ready for use shortly.