# Creating the cambridge-toolchain docker image #

We need an Ubuntu host for that. The easiest way is to use AWS. So spin up a strong instance with Ubuntu 18.04 (ami-0a634ae95e11c6f91) as the AMI. 

Note that I chose the AMD AMI, so if you use a different one, please change the docker installation instructions accordingly.

Also note that neither the FPGA CentOS AMI nor the Debian AWS instances have the UFS kernel module by default. 


```
cd ~
sudo modprobe ufs #If this doesn't work, don't bother with the rest. Find a machine that has this.
sudo apt update
sudo apt install -y git-all
sudo apt install -y git-lfs
sudo apt install -y awscli
git clone git@github.com:DARPA-SSITH-Demonstrators/SSITH-FETT-Target.git
cd SSITH-FETT-Target
git submodule update --init
cd SSITH-FETT-Binaries
git lfs pull
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo apt install -y zstd
```

If you're going to modify the Dockerfile or any other files, please make sure your commits are not anonymous
```
git config --global user.name <yourName>
git config --global user.email <yourEmail>
```

Now let's create the docker image:
```
cd ~/SSITH-FETT-Target/docker/cheri/
./copy-files.sh
sudo docker build --tag cambridge-toolchain .
```

Save it to a tar.gz file:
```
sudo docker save cambridge-toolchain | gzip > cambridge-toolchain.tar.gz
```

Delete the extra files:
```
./clear.sh
```