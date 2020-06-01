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

3. Install git 2.x.x and git lfs. You can install git using whatever technique you want, but since nix was just installed, it can be done conveniently,

   ```
   $ nix-env -i git
   $ nix-env -i git-lfs
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

   For the permanent AMI, an account was created so the FETT Environment can be modified by the user and still interact with the artifactory resources. The user `besspin_fett` was added and a token key was registered. Also, for good practice,

   ```
   $ chmod 600 /home/centos/.config/nix/netrc
   ```

5. Clone the [FETT Target Repository](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Target). If `nix` has already been installed and you're modifying an existing AMI, it is a good idea to delete packages no longer used by the project, with

   ```
   $ nix-collect-garbage
   ```

   Initialize and update the submodules, running

   ```
   $ cd ~
   $ git clone https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Target.git && cd SSITH-FETT-Target
   $ git submodule init
   $ git submodule update
   $ nix-shell
   $ exit
   $ cd ~
   $ rm -rf SSITH-FETT-Target
   ```

   Nix will now perform the first time builds and installation of the FETT Environment. This will take ~20 minutes. After the first time installation, subsequent re-runs will only take a few seconds. 

6. As was suggested in #323, the permissions can be changed for the amazon FPGA management toosl to not require `sudo`. This can be done with
   
   ```
   # sudo chmod u+s /usr/bin/fpga-*
   ```

7. Clear personal items and prepare image for AMI creation. 

   * remove git usernames if they are configured, clearing

     ```
     /home/centos/.gitconfig
     ```

   * **IF NOT USING `besspin_fett`, delete the contents of `/home/centos/.config/nix` as they contain your login credentials**

   * **delete/deactivate the SSH keys associated with your GitHub/GitLab accounts**

   * clear your command history

     ```
     $ rm ~/.bash_history
     $ history -c
     ```

8. Go to `Instances` in the EC2 dashboard. Select the `f1` instances, and `Image->Create Image`. The AMI will be created and ready for use shortly.