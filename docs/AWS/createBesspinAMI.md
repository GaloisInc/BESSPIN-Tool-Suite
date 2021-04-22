# Building the BESSPIN AMI 

## Overview

This guide outlines how to modify a FPGA Developer AMI to run both BESSPIN, FireSim built FPGA tools and Connectal tools. This image is designed for BESSPIN development. The critical modifications are

* Update `git` so that the BESSPIN Environment can aquire its sources correctly
* Produce a BESSPIN Environment by populating packages in `nix/store`
* Setup the FPGA tools, and required kernel modules
* Configure device rules in `udev` to let connectal run as non-root
* Configure `rsyslog` for logging
* Put `BESSPIN-Tool-Suite` in the user's home directory
* Install AWS Cloudwatch

## Procedure

1. Launch a `f1.2xlarge` instance (or any other instance, we often use c4.4xlarge). Importantly, search for the AMI

   ```
   FPGA Developer AMI - 1.6.0-40257ab5-6688-4c95-97d1-e251a40fd1fc-ami-0b1edf08d56c2da5c.4 (ami-02b792770bf83b668)
   ```

   to acquire a FireSim compatible image. Follow the usual AWS procedure, selecting a VPC with a public subnet. Ideally, add protection from accidental termination. Increase the storage to \~150GB and remove the ephemeral storage drive. 

2. Install the Nix Package Manager. Use the following command, then logout and re-login.

   ```
   $ sudo curl -L https://nixos.org/nix/install | sh
   ```


3. Install git 2.x.x and git lfs. You can install git using whatever technique you want, but since nix was just installed, it can be done conveniently,

   ```
   $ nix-env -i git
   $ nix-env -i git-lfs
   ```

