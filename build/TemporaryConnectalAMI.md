# Building Temporary Connectal AMI

## Overview

These instructions build out a FETT Target environment to run the connectal workflow. Currently, the AMI is a temporary environment to be used until the FETT Target AMI integrations exist for connectal. The setup is similar to the `FireSimAMI.md` instructions.

## Procedure

1. Base the image on `ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20200408 (ami-003634241a8fcdec0)`
   
2. Install AWS/AWS FPGA utilities

    ```
    sudo apt install awscli
    ```
    ```
    git clone https://github.com/aws/aws-fpga.git && cd ~/aws-fpga/
    . sdk_setup.sh
    ```

3. Install connectal drivers
    ```
    sudo add-apt-repository -y ppa:jamey-hicks/connectal
    sudo apt update
    sudo apt install connectal
    modprobe portalmem
    modprobe pcieportal
    ```

4. Install the Nix Package Manager.
    ```
    $ sh <(curl https://nixos.org/nix/install) --no-daemon
    ```

was used. 

5. Install git 2.x.x and git lfs. You can install git using whatever technique you want, but since nix was just installed, it can be done conveniently,
   ```
   $ nix-env -i git
   $ nix-env -i git-lfs
   ```

6. As FETT Environment is based on tool-suite, all of the relevant accesses need to be setup in order for the shell to function correctly. Provided that you have access to the correct repositories, it will help to setup SSH keys with [http://gitlab-ext.galois.com](https://docs.gitlab.com/ee/ssh/) and [www.github.com](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent). Also, tool-suite utilizes a binary cache that will need to be accessed. This is done by [following the tool-suite setup instructions](https://gitlab-ext.galois.com/ssith/tool-suite). The general steps are to create two files, a `nix.conf` configuration file and a `netrc` file with the relevant artifactory login credentials. 

**/home/ubuntu/.config/nix/nix.conf**

```
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= besspin.galois.com-1:8IqXQ2FM1J5CuPD+KN9KK4z6WHve4KF3d9zGRK+zsBw=
substituters = https://artifactory.galois.com/besspin_generic-nix/ https://cache.nixos.org/
netrc-file = /home/ubuntu/.config/nix/netrc
```
**/home/ubuntu/.config/netrc**

```
machine artifactory.galois.com
login <your username>
password <your password>
```

   For the permanent AMI, an account was created so the FETT Environment can be modified by the user and still interact with the artifactory resources. The user `besspin_fett` was added and a token key was registered. Also, for good practice,

```
$ chmod 600 /home/ubuntu/.config/nix/netrc
```

7. Clone the [FETT Target Repository](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Target). If `nix` has already been installed and you're modifying an existing AMI, it is a good idea to delete packages no longer used by the project, with
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

8. As was suggested in #323, the permissions can be changed for the amazon FPGA management tools to not require `sudo`. This can be done with
    ```
    sudo chmod u+s /usr/local/bin/fpga-*
    ```

9. Clear personal items and prepare image for AMI creation. 

   * remove git usernames if they are configured, clearing
     ```
     /home/ubuntu/.gitconfig
     ```

   * **IF NOT USING `besspin_fett`, delete the contents of `/home/ubuntu/.config/nix` as it contains your login credentials**

   * **delete/deactivate the SSH keys associated with your GitHub/GitLab accounts**

   * clear your command history
     ```
     $ rm ~/.bash_history
     $ history -c
     ```

10. Go to `Instances` in the EC2 dashboard. Select the `f1` instances, and `Image->Create Image`. The AMI will be created and ready for use shortly.