4. As BESSPIN Environment is based on tool-suite, all of the relevant accesses need to be setup in order for the shell to function correctly. Provided that you have access to the correct repositories, it will help to setup SSH keys with [http://gitlab-ext.galois.com](https://docs.gitlab.com/ee/ssh/) and [www.github.com](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent). Also, tool-suite utilizes a binary cache that will need to be accessed. This is done by [following the tool-suite setup instructions](https://gitlab-ext.galois.com/ssith/tool-suite). The general steps are to create two files, a `nix.conf` configuration file and a `netrc` file with the relevant artifactory login credentials.

   **/home/centos/.config/nix/nix.conf**

   ```
   trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= besspin.galois.com-1:8IqXQ2FM1J5CuPD+KN9KK4z6WHve4KF3d9zGRK+zsBw=
   substituters = https://artifactory.galois.com/besspin_generic-nix/ https://cache.nixos.org/
   netrc-file = /home/centos/.config/nix/netrc
   ```

   **/home/centos/.config/nix/netrc**

   ```
   machine artifactory.galois.com
   login <your username>
   password <your password>
   ```

   For the permanent AMI, an account was created so the BESSPIN Environment can be modified by the user and still interact with the artifactory resources. The user BESSPIN was added and a token key was registered. Also, for good practice,

   ```
   $ chmod 600 /home/centos/.config/nix/netrc
   ```

   After you do that, you have to logout and re-login.

5. Clone the [BESSPIN Repository](https://github.com/GaloisInc/BESSPIN-Tool-Suite). If `nix` has already been installed and you're modifying an existing AMI, it is a good idea to delete packages no longer used by the project, with

   ```
   $ nix-collect-garbage
   ```

   Initialize and update the submodules, running

   ```
   $ cd ~
   $ git clone git@github.com:GaloisInc/BESSPIN-Tool-Suite.git
   $ cd BESSPIN-Tool-Suite
   $ git submodule update --init
   $ cd BESSPIN-LFS
   $ git lfs pull
   $ cd ..
   $ nix-shell
   $ exit
   $ cd ~
   ```

   Nix will now perform the first time builds and installation of the BESSPIN Environment. This will take \~20 minutes. After the first time installation, subsequent re-runs will only take a few seconds. 

   For a machine that will checkout and pull different versions of `BESSPIN-Tool-Suite` (like one for CI or updating the AMI), you should stash the binary repo before updating it as a submodule and pulling. So for update, do the following
   ```
   $ cd ~/BESSPIN-Tool-Suite/BESSPIN-LFS
   $ git stash
   $ cd ..
   $ git submodule update
   $ cd BESSPIN-LFS
   $ git lfs pull
   ```

6. Install FPGA SDK tools.

  ```
  $ cd ~
  $ git clone https://github.com/aws/aws-fpga
  $ cd aws-fpga
  $ git checkout 6c707ab4a26c2766b916dad9d40727266fa0e4ef
  $ source sdk_setup.sh
  $ cd ..
  $ rm -rf aws-fpga
  ```

As was suggested in #323, the permissions can be changed for the amazon FPGA management tools to not require `sudo`. This can be done with
   
   ```
      $ sudo chmod u+s /usr/bin/fpga-*
   ```

7. For use of connectal, modify the device rules so that nodes are accessible by non-root users. Create the file as root,

   **/etc/udev/rules.d/99-pcieportal.rules**

   ```
   # UDev rules for setting up Bluespec emulation device drivers

   ACTION=="add",SUBSYSTEM=="pci",ATTR{vendor}=="0x1be7", ATTR{device}="0xb100", RUN+="/sbin/modprobe -ba pcieportal portalmem"
   KERNEL=="portal*",MODE="666"
   KERNEL=="xdma*",MODE="666"
   KERNEL=="portalmem",MODE="666"
   KERNEL=="connectal",MODE="666"

   ```

8. Update `rsyslog.conf`. 

   1. Inside the file,

      **/etc/rsyslog.conf**

      ```
      # Provides UDP syslog reception
      #$ModLoad imudp.so
      #$UDPServerRun 514
      ```

      Change to

      ```
      # Provides UDP syslog reception
      $ModLoad imudp.so
      $UDPServerRun 514
      
      $template RemoteLogs,"/var/log/%FROMHOST-IP%/%PROGRAMNAME%.log"
      *.* ?RemoteLogs
      ```

   2. Enable the service by running,

      ```
      $ sudo service rsyslog restart
      ```

9. Install cloudwatch

   1. Download and install the cloudwatch rpm

      ```
      $ wget https://s3.amazonaws.com/amazoncloudwatch-agent/centos/amd64/latest/amazon-cloudwatch-agent.rpm
      $ sudo rpm -U ./amazon-cloudwatch-agent.rpm
      ```

   2. Make the file

      **/opt/aws/amazon-cloudwatch-agent/bin/config.json**

      ```json
      {
          "agent": {
              "metrics_collection_interval": 60,
              "run_as_user": "root"
          },
          "logs": {
              "logs_collected": {
                  "files": {
                      "collect_list": [
                          {
                              "file_path": "/var/log/172.0.16.2/**",
                              "log_group_name": "BESSPIN-172-syslogs",
                              "log_stream_name": "{instance_id}"
                          },
                          {
                              "file_path": "/var/log/user-data.log",
                              "log_group_name": "user-data.log",
                              "log_stream_name": "{instance_id}"
                          },
                          {
                              "file_path": "/var/log/cloud-init.log",
                              "log_group_name": "cloud-init.log",
                              "log_stream_name": "{instance_id}"
                          },
                          {
                              "file_path": "/home/centos/BESSPIN-Tool-Suite/workDir/besspin.log",
                              "log_group_name": "besspin.log",
                              "log_stream_name": "{instance_id}"
                          },
                          {
                              "file_path": "/home/centos/BESSPIN-Tool-Suite/workDir/shell.out",
                              "log_group_name": "shell.out",
                              "log_stream_name": "{instance_id}"

                          },
                          {
                              "file_path": "/home/centos/BESSPIN-Tool-Suite/workDir/tty.out",
                              "log_group_name": "tty.out",
                              "log_stream_name": "{instance_id}"
                          }
                      ]
                  }
              }
          },
          "metrics": {
              "append_dimensions": {
                  "AutoScalingGroupName": "${aws:AutoScalingGroupName}",
                  "ImageId": "${aws:ImageId}",
                  "InstanceId": "${aws:InstanceId}",
                  "InstanceType": "${aws:InstanceType}"
              },
              "metrics_collected": {
                  "cpu": {
                      "measurement": [
                          "cpu_usage_idle",
                          "cpu_usage_iowait",
                          "cpu_usage_user",
                          "cpu_usage_system"
                      ],
                      "metrics_collection_interval": 60,
                      "resources": [
                          "*"
                      ],
                      "totalcpu": false
                  },
                  "disk": {
                      "measurement": [
                          "used_percent",
                          "inodes_free"
                      ],
                      "metrics_collection_interval": 60,
                      "resources": [
                          "*"
                      ]
                  },
                  "diskio": {
                      "measurement": [
                          "io_time",
                          "write_bytes",
                          "read_bytes",
                          "writes",
                          "reads"
                      ],
                      "metrics_collection_interval": 60,
                      "resources": [
                          "*"
                      ]
                  },
                  "mem": {
                      "measurement": [
                          "mem_used_percent"
                      ],
                      "metrics_collection_interval": 60
                  },
                  "netstat": {
                      "measurement": [
                          "tcp_established",
                          "tcp_time_wait"
                      ],
                      "metrics_collection_interval": 60
                  },
                  "statsd": {
                      "metrics_aggregation_interval": 60,
                      "metrics_collection_interval": 10,
                      "service_address": ":8125"
                  },
                  "swap": {
                      "measurement": [
                          "swap_used_percent"
                      ],
                      "metrics_collection_interval": 60
                  }
              }
          }
      }
      ```

   3. For the startup script, run

      ```
      $ sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
      ```

12. In `/etc/pam.d/system-auth`, comment out this line:
```
-session     optional      pam_systemd.so
```
This causes the polling timeout on a system bus socket when using sudo with cloud-hook. More info can be found [here](https://bugs.launchpad.net/tripleo/+bug/1819461).

13. Install `python3` for the private binaries download:
```bash
  sudo yum install -y python3
```

14. Clear personal items and prepare image for AMI creation. 

    * remove git usernames if they are configured, clearing

    ```
    /home/centos/.gitconfig
    ```

    * **IF NOT USING BESSPIN, delete the contents of `/home/centos/.config/nix` as it contains your login credentials**

    * **delete/deactivate the SSH keys associated with your GitHub/GitLab accounts**

    ```
    rm ~/.ssh/*
    ```

    * clear your command history

    ```
    $ rm ~/.bash_history
    $ history -c
    ```
    * delete folders in `/home/centos/` that aren't the repository `BESSPIN-Tool-Suite`

    Also, you may run `history -c` inside `nix-shell`.

15. Go to `Instances` in the EC2 dashboard. Select your instance, and stop it and wait for it to shutdown. Then, `Image->Create Image`. The AMI will be created and ready for use shortly.

16. Go to `AMIs` in the EC2 dashboard. Select the new AMI and `Modify Image Permissions`. Add the production accounts to the AMI permissions. 

17. Copy the AMI to North Virginia, then add the production account to the permissions of the N. Virginia version too.

